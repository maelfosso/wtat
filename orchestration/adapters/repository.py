import os
from ..config import settings

class Repository:
    def __init__(self, conn):
        self.conn = conn

    # -- RAW
    def ingest_page(self, page_id: int) -> int:
        page_dir = settings.raw_root / str(page_id)
        if not page_dir.exists():
            return 0
        disk_files = {f for f in os.listdir(page_dir) if f.endswith(".json")}
        new_files = disk_files - self.known_bronze_files(page_id)
        if not new_files:
            return 0
        paths = [f"{page_dir}/{f}" for f in new_files]
        self.insert_bronze(paths, page_id)
        return len(new_files)

    def ingest_all_pages(self) -> dict[int, int]:
        pages = [int(d.name) for d in settings.raw_root.iterdir() if d.is_dir()]
        return {pid: self.ingest_page(pid) for pid in pages}

    # ── BRONZE ──────────────────────────────────────────────
    def ensure_bronze_schema(self) -> None:
        self.conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bronze.posts (
                post_id BIGINT PRIMARY KEY, page_id BIGINT NOT NULL,
                url VARCHAR, message VARCHAR NOT NULL,
                post_timestamp TIMESTAMPTZ NOT NULL,
                author_id BIGINT, author_name VARCHAR,
                reactions_count INTEGER, comments_count INTEGER,
                reshare_count INTEGER, source_file VARCHAR NOT NULL
            )
        """)

    def known_bronze_files(self, page_id: int) -> set[str]:
        rows = self.conn.execute(
            "SELECT source_file FROM bronze.posts WHERE page_id = ?", [page_id]
        ).fetchall()
        return {r[0] for r in rows}

    def insert_bronze(self, files: list[str], page_id: int) -> None:
        self.conn.execute("""
            INSERT INTO bronze.posts BY NAME
            SELECT post_id, ? AS page_id, url, message,
                   to_timestamp(timestamp) AS post_timestamp,
                   author.id AS author_id, author.name AS author_name,
                   reactions_count, comments_count, reshare_count,
                   filename AS source_file
            FROM read_json_auto(?, filename=true, union_by_name=true)
            WHERE regexp_matches(message, 'RECHERCHE NDOLO 100% KMER DU TERRE|RECHERCHE NDOLO 100% KMER|Chaque Dimanche Matin')
            ON CONFLICT (post_id) DO NOTHING
        """, [page_id, files])

    # ── SILVER ──────────────────────────────────────────────
    def ensure_silver_schema(self) -> None:
        self.conn.execute("CREATE SCHEMA IF NOT EXISTS silver")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.posts (
                post_id BIGINT PRIMARY KEY, page_id BIGINT NOT NULL,
                url VARCHAR NOT NULL, message VARCHAR NOT NULL,
                post_timestamp TIMESTAMPTZ NOT NULL, post_type VARCHAR NOT NULL,
                author_id BIGINT NOT NULL, author_name VARCHAR NOT NULL,
                reactions_count INTEGER NOT NULL, comments_count INTEGER NOT NULL,
                reshare_count INTEGER NOT NULL, source_file VARCHAR NOT NULL
            )
        """)

        # Table ADS : le découpage. Peut être régénérée sans dommage.
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.ads (
                ad_id VARCHAR PRIMARY KEY,      -- hash(post_id, ad_text)
                ad VARCHAR NOT NULL,
                post_id BIGINT NOT NULL,
                post_type VARCHAR NOT NULL
            )
        """)
        # Table EXTRACTION : l'état LLM. JAMAIS écrasée.
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.ads_extraction (
                ad_id VARCHAR PRIMARY KEY,
                extraction_status VARCHAR DEFAULT 'NOT STARTED'
                    CHECK (extraction_status IN ('NOT STARTED','PENDING','SUCCESS','FAILURE')),
                profile JSON,
                extraction_time DOUBLE,
                extracted_at TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS silver.ads_errors (
                post_id BIGINT, error VARCHAR, post_preview VARCHAR,
                created_at TIMESTAMP DEFAULT current_timestamp
            )
        """)

    def promote_to_silver(self) -> int:
        """Bronze → silver, type reconstruit, anti-join. Retourne le nb inséré."""
        before = self.conn.execute("SELECT count(*) FROM silver.posts").fetchone()[0]
        self.conn.execute("""
            INSERT INTO silver.posts BY NAME
            SELECT b.post_id, b.page_id, b.url, b.message, b.post_timestamp,
                   CASE WHEN regexp_matches(lower(b.message), 'chaque dimanche')
                        THEN 'Dimanche' ELSE 'Special' END AS post_type,
                   b.author_id, b.author_name, b.reactions_count,
                   b.comments_count, b.reshare_count, b.source_file
            FROM bronze.posts b
            ANTI JOIN silver.posts s ON b.post_id = s.post_id
            ON CONFLICT (post_id) DO NOTHING
        """)
        after = self.conn.execute("SELECT count(*) FROM silver.posts").fetchone()[0]
        return after - before

    def posts_for_split(self) -> "pd.DataFrame":
        return self.conn.execute("""
            SELECT post_id, message, post_type
            FROM silver.posts s
            ANTI JOIN silver.ads a ON s.post_id = a.post_id 
        """).fetch_df()

    def insert_ads(self, ads_df) -> int:
        """Insère les annonces splittées. ON CONFLICT = idempotent, préserve l'existant."""
        if ads_df.empty:
            return 0
        before = self.conn.execute("SELECT count(*) FROM silver.ads").fetchone()[0]
        # ad_id stable = hash(post_id, ad). Jamais ROW_NUMBER.
        self.conn.execute("""
            INSERT INTO silver.ads (ad_id, ad, post_id, post_type)
            SELECT md5(post_id::VARCHAR || '|' || ad), ad, post_id, post_type
            FROM ads_df
            ON CONFLICT (ad_id) DO NOTHING
        """)
        # Amorce l'état d'extraction pour les nouvelles annonces uniquement
        self.conn.execute("""
            INSERT INTO silver.ads_extraction (ad_id)
            SELECT ad_id FROM silver.ads
            ANTI JOIN silver.ads_extraction USING (ad_id)
        """)
        after = self.conn.execute("SELECT count(*) FROM silver.ads").fetchone()[0]
        return after - before

    def insert_ad_errors(self, errors_df) -> None:
        if not errors_df.empty:
            self.conn.execute(
                "INSERT INTO silver.ads_errors(post_id, error, post_preview) "
                "SELECT post_id, error, post_preview FROM errors_df"
            )

    def fetch_ads_to_process(self) -> "pd.DataFrame":
        return self.conn.execute("""
            SELECT a.ad_id, a.ad, a.post_type
            FROM silver.ads a
            JOIN silver.ads_extraction e USING (ad_id)
            WHERE e.extraction_status != 'SUCCESS'
        """).fetch_df()

    def ad_extraction_started(self, ad_id):
        self.conn.execute(
          "UPDATE ads SET extraction_status = 'PENDING' WHERE id = ?",
          [ad_id]
        )

    def ad_extraction_success(self, ad_id, profiles, dt):
        self.conn.execute("""
            UPDATE silver.ads_extraction
            SET extraction_status="SUCCESS", profile=?, extraction_time=?, extracted_at=now()
            WHERE ad_id=?
        """, [profiles.model_dump_json(), dt, ad_id])

    def ad_extraction_failed(self, ad_id, profiles, dt):
        self.conn.execute("""
            UPDATE silver.ads_extraction
            SET extraction_status="FAILURE", extraction_time=?
            WHERE ad_id=?
        """, [dt, ad_id])
    
    # ── silver : split (recalculable) ────────────────────────
    def ensure_gold_schema(self) -> None:
        self.conn.execute("CREATE SCHEMA IF NOT EXISTS gold")
        