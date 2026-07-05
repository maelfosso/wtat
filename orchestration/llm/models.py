"""
Modèles Pydantic — extraction des profils d'annonces matrimoniales (WTAT).

═══════════════════════════════════════════════════════════════════════════
DOCTRINE (ne pas la perdre en éditant)
═══════════════════════════════════════════════════════════════════════════
1. DEUX gestes, jamais confondus :
   - EXTRAIRE le texte BRUT, fidèle (aucune normalisation de forme) -> str + raw.
   - CLASSER le SENS dans une modalité fermée                        -> Enum via Categorized.
   La normalisation de forme (1m70->1.70) est faite par le cleaning Python, plus tard.

2. DEUX natures de champ :
   - ANALYTIQUE (GROUP BY)  -> Categorized[Enum] { raw, value }.
   - DESCRIPTIF (infini)    -> list[str] nue (destiné lecture/embedding).

3. SYMÉTRIE PAR DÉFAUT : un attribut vit des DEUX côtés (seeker ET sought),
   sauf impossibilité structurelle (age vs age_min/max ; récit de soi).
   On ne présume pas qui déclare quoi — l'analyse le révélera.

4. GÉOGRAPHIE HIÉRARCHIQUE (city->region->country->continent), jamais plate.

5. RIEN N'EST EXCLU. Les champs rares (<10%) sont conservés mais ANNOTÉS
   [NARRATIF] : ils servent à citer des cas, pas à agréger. Les taux entre
   crochets viennent d'un échantillon réel de 200 annonces (page Warman).
   Données actuelles jusqu'au 01/04/2023 — le corpus grandira, les rares
   peuvent monter.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from enum import Enum
from typing import Generic, TypeVar
from pydantic import BaseModel, Field


# ═════════════════════════════════════════════════════════════
# Patron générique raw + value
# ═════════════════════════════════════════════════════════════
E = TypeVar("E", bound=Enum)


class Categorized(BaseModel, Generic[E]):
    """Sens classé (value) + texte source préservé (raw). value=None si inclassable."""
    raw: str | None = None
    value: E | None = None


# ═════════════════════════════════════════════════════════════
# Énumérations — modalités fermées
# ═════════════════════════════════════════════════════════════
class Sex(str, Enum):
    HOMME = "Homme"
    FEMME = "Femme"


class Ternary(str, Enum):
    OUI = "Oui"
    NON = "Non"


class MaritalStatus(str, Enum):
    CELIBATAIRE = "célibataire"
    DIVORCE = "divorcé"
    VEUF = "veuf"
    SEPARE = "séparé"              # "terminé avec sa précédente relation"
    NON_ENGAGE = "non_engagé"
    NON_PRECISE = "non_précisé"


class OccupationType(str, Enum):          # [77%] pilier
    METIER_QUALIFIE = "métier_qualifié"   # ingénieur, analyste, infirmière
    SECTEUR = "secteur"                    # "la tech", "banque assurance"
    STATUT_SEUL = "statut_seul"            # "travail stable", sans métier
    TYPE_EMPLOYEUR = "type_employeur"      # "multinationale", "fonction publique"
    ETUDIANT = "étudiant"                  # en cursus (aussi capté par life_stage)
    SANS_EMPLOI = "sans_emploi"            # "sans qualification", "je cherche du travail"
    NON_PRECISE = "non_précisé"


class FinancialStability(str, Enum):      # [55%] pilier
    TRES_CONFORTABLE = "très_confortable"  # "financièrement très stable", "à l'aise"
    STABLE = "stable"                      # "stabilité financière"
    MODESTE = "modeste"                    # "je gagne ma vie sans plus"
    PRECAIRE = "précaire"                  # "financièrement pas stable", "je galère"
    NON_PRECISE = "non_précisé"


class MentalState(str, Enum):             # [25%] déclaré des deux côtés
    STABLE = "stable"                      # "psychologiquement/émotionnellement stable"
    FRAGILE = "fragile"                    # "je me reconstruis encore"
    NON_PRECISE = "non_précisé"


class HealingStatus(str, Enum):           # [8.5%] NARRATIF — seeker only
    RECONSTRUIT = "reconstruit"            # "guéri", "prêt", "reconstruit"
    EN_GUERISON = "en_guérison"            # processus en cours
    RUPTURE_RECENTE = "rupture_récente"    # "je sors à peine de"
    NON_PRECISE = "non_précisé"


class EducationLevel(str, Enum):          # [15%]
    UNIVERSITAIRE = "universitaire"        # licence, master, bac+, diplômé sup
    SECONDAIRE = "secondaire"
    PROFESSIONNEL = "professionnel"        # formation, technique
    NON_PRECISE = "non_précisé"


class ReligiosityLevel(str, Enum):        # [26%] religion présente
    PRATIQUANT = "pratiquant"              # "craint Dieu", "biblique", "prière", "chrétien pratiquant"
    CROYANT = "croyant"                    # appartenance sans pratique déclarée
    NON_PRECISE = "non_précisé"


class SkinTone(str, Enum):                # [27%] dimension sensible mais massive
    CLAIR = "clair"                        # "teint clair", "peau claire", "métis(se)"
    FONCE = "foncé"                        # "peau noire", "teint foncé"
    NON_PRECISE = "non_précisé"


class BuildType(str, Enum):               # [58%] corpulence
    MINCE = "mince"                        # "fine", "mince", "élancée"
    NORMALE = "normale"                    # "corpulence/morphologie normale", "équilibrée"
    RONDE = "ronde"                        # "ronde", "formes", "courbes harmonieuses"
    ATHLETIQUE = "athlétique"
    NON_PRECISE = "non_précisé"


class HeightQualitative(str, Enum):       # [54%] taille qualitative
    GRAND = "grand"                        # "grand", "grande taille"
    MOYEN = "moyen"
    PETIT = "petit"
    NON_PRECISE = "non_précisé"


class SmokingAlcohol(str, Enum):          # [4.5%] NARRATIF
    ABSTINENT = "abstinent"                # "ne fume pas", "sans vices", "ne boit pas"
    CONSOMMATEUR = "consommateur"
    NON_PRECISE = "non_précisé"


class ResidencyRequirement(str, Enum):    # marqueur diaspora
    REQUISE = "régularité_requise"         # "situation régulière", "papiers", "séjour stable"
    NON_MENTIONNEE = "non_mentionnée"


class PolygamyStance(str, Enum):          # [1%] NARRATIF — symétrique
    POUR = "pour"
    CONTRE = "contre"
    NON_PRECISE = "non_précisé"


class Virginity(str, Enum):               # [3.5%] NARRATIF — symétrique
    VIERGE = "vierge"                      # déclare/exige la virginité
    NON_VIERGE = "non_vierge"
    NON_PRECISE = "non_précisé"


class RelationshipGoal(str, Enum):        # [53%] pilier
    MARIAGE = "mariage"                    # "en vue du mariage", "épouse", "alliance sacrée", "foyer"
    RELATION_SERIEUSE = "relation_sérieuse"  # "relation stable et durable" sans "mariage"
    NON_PRECISE = "non_précisé"


class LifeStage(str, Enum):               # statut de vie (distinct de l'occupation)
    ETUDIANT = "étudiant"
    EN_ACTIVITE = "en_activité"
    RETRAITE = "retraité"
    NON_PRECISE = "non_précisé"


class HealthStatus(str, Enum):            # [~25%, à confirmer — faux positifs "santé"]
    BONNE_SANTE = "bonne_santé"            # "en bonne santé", "sans maladie"
    HANDICAP_MALADIE = "handicap_maladie"  # mention explicite d'un handicap/maladie
    NON_PRECISE = "non_précisé"


class SourceType(str, Enum):              # niveau ANNONCE, pas profil
    DIRECT = "direct"                      # annonceur donne son propre contact (Warman)
    AGENCY = "agency"                      # intermédiaire/cabinet (Cheldim)
    NON_PRECISE = "non_précisé"


class GeoScope(str, Enum):
    CITY = "city"
    REGION = "region"
    COUNTRY = "country"
    CONTINENT = "continent"


# ═════════════════════════════════════════════════════════════
# Géographie
# ═════════════════════════════════════════════════════════════
class Location(BaseModel):
    """Lieu en strates. Complète les niveaux SUPÉRIEURS déductibles
    (Douala->Cameroun->Afrique), jamais un inférieur inventé."""
    raw: str
    city: str | None = None
    region: str | None = None
    country: str | None = None
    continent: str | None = None


class LocationPreference(BaseModel):
    """Zone acceptée pour le partenaire. accepted_zones ORDONNÉE :
    première=préférée, suivantes=replis."""
    raw: str
    same_as_seeker: bool = False           # "près de moi", même zone que l'annonceur
    scope: GeoScope | None = None
    accepted_zones: list[Location] = Field(default_factory=list)


# ═════════════════════════════════════════════════════════════
# Contact — [100%] clé de déduplication.
# ATTENTION : ignorer le numéro de l'ADMIN/AGENCE de la page (99% des annonces
# Warman portent le numéro admin en pied). Ne capter que le contact PERSONNEL.
# ═════════════════════════════════════════════════════════════
class Contact(BaseModel):
    email: str | None = None
    whatsapp: str | None = None
    phone: str | None = None
    is_agency_contact: bool = Field(
        default=False,
        description="True si le seul contact est celui de l'agence/admin, pas de l'annonceur",
    )


# ═════════════════════════════════════════════════════════════
# CHERCHEUR — personne réelle
# ═════════════════════════════════════════════════════════════
class Seeker(BaseModel):
    # — identité —
    name: str | None = None
    sex: Sex | None = None
    age: str | None = None                 # BRUT ("36 ans", "bientôt 30ans")

    # — physique (BRUT pour les mesures, catégorisé pour le qualitatif) —
    height: str | None = None              # BRUT ("1m82", "1,79")
    height_qualitative: Categorized[HeightQualitative] = Field(default_factory=Categorized)  # [54%]
    weight: str | None = None              # BRUT ("85kg")
    build: Categorized[BuildType] = Field(default_factory=Categorized)                        # [58%]
    skin_tone: Categorized[SkinTone] = Field(default_factory=Categorized)                     # [27%]
    physical_appearance: list[str] = Field(default_factory=list)                              # [44%] libre

    # — géo & origine —
    residence: Location | None = None
    origin: Location | None = None
    ethnicity: str | None = None           # [43%] "Bamiléké", "de l'Ouest", "kmr"
    nationality: str | None = None         # [100%] "camerounais(e)" — quasi constant
    language: str | None = None

    # — foi —
    religion: str | None = None            # [26%] "chrétien", "catholique"
    religiosity: Categorized[ReligiosityLevel] = Field(default_factory=Categorized)

    # — vie professionnelle & matérielle —
    occupation: Categorized[OccupationType] = Field(default_factory=Categorized)  # [77%]
    life_stage: Categorized[LifeStage] = Field(default_factory=Categorized)
    education: Categorized[EducationLevel] = Field(default_factory=Categorized)   # [15%]
    financial: Categorized[FinancialStability] = Field(default_factory=Categorized)  # [55%]

    # — situation familiale —
    marital_status: Categorized[MaritalStatus] = Field(default_factory=Categorized)
    has_children: Ternary | None = None    # [87%] en a-t-il DÉJÀ
    number_of_children: str | None = None  # BRUT ("1", "00", "père d'un enfant de 6 ans")
    children_desire: Ternary | None = None # veut-il EN AVOIR (projet)
    family_orientation: Ternary | None = None  # [65%] "orienté famille", "valeurs familiales", prend soin des proches

    # — psychologie (récit de soi, asymétrique) —
    mental_state: Categorized[MentalState] = Field(default_factory=Categorized)   # [25%]
    past_relationship: Ternary | None = None                                      # [8.5%] NARRATIF
    past_relationship_detail: str | None = None   # BRUT ("relation de 7 ans", "il y a 2 ans")
    healing_status: Categorized[HealingStatus] = Field(default_factory=Categorized)  # NARRATIF

    # — santé & mœurs —
    health: Categorized[HealthStatus] = Field(default_factory=Categorized)
    smoking_alcohol: Categorized[SmokingAlcohol] = Field(default_factory=Categorized)  # [4.5%] NARRATIF

    # — mœurs culturelles (NARRATIF mais capté volontairement) —
    virginity: Categorized[Virginity] = Field(default_factory=Categorized)        # [3.5%]
    polygamy: Categorized[PolygamyStance] = Field(default_factory=Categorized)     # [1%]

    # — intention & personnalité —
    relationship_goal: Categorized[RelationshipGoal] = Field(default_factory=Categorized)  # [53%]
    qualities: list[str] = Field(default_factory=list)   # [90%] libre -> embedding
    values: list[str] = Field(default_factory=list)
    defects: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)   # [58%] libre

    # — contact —
    contact: Contact = Field(default_factory=Contact)


# ═════════════════════════════════════════════════════════════
# RECHERCHÉ — ensemble de CRITÈRES
# ═════════════════════════════════════════════════════════════
class Sought(BaseModel):
    sex: Sex | None = None
    age_min: int | None = None             # "entre 26 et 34" -> 26
    age_max: int | None = None             # "35 ans maximum" -> 35

    # — physique recherché —
    height_min: str | None = None          # BRUT ("1.72 et plus")
    height_qualitative: Categorized[HeightQualitative] = Field(default_factory=Categorized)  # "grand"
    build: Categorized[BuildType] = Field(default_factory=Categorized)            # "pas en surpoids"
    skin_tone: Categorized[SkinTone] = Field(default_factory=Categorized)         # teint recherché
    physical_appearance: list[str] = Field(default_factory=list)                  # "jolie", "présentable"

    # — géo —
    location_preference: LocationPreference | None = None
    ethnicity: str | None = None           # "une femme kmr"
    language: str | None = None

    # — foi —
    religion: str | None = None
    religiosity: Categorized[ReligiosityLevel] = Field(default_factory=Categorized)

    # — vie pro & matérielle recherchée —
    occupation: Categorized[OccupationType] = Field(default_factory=Categorized)
    life_stage: Categorized[LifeStage] = Field(default_factory=Categorized)
    education: Categorized[EducationLevel] = Field(default_factory=Categorized)   # "niveau universitaire"
    financial: Categorized[FinancialStability] = Field(default_factory=Categorized)  # "financièrement stable"
    residency: Categorized[ResidencyRequirement] = Field(default_factory=Categorized)  # séjour régulier

    # — situation familiale recherchée —
    marital_status: Categorized[MaritalStatus] = Field(default_factory=Categorized)
    has_children: Ternary | None = None
    max_children: str | None = None        # BRUT ("un enfant maximum", "sans enfant ou un au trop")
    children_desire: Ternary | None = None
    family_orientation: Ternary | None = None

    # — psychologie recherchée (symétrique ici : on cherche la stabilité) —
    mental_state: Categorized[MentalState] = Field(default_factory=Categorized)   # "psychologiquement stable"

    # — santé & mœurs —
    health: Categorized[HealthStatus] = Field(default_factory=Categorized)
    smoking_alcohol: Categorized[SmokingAlcohol] = Field(default_factory=Categorized)
    virginity: Categorized[Virginity] = Field(default_factory=Categorized)        # exige la virginité
    polygamy: Categorized[PolygamyStance] = Field(default_factory=Categorized)     # refuse/exige polygamie

    # — intention & personnalité recherchées —
    relationship_goal: Categorized[RelationshipGoal] = Field(default_factory=Categorized)
    qualities: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)

    # — le NÉGATIF : qui est rejeté [25%] —
    exclusions: list[str] = Field(
        default_factory=list,
        description="Clauses d'exclusion : qui l'annonceur REFUSE. "
                    "'égoïstes s'abstenir', 'pas d'intéressées par l'argent'",
    )

    # — divers —
    urgency: str | None = None             # "prêt rapidement", "mariage dans l'année"
    photo_requested: bool = False          # [64%] demande une/des photo(s)
    relationship_summary: list[str] = Field(default_factory=list)


# ═════════════════════════════════════════════════════════════
# Contrat de sortie
# ═════════════════════════════════════════════════════════════
class DualProfiles(BaseModel):
    """Une annonce -> chercheur + critères + provenance.

    source_type / agency_name sont au niveau ANNONCE (provenance), pas du profil.
    Si l'annonce ne détaille aucun critère, `sought` reste par défaut
    (sexe recherché souvent déductible).
    """
    seeker: Seeker
    sought: Sought
    source_type: SourceType | None = None
    agency_name: str | None = None         # "Cheldim", "Warman" sinon None
