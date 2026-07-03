# --- Étape de compilation ---
FROM rust:1.85.0-bookworm AS builder

WORKDIR /usr/src/app
COPY . .

# On compile en mode release pour les performances
RUN cargo build --release

# --- Étape d'exécution ---
FROM debian:bookworm-slim

# Installation des certificats SSL (indispensable pour les requêtes HTTPS vers RapidAPI)
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# On récupère uniquement le binaire compilé
COPY --from=builder /usr/src/app/target/release/wtat-ingestion /app/wtat-ingestion

# On s'assure que le dossier de données existe
RUN mkdir -p /app/data/raw

# Commande de lancement
CMD ["./wtat-ingestion"]
