PROMPT_TEMPLATE = """
Tu es un expert en extraction de données de petites annonces matrimoniales camerounaises et diaspora.
Extrait TOUS les champs ci-dessous avec précision. Si une information n'est pas présente, mets null.

FORMAT DE SORTIE STRICT (JSON valide) :
{
  "NAME": "Prénom ou pseudo ou null",
  "RELIGION": "Religion ou null",
  "AGE": "Âge exact avec unité ou null",
  "SEX": "'Homme' ou 'Femme'",
  "HEIGHT": "Taille normalisée 'X.XX m' ou null",
  "WEIGHT": "Poids normalisé 'XX kg' ou null",
  "PRIMARY_COUNTRY_OF_RESIDENCE": "Pays de résidence PRINCIPAL (ex: 'France')",
  "OTHER_LOCATIONS_MENTIONED": ["Villes/régions spécifiques"],
  "COUNTRY_OF_ORIGIN": "Pays d'origine EXPLICITE ou null",
  "SECTOR_OF_ACTIVITY": "Profession ou null",
  "MARITAL_STATUS": "Statut marital ou null",
  "HAS_CHILDREN": "'Oui' ou 'Non'",
  "NUMBER_OF_CHILDREN": "Nombre EXACT en chiffre (ex: '0', '1', '3')",
  "QUALITIES": ["Qualités explicites"],
  "VALUES": ["Valeurs"],
  "DEFECTS": ["Défauts mentionnés ou []"],
  "INTERESTS": ["Centres d'intérêt ou []"],
  "PHYSICAL_APPEARANCE": ["Description physique SAUF taille/poids"],
  "ECONOMIC_SITUATION": ["Situation économique ou []"],
  "EDUCATION_LEVEL": ["Niveau d'études ou []"],
  "ILLNESS": ["Maladies ou []"],
  "RELATIONSHIP": ["Critères pour partenaire — RÉSUMER en phrases courtes"]
}

RÈGLES ABSOLUES :
1. CONVERTIR : "00" → "0", "un" → "1", "trois" → "3"
2. DISTINGUER :
   - Résidence = pays seulement (ex: "France")
   - Origine = pays EXPLICITE seulement (ex: "Cameroun")
   - Régions ("Ouest", "Sud") → ONLY dans OTHER_LOCATIONS_MENTIONED
3. POUR RELATIONSHIP : résumer paragraphes longs en 3-5 phrases courtes
4. NE JAMAIS INFÉRER : pas de religion mentionnée → null
5. SEXE IMPLICITE : "camerounaise" → "Femme", "homme" → "Homme"

EXEMPLES RÉELS SANS MODIFICATION :

Exemple 1 (annonce originale) :
Texte: "RESSE 4
Jeune femme de 42 ans basée en Allemagne, 1m64 pour 65 kg, maman de 3 adorables bambins, je recherche un partenaire de vie âgé entre 45 et 50 ans qui est déjà papa et ne souhaite plus d'enfants. Il devra être honnête, travailleur, fidèle, attentionné et drôle. Ensemble on veillera sur notre progéniture. Mon entourage me décrit comme humble, honnête, maternelle et la liste est non exhaustive. Si tu souhaites qu'on écrive notre histoire, rejoins moi promptement à sylviascott2004@gmail.com"

JSON attendu:
{
  "NAME": null,
  "RELIGION": null,
  "AGE": "42 ans",
  "SEX": "Femme",
  "HEIGHT": "1.64 m",
  "WEIGHT": "65 kg",
  "PRIMARY_COUNTRY_OF_RESIDENCE": "Allemagne",
  "OTHER_LOCATIONS_MENTIONED": [],
  "COUNTRY_OF_ORIGIN": null,
  "SECTOR_OF_ACTIVITY": null,
  "MARITAL_STATUS": null,
  "HAS_CHILDREN": "Oui",
  "NUMBER_OF_CHILDREN": "3",
  "QUALITIES": ["humble", "honnête", "maternelle"],
  "VALUES": ["famille"],
  "DEFECTS": [],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": [],
  "ECONOMIC_SITUATION": [],
  "EDUCATION_LEVEL": [],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "45-50 ans",
    "déjà papa",
    "ne souhaite plus d'enfants",
    "doit être honnête, travailleur, fidèle, attentionné et drôle"
  ]
}

Exemple 2 (annonce Cheldim structurée) :
Texte: "𝙍𝒆𝒏𝒄𝒐𝒏𝒕𝒓𝒆 𝙎𝒆́𝙧𝒊𝙚𝙪𝙨𝙚, 𝙋𝒓𝙤𝒇𝙞𝙡 𝑽𝙚́𝒓𝙞𝒇𝙞𝒆́,
𝐶𝘩𝑒𝘭𝑑𝘪𝑚 𝐴𝑔𝑒𝘯𝘤𝑒 𝘔𝘢𝘵𝘳𝘪𝘮𝘰𝘯𝘪𝘢𝘭𝘦 237
Âge : 40 ans
Situation familiale : 1 enfant
Métier : Ingénieur
Lieu de résidence : France
Taille : 1m75
Homme de 40ans, résidant en France, Je suis une personne simple, posée et claire dans mes intentions. Je sais ce que je veux et je sais *surtout ce que je ne veux pas*, donc je  m'inscris dans une démarche sérieuse.
J'accorde une grande importance à la stabilité, au respect, à la communication et à la sincérité. Pour moi, une relation durable se construit sur des bases solides, une vision commune et une volonté réelle de s'engager.
👩‍🦰 La femme que je souhaite rencontrer
Je recherche une femme :
âgée de 40 ans maximum,
résidant en Europe ou Afrique
qui se sent belle et féminine,
Propre, douce, respectueuse et équilibrée,
ambitieuse, avec des objectifs clairs, de corpulence mince ou moyenne avec des formes africaines, naturelles et assumées.
💞 Ce que je peux offrir
Je suis un homme capable d'apporter :
une présence stable et rassurante,
du respect, de la loyauté et de la considération,
un cadre de relation sain et structuré,
une relation fondée sur la communication, la compréhension et l'engagement.
🎯 Objectif : construire une relation sérieuse, saine et durable, basée sur le respect mutuel, la stabilité émotionnelle et une volonté commune d'avancer ensemble.
Si interessé m'écrire à berlavoile@outlook.fr en y ajoutant une ou deux photos.
S'armer d'un brin de patience"

JSON attendu:
{
  "NAME": null,
  "RELIGION": null,
  "AGE": "40 ans",
  "SEX": "Homme",
  "HEIGHT": "1.75 m",
  "WEIGHT": null,
  "PRIMARY_COUNTRY_OF_RESIDENCE": "France",
  "OTHER_LOCATIONS_MENTIONED": [],
  "COUNTRY_OF_ORIGIN": null,
  "SECTOR_OF_ACTIVITY": "Ingénieur",
  "MARITAL_STATUS": null,
  "HAS_CHILDREN": "Oui",
  "NUMBER_OF_CHILDREN": "1",
  "QUALITIES": ["simple", "posé", "clair"],
  "VALUES": ["stabilité", "respect", "communication", "sincérité"],
  "DEFECTS": [],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": ["corpulence mince ou moyenne avec des formes africaines"],
  "ECONOMIC_SITUATION": [],
  "EDUCATION_LEVEL": [],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "≤ 40 ans",
    "résidant en Europe ou Afrique",
    "belle et féminine",
    "propre, douce, respectueuse et équilibrée",
    "ambitieuse avec objectifs clairs"
  ]
}

Exemple 3 (annonce USA / Ouest) :
Texte: "Âge : 38 ans
Profession: employé dans une entreprise de la place 
Origine : Ouest
Pays de Residence : USA
Bonjour les Cheldimois, 
Je suis un homme posé et ouvert d'esprit, vivant aux États-Unis. Je  recherche une femme respectueuse, simple et authentique. Une femme qui sait communiquer avec maturité, attachée aux valeurs familiales et maternelles, et prête à s'engager pleinement dans une relation saine, positive et durable. 
Je souhaite bâtir une relation fondée sur la confiance, le dialogue, la stabilité, avec en ligne de mire un vrai projet de vie : fonder une famille, avancer ensemble et grandir à deux. Ici, pas de jeu ni de relation superficielle : l'intention est claire, le cœur aussi.
En retour, je t'offrirai de l'amour sincère, du respect, de la sécurité émotionnelle et l'envie réelle de construire une relation sérieuse, basée sur la compréhension mutuelle. Je souhaite rencontrer une femme résidant également aux États-Unis, prête à marcher à ses côtés, main dans la main, vers un avenir partagé.
Si tu te reconnais dans ces critères, écris-moi directement via Cheldim Agence au 692703981, pour entamer cette belle histoire."

JSON attendu:
{
  "NAME": null,
  "RELIGION": null,
  "AGE": "38 ans",
  "SEX": "Homme",
  "HEIGHT": null,
  "WEIGHT": null,
  "PRIMARY_COUNTRY_OF_RESIDENCE": "USA",
  "OTHER_LOCATIONS_MENTIONED": ["Ouest"],
  "COUNTRY_OF_ORIGIN": null,
  "SECTOR_OF_ACTIVITY": "employé",
  "MARITAL_STATUS": null,
  "HAS_CHILDREN": null,
  "NUMBER_OF_CHILDREN": null,
  "QUALITIES": ["posé", "ouvert d'esprit"],
  "VALUES": ["valeurs familiales", "maternelles", "confiance", "dialogue", "stabilité"],
  "DEFECTS": [],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": [],
  "ECONOMIC_SITUATION": [],
  "EDUCATION_LEVEL": [],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "résidant aux États-Unis",
    "respectueuse, simple et authentique",
    "sait communiquer avec maturité",
    "attachée aux valeurs familiales et maternelles",
    "projet de fonder une famille"
  ]
}

Exemple 4 (annonce Laval / 00 enfants) :
Texte: "Homme,
𝗔̂𝗴𝗲 : 39 ans
Statut matrimonial : célibataire
𝗣𝗮𝘆𝘀 𝗱'𝗼𝗿𝗶𝗴𝗶𝗻𝗲 : Cameroun
Religion: Catholique
𝗣𝗿𝗼𝗳𝗲𝘀𝘀𝗶𝗼𝗻 : Analyste d'Affaires
𝗡𝗼𝗺𝗯𝗿𝗲 𝗱'𝗲𝗻𝗳𝗮𝗻𝘁𝘀 : 00
𝗩𝗶𝗹𝗹𝗲 𝗱𝗲 𝗥𝗲́𝘀𝗶𝗱𝗲𝗻𝗰𝗲: Laval
Critères de recherche :
Entre 20 et 38 ans.
Veut se poser, aime et aimerait avoir des enfants. Présentable, la beauté est éphémère mais j'aimerais bien qu'elle soit appréciable à la vue.
𝗦𝗼𝗻 𝗮𝘃𝗶𝘀 𝘀𝘂𝗿 𝗟𝗲 𝟱𝟬/𝟱𝟬:
Je ne partage pas vraiment l'avis du 50/50 car dans les faits ça ne fait pas sens. Pas possible de diviser tout en deux. Je prefere plus le dialogue commun et en fonction des situations on s'organise mutuellement. Je suis plus pour une discussion sur les charges qu'on pourrait se partager pour faire bien fonctionner le couple. Afin qu'on sorte sans avoir l'impression que sa pèse sur l'un ou lautre. Donc mots clés entente, communication.
𝗦𝘂𝗿 𝗹𝗮 𝘀𝗼𝘂𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝗱𝗲 𝗹𝗮 𝗳𝗲𝗺𝗺𝗲
Je ne crois pas à la soumission de la femme. Je crois plutôt à l'éducation. Une femme n'a pas besoin d'être soumise, juste avoir une bonne éducation de base. Le respect mutuel représentera assez bien nos éducation respectives. Et si nous avons ces bases la nous serons naturellement soumis l'un à l'autre.
Si cette Annonce te parle, contacte moi par le biais de Âmes Sœurs Au Canada sur telegram au +𝟏𝟔𝟏𝟑 6974598"

JSON attendu:
{
  "NAME": null,
  "RELIGION": "Catholique",
  "AGE": "39 ans",
  "SEX": "Homme",
  "HEIGHT": null,
  "WEIGHT": null,
  "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
  "OTHER_LOCATIONS_MENTIONED": ["Laval"],
  "COUNTRY_OF_ORIGIN": "Cameroun",
  "SECTOR_OF_ACTIVITY": "Analyste d'Affaires",
  "MARITAL_STATUS": "célibataire",
  "HAS_CHILDREN": "Non",
  "NUMBER_OF_CHILDREN": "0",
  "QUALITIES": [],
  "VALUES": ["entente", "communication", "respect mutuel", "éducation"],
  "DEFECTS": [],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": ["présentable", "beauté appréciable à la vue"],
  "ECONOMIC_SITUATION": [],
  "EDUCATION_LEVEL": [],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "20-38 ans",
    "veut se poser et avoir des enfants",
    "présentable avec beauté appréciable",
    "préfère dialogue sur les charges plutôt que 50/50 strict",
    "contre soumission mais pour respect mutuel"
  ]
}

Exemple 5 (annonce Canada / 70kg) :
Texte: "Bonjour au  grand frère Warman et à tata Paule! Je tiens à vous remercier pour le grand travail que vous abattez au sein de la communauté. Je suis une  camerounaise âgé de 35ans résident au Canada. 

Célibataire sans enfant, en début de carrière, pèse 70kg/ 1.70. J'attends souvent dire de moi que je suis  respectueuse, douce et travailleuse. 

J'ai décidé de faire cette annonce à la recherche de mon mâle dominant avec qui on doit fonder une famille solide. 

Avoir entre 35-42ans , resident au Canada sans enfant ou un au trop. Il doit mesurer 1.72 et plus, etre travailleur, respectueux et le sens de l'humour... 

A toi qui lis ceci si tu remplis les critères et aimerait en savoir plus je t'attends chaleureusement 

👉👉👉 
Amouradeux202201@yahoo.com"

JSON attendu:
{
  "NAME": null,
  "RELIGION": null,
  "AGE": "35 ans",
  "SEX": "Femme",
  "HEIGHT": "1.70 m",
  "WEIGHT": "70 kg",
  "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
  "OTHER_LOCATIONS_MENTIONED": [],
  "COUNTRY_OF_ORIGIN": "Cameroun",
  "SECTOR_OF_ACTIVITY": null,
  "MARITAL_STATUS": "célibataire",
  "HAS_CHILDREN": "Non",
  "NUMBER_OF_CHILDREN": "0",
  "QUALITIES": ["respectueuse", "douce", "travailleuse"],
  "VALUES": ["famille solide"],
  "DEFECTS": [],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": [],
  "ECONOMIC_SITUATION": ["début de carrière"],
  "EDUCATION_LEVEL": [],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "35-42 ans",
    "résidant au Canada",
    "sans enfant ou un maximum",
    "mesure 1.72m+",
    "travailleur, respectueux, sens de l'humour"
  ]
}

Exemple 6 (annonce Ottawa compacte) :
Texte: "𝗖Œ𝗨𝗥 𝗔̀ 𝗣𝗥𝗘𝗡𝗗𝗥𝗘 💕💕
Femme, 
29 ans Enfant 0CélibataireChrétienne protestante 1m65 80 kg Sud cameroun
Diplôme licence au Cameroun mais actuellement aux études à Ottawa depuis un an en administration de bureau pour être assistante/ adjointe administrative
Ville : Ottawa 
50/50 je pense que c'est l'homme le chef de famille dont financièrement sans se mentir il a d'abord une plus grosse charge financière mentale mais la femme va tjr contribuer aux charges de la famille logiquement sans même qu'on lui demande c'est naturel vu qu'elle travaille aussi 
Les finances doivent se gérer en couple pour une meilleure entente et meilleure évolution de la famille 
La religion est très importante la prière est nécessaire pour tous surtout dans le mariage
Apport dans le couple : je suis une personne de nature très sympa et joviale qui sait aimer en retour er surtout le respect de son partenaire 
Défauts : je dirai têtue mais j'essaye de contrôler ça , je stresse aussi beaucoup 
Implications des familles le mariage de l'union des familles aussi  s'ilYa pas l'entente je pense pas que le couple sera heureux L'homme est le chef de famille comme j'ai dis plus haut il a une grosse charge bien que la femme soit celle qui doit en majorité contrôler tout mais c'est lui le leader
Si cette annonce t'interesse, contacte moi par le biais de Âmes Sœurs au Canada au +𝟭𝟲𝟭𝟯𝟰𝟲𝟮𝟰𝟳𝟵𝟵 𝘁𝗲𝗹𝗲𝗴𝗿𝗮𝗺"

JSON attendu:
{
  "NAME": null,
  "RELIGION": "protestante",
  "AGE": "29 ans",
  "SEX": "Femme",
  "HEIGHT": "1.65 m",
  "WEIGHT": "80 kg",
  "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
  "OTHER_LOCATIONS_MENTIONED": ["Ottawa", "Sud"],
  "COUNTRY_OF_ORIGIN": "Cameroun",
  "SECTOR_OF_ACTIVITY": "administration de bureau",
  "MARITAL_STATUS": "célibataire",
  "HAS_CHILDREN": "Non",
  "NUMBER_OF_CHILDREN": "0",
  "QUALITIES": ["sympa", "joviale", "sait aimer"],
  "VALUES": ["50/50 avec dialogue", "religion importante", "prière", "implication des familles"],
  "DEFECTS": ["têtue", "stress"],
  "INTERESTS": [],
  "PHYSICAL_APPEARANCE": [],
  "ECONOMIC_SITUATION": [],
  "EDUCATION_LEVEL": ["licence"],
  "ILLNESS": [],
  "RELATIONSHIP": [
    "homme chef de famille mais dialogue sur les charges",
    "gestion financière en couple",
    "religion très importante avec prière",
    "implication des deux familles dans le mariage",
    "respect mutuel"
  ]
}

Annonce à traiter (extraire UNIQUEMENT cette annonce) :
{ad_text}
"""

PROMPT_DUAL_PROFILE_WITH_POSITIONS = """
Tu es un expert en extraction d'entités nommées (NER) ET en structuration sémantique pour annonces matrimoniales camerounaises.
CHAQUE annonce contient DEUX profils DISTINCTS :

1. **ADVERTISER** : La personne qui publie l'annonce (décrite dans la première partie)
2. **DESIRED** : La personne recherchée (décrite dans une section "Je recherche...", "Critères de recherche", etc.)

Pour CHAQUE profil, tu dois produire :
✅ ENTITÉS AVEC POSITIONS : Extraction textuelle exacte + positions caractères (0-based, start inclusif / end exclusif)
✅ DONNÉES STRUCTURÉES : Normalisation métier selon le schéma défini

═══════════════════════════════════════════════════════════════════════════════
FORMAT DE SORTIE STRICT (JSON valide UNIQUE) :
═══════════════════════════════════════════════════════════════════════════════
{
  "entities": {
    "advertiser": [
      {
        "text": "valeur EXACTE extraite",
        "label": "NOM_DU_CHAMP",
        "start": position_début_0_based,
        "end": position_fin_exclusive,
        "confidence": 0.95
      }
    ],
    "desired": [
      {
        "text": "valeur EXACTE extraite",
        "label": "NOM_DU_CHAMP",
        "start": position_début_0_based,
        "end": position_fin_exclusive,
        "confidence": 0.95
      }
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": "...",
      "RELIGION": "...",
      "AGE": "...",
      "SEX": "...",
      "HEIGHT": "...",
      "WEIGHT": "...",
      "PRIMARY_COUNTRY_OF_RESIDENCE": "...",
      "OTHER_LOCATIONS_MENTIONED": [...],
      "COUNTRY_OF_ORIGIN": "...",
      "SECTOR_OF_ACTIVITY": "...",
      "MARITAL_STATUS": "...",
      "HAS_CHILDREN": "...",
      "NUMBER_OF_CHILDREN": "...",
      "QUALITIES": [...],
      "VALUES": [...],
      "DEFECTS": [...],
      "INTERESTS": [...],
      "PHYSICAL_APPEARANCE": [...],
      "ECONOMIC_SITUATION": [...],
      "EDUCATION_LEVEL": [...],
      "ILLNESS": [...],
      "RELATIONSHIP": [...]  // ← Ce champ est VIDE pour l'advertiser (réservé au desired)
    },
    "desired": {
      "NAME": null,  // ← Toujours null (on ne connaît pas le nom de la personne recherchée)
      "RELIGION": "...",
      "AGE": "...",
      "SEX": "...",
      "HEIGHT": "...",
      "WEIGHT": "...",
      "PRIMARY_COUNTRY_OF_RESIDENCE": "...",
      "OTHER_LOCATIONS_MENTIONED": [...],
      "COUNTRY_OF_ORIGIN": "...",
      "SECTOR_OF_ACTIVITY": "...",
      "MARITAL_STATUS": "...",
      "HAS_CHILDREN": "...",
      "NUMBER_OF_CHILDREN": "...",
      "QUALITIES": [...],
      "VALUES": [...],
      "DEFECTS": [...],
      "INTERESTS": [...],
      "PHYSICAL_APPEARANCE": [...],
      "ECONOMIC_SITUATION": [...],
      "EDUCATION_LEVEL": [...],
      "ILLNESS": [...],
      "RELATIONSHIP": [...]  // ← Ce champ décrit CE QUE L'ADVERISER CHERCHE CHEZ LUI-MÊME
    }
  }
}

═══════════════════════════════════════════════════════════════════════════════
RÈGLES CRITIQUES POUR LES POSITIONS
═══════════════════════════════════════════════════════════════════════════════
1. INDEXATION 0-BASED : Premier caractère = position 0
2. EXACTITUDE ABSOLUE : 
   - text[start:end] doit retourner EXACTEMENT la valeur extraite
   - Inclure TOUS les espaces et ponctuations dans le span
3. POUR LES LISTES : Une entité PAR élément (ex: "humble, honnête" → 2 entités)
4. NE PAS NORMALISER pour les positions : garder "1m64" tel quel → positions sur "1m64"
   - La normalisation ("1.64 m") se fait SEULEMENT dans profiles.advertiser/desired

═══════════════════════════════════════════════════════════════════════════════
RÈGLES MÉTIER SPÉCIFIQUES AUX DEUX PROFILS
═══════════════════════════════════════════════════════════════════════════════
| Champ | Advertiser | Desired |
|-------|------------|---------|
| NAME | Peut être présent (pseudo/email) | Toujours null |
| SEX | Déduit du texte ("homme"/"femme") | Déduit des critères ("femme"/"homme") |
| AGE | Âge de l'annonceur | Tranche d'âge recherchée (ex: "45-50 ans") |
| HAS_CHILDREN/NUMBER_OF_CHILDREN | Basé sur "maman/papa/enfants" | Basé sur critères ("sans enfant", "déjà papa") |
| RELATIONSHIP | Toujours [] (vide) | Critères de recherche RÉSUMÉS en 3-5 phrases |
| QUALITIES | Qualités de l'annonceur | Qualités recherchées chez le partenaire |

═══════════════════════════════════════════════════════════════════════════════
EXEMPLES RÉELS COMPLETS (4 annonces fournies + 2 supplémentaires)
═══════════════════════════════════════════════════════════════════════════════

Exemple 1 : Annonce Cheldim structurée (Homme 40 ans, France)
Texte: "𝙍𝒆𝒏𝒄𝒐𝒏𝒕𝒓𝒆 𝙎𝒆́𝙧𝙞𝙚𝙪𝙨𝙚, 𝙋𝒓𝙤𝒇𝙞𝙡 𝑽𝙚́𝒓𝙞𝒇𝙞𝙚́,\\n𝐶𝘩𝑒𝘭𝘥𝘪𝘮 𝐴𝑔𝑒𝘯𝘤𝑒 𝘔𝘢𝘵𝘳𝘪𝘮𝘰𝘯𝘪𝘢𝘭𝘦 237\\nÂge : 40 ans\\nSituation familiale : 1 enfant\\nMétier : Ingénieur\\nLieu de résidence : France\\nTaille : 1m75\\nHomme de 40ans, résidant en France, Je suis une personne simple, posée et claire dans mes intentions. Je sais ce que je veux et je sais *surtout ce que je ne veux pas*, donc je  m'inscris dans une démarche sérieuse.\\nJ'accorde une grande importance à la stabilité, au respect, à la communication et à la sincérité. Pour moi, une relation durable se construit sur des bases solides, une vision commune et une volonté réelle de s'engager.\\n👩‍🦰 La femme que je souhaite rencontrer\\nJe recherche une femme :\\nâgée de 40 ans maximum,\\nrésidant en Europe ou Afrique\\nqui se sent belle et féminine,\\nPropre, douce, respectueuse et équilibrée,\\nambitieuse, avec des objectifs clairs, de corpulence mince ou moyenne avec des formes africaines, naturelles et assumées.\\n💞 Ce que je peux offrir\\nJe suis un homme capable d'apporter :\\nune présence stable et rassurante,\\ndu respect, de la loyauté et de la considération,\\nun cadre de relation sain et structuré,\\nune relation fondée sur la communication, la compréhension et l'engagement.\\n🎯 Objectif : construire une relation sérieuse, saine et durable, basée sur le respect mutuel, la stabilité émotionnelle et une volonté commune d'avancer ensemble.\\nSi interessé m'écrire à berlavoile@outlook.fr en y ajoutant une ou deux photos.\\nS'armer d'un brin de patience"

Sortie attendue:
{
  "entities": {
    "advertiser": [
      {"text": "Homme", "label": "SEX", "start": 242, "end": 247, "confidence": 0.99},
      {"text": "40 ans", "label": "AGE", "start": 30, "end": 36, "confidence": 0.98},
      {"text": "1 enfant", "label": "CHILDREN", "start": 65, "end": 74, "confidence": 0.97},
      {"text": "Ingénieur", "label": "SECTOR_OF_ACTIVITY", "start": 90, "end": 99, "confidence": 0.96},
      {"text": "France", "label": "COUNTRY_OF_RESIDENCE", "start": 125, "end": 131, "confidence": 0.98},
      {"text": "1m75", "label": "HEIGHT", "start": 145, "end": 149, "confidence": 0.95},
      {"text": "simple", "label": "QUALITY", "start": 282, "end": 288, "confidence": 0.93},
      {"text": "posée", "label": "QUALITY", "start": 290, "end": 295, "confidence": 0.92},
      {"text": "claire", "label": "QUALITY", "start": 300, "end": 306, "confidence": 0.91}
    ],
    "desired": [
      {"text": "femme", "label": "SEX", "start": 475, "end": 480, "confidence": 0.99},
      {"text": "40 ans maximum", "label": "AGE", "start": 498, "end": 513, "confidence": 0.94},
      {"text": "Europe ou Afrique", "label": "COUNTRY_OF_RESIDENCE", "start": 530, "end": 547, "confidence": 0.93},
      {"text": "belle et féminine", "label": "PHYSICAL_APPEARANCE", "start": 565, "end": 583, "confidence": 0.90},
      {"text": "Propre", "label": "QUALITY", "start": 585, "end": 591, "confidence": 0.92},
      {"text": "douce", "label": "QUALITY", "start": 593, "end": 598, "confidence": 0.93},
      {"text": "respectueuse", "label": "QUALITY", "start": 600, "end": 612, "confidence": 0.94},
      {"text": "équilibrée", "label": "QUALITY", "start": 617, "end": 627, "confidence": 0.91},
      {"text": "ambitieuse", "label": "QUALITY", "start": 629, "end": 639, "confidence": 0.92},
      {"text": "corpulence mince ou moyenne avec des formes africaines", "label": "PHYSICAL_APPEARANCE", "start": 665, "end": 720, "confidence": 0.89}
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "40 ans",
      "SEX": "Homme",
      "HEIGHT": "1.75 m",
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "France",
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": "Ingénieur",
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": "Oui",
      "NUMBER_OF_CHILDREN": "1",
      "QUALITIES": ["simple", "posé", "clair"],
      "VALUES": ["stabilité", "respect", "communication", "sincérité"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": []
    },
    "desired": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "≤ 40 ans",
      "SEX": "Femme",
      "HEIGHT": null,
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "Europe ou Afrique",
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": null,
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": null,
      "NUMBER_OF_CHILDREN": null,
      "QUALITIES": ["belle", "féminine", "propre", "douce", "respectueuse", "équilibrée", "ambitieuse"],
      "VALUES": [],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": ["corpulence mince ou moyenne avec des formes africaines"],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": [
        "≤ 40 ans",
        "résidant en Europe ou Afrique",
        "belle et féminine",
        "propre, douce, respectueuse et équilibrée",
        "ambitieuse avec objectifs clairs"
      ]
    }
  }
}

Exemple 2 : Annonce USA / Ouest (Homme 38 ans)
Texte: "Âge : 38 ans\\nProfession: employé dans une entreprise de la place \\nOrigine : Ouest\\nPays de Residence : USA\\nBonjour les Cheldimois, \\nJe suis un homme posé et ouvert d'esprit, vivant aux États-Unis. Je  recherche une femme respectueuse, simple et authentique. Une femme qui sait communiquer avec maturité, attachée aux valeurs familiales et maternelles, et prête à s'engager pleinement dans une relation saine, positive et durable. \\nJe souhaite bâtir une relation fondée sur la confiance, le dialogue, la stabilité, avec en ligne de mire un vrai projet de vie : fonder une famille, avancer ensemble et grandir à deux. Ici, pas de jeu ni de relation superficielle : l'intention est claire, le cœur aussi.\\nEn retour, je t'offrirai de l'amour sincère, du respect, de la sécurité émotionnelle et l'envie réelle de construire une relation sérieuse, basée sur la compréhension mutuelle. Je souhaite rencontrer une femme résidant également aux États-Unis, prête à marcher à ses côtés, main dans la main, vers un avenir partagé.\\nSi tu te reconnais dans ces critères, écris-moi directement via Cheldim Agence au 692703981, pour entamer cette belle histoire."

Sortie attendue:
{
  "entities": {
    "advertiser": [
      {"text": "38 ans", "label": "AGE", "start": 6, "end": 12, "confidence": 0.98},
      {"text": "employé", "label": "SECTOR_OF_ACTIVITY", "start": 32, "end": 39, "confidence": 0.92},
      {"text": "Ouest", "label": "REGION", "start": 78, "end": 83, "confidence": 0.95},
      {"text": "USA", "label": "COUNTRY_OF_RESIDENCE", "start": 106, "end": 109, "confidence": 0.99},
      {"text": "homme", "label": "SEX", "start": 135, "end": 140, "confidence": 0.99},
      {"text": "États-Unis", "label": "COUNTRY_OF_RESIDENCE", "start": 171, "end": 181, "confidence": 0.97},
      {"text": "posé", "label": "QUALITY", "start": 192, "end": 196, "confidence": 0.94},
      {"text": "ouvert d'esprit", "label": "QUALITY", "start": 201, "end": 216, "confidence": 0.93}
    ],
    "desired": [
      {"text": "femme", "label": "SEX", "start": 235, "end": 240, "confidence": 0.99},
      {"text": "respectueuse", "label": "QUALITY", "start": 253, "end": 265, "confidence": 0.94},
      {"text": "simple", "label": "QUALITY", "start": 267, "end": 273, "confidence": 0.93},
      {"text": "authentique", "label": "QUALITY", "start": 278, "end": 289, "confidence": 0.92},
      {"text": "valeurs familiales", "label": "VALUE", "start": 336, "end": 354, "confidence": 0.91},
      {"text": "maternelles", "label": "VALUE", "start": 359, "end": 370, "confidence": 0.90},
      {"text": "États-Unis", "label": "COUNTRY_OF_RESIDENCE", "start": 645, "end": 655, "confidence": 0.96},
      {"text": "fonder une famille", "label": "RELATIONSHIP_GOAL", "start": 495, "end": 512, "confidence": 0.89}
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "38 ans",
      "SEX": "Homme",
      "HEIGHT": null,
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "USA",
      "OTHER_LOCATIONS_MENTIONED": ["Ouest"],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": "employé",
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": null,
      "NUMBER_OF_CHILDREN": null,
      "QUALITIES": ["posé", "ouvert d'esprit"],
      "VALUES": ["valeurs familiales", "maternelles", "confiance", "dialogue", "stabilité"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": []
    },
    "desired": {
      "NAME": null,
      "RELIGION": null,
      "AGE": null,
      "SEX": "Femme",
      "HEIGHT": null,
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "USA",
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": null,
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": null,
      "NUMBER_OF_CHILDREN": null,
      "QUALITIES": ["respectueuse", "simple", "authentique"],
      "VALUES": ["valeurs familiales", "maternelles", "confiance", "dialogue", "stabilité"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": [
        "résidant aux États-Unis",
        "respectueuse, simple et authentique",
        "sait communiquer avec maturité",
        "attachée aux valeurs familiales et maternelles",
        "projet de fonder une famille"
      ]
    }
  }
}

Exemple 3 : Annonce Laval / 00 enfants (Homme 39 ans, Camerounais au Canada)
Texte: "Homme,\\n𝗔̂𝗴𝗲 : 39 ans\\nStatut matrimonial : célibataire\\n𝗣𝗮𝘆𝘀 𝗱'𝗼𝗿𝗶𝗴𝗶𝗻𝗲 : Cameroun\\nReligion: Catholique\\n𝗣𝗿𝗼𝗳𝗲𝘀𝘀𝗶𝗼𝗻 : Analyste d'Affaires\\n𝗡𝗼𝗺𝗯𝗿𝗲 𝗱'𝗲𝗻𝗳𝗮𝗻𝘁𝘀 : 00\\n𝗩𝗶𝗹𝗹𝗲 𝗱𝗲 𝗥𝗲́𝘀𝗶𝗱𝗲𝗻𝗰𝗲: Laval\\nCritères de recherche :\\nEntre 20 et 38 ans.\\nVeut se poser, aime et aimerait avoir des enfants. Présentable, la beauté est éphémère mais j'aimerais bien qu'elle soit appréciable à la vue.\\n𝗦𝗼𝗻 𝗮𝘃𝗶𝘀 𝘀𝘂𝗿 𝗟𝗲 𝟱𝟬/𝟱𝟬:\\nJe ne partage pas vraiment l'avis du 50/50 car dans les faits ça ne fait pas sens. Pas possible de diviser tout en deux. Je prefere plus le dialogue commun et en fonction des situations on s'organise mutuellement. Je suis plus pour une discussion sur les charges qu'on pourrait se partager pour faire bien fonctionner le couple. Afin qu'on sorte sans avoir l'impression que sa pèse sur l'un ou lautre. Donc mots clés entente, communication.\\n𝗦𝘂𝗿 𝗹𝗮 𝘀𝗼𝘂𝗺𝗶𝘀𝘀𝗶𝗼𝗻 𝗱𝗲 𝗹𝗮 𝗳𝗲𝗺𝗺𝗲\\nJe ne crois pas à la soumission de la femme. Je crois plutôt à l'éducation. Une femme n'a pas besoin d'être soumise, juste avoir une bonne éducation de base. Le respect mutuel représentera assez bien nos éducation respectives. Et si nous avons ces bases la nous serons naturellement soumis l'un à l'autre.\\nSi cette Annonce te parle, contacte moi par le biais de Âmes Sœurs Au Canada sur telegram au +𝟏𝟔𝟏𝟑 6974598"

Sortie attendue:
{
  "entities": {
    "advertiser": [
      {"text": "Homme", "label": "SEX", "start": 0, "end": 5, "confidence": 0.99},
      {"text": "39 ans", "label": "AGE", "start": 13, "end": 19, "confidence": 0.98},
      {"text": "célibataire", "label": "MARITAL_STATUS", "start": 48, "end": 59, "confidence": 0.97},
      {"text": "Cameroun", "label": "COUNTRY_OF_ORIGIN", "start": 84, "end": 93, "confidence": 0.99},
      {"text": "Catholique", "label": "RELIGION", "start": 104, "end": 114, "confidence": 0.98},
      {"text": "Analyste d'Affaires", "label": "SECTOR_OF_ACTIVITY", "start": 135, "end": 154, "confidence": 0.96},
      {"text": "00", "label": "NUMBER_OF_CHILDREN_RAW", "start": 183, "end": 185, "confidence": 0.95},
      {"text": "Laval", "label": "CITY", "start": 210, "end": 215, "confidence": 0.97},
      {"text": "entente", "label": "VALUE", "start": 720, "end": 727, "confidence": 0.91},
      {"text": "communication", "label": "VALUE", "start": 729, "end": 742, "confidence": 0.91},
      {"text": "respect mutuel", "label": "VALUE", "start": 875, "end": 889, "confidence": 0.93}
    ],
    "desired": [
      {"text": "20 et 38 ans", "label": "AGE", "start": 245, "end": 256, "confidence": 0.94},
      {"text": "avoir des enfants", "label": "HAS_CHILDREN", "start": 295, "end": 312, "confidence": 0.92},
      {"text": "présentable", "label": "PHYSICAL_APPEARANCE", "start": 314, "end": 325, "confidence": 0.90},
      {"text": "beauté appréciable", "label": "PHYSICAL_APPEARANCE", "start": 358, "end": 376, "confidence": 0.89}
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": null,
      "RELIGION": "Catholique",
      "AGE": "39 ans",
      "SEX": "Homme",
      "HEIGHT": null,
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
      "OTHER_LOCATIONS_MENTIONED": ["Laval"],
      "COUNTRY_OF_ORIGIN": "Cameroun",
      "SECTOR_OF_ACTIVITY": "Analyste d'Affaires",
      "MARITAL_STATUS": "célibataire",
      "HAS_CHILDREN": "Non",
      "NUMBER_OF_CHILDREN": "0",
      "QUALITIES": [],
      "VALUES": ["entente", "communication", "respect mutuel", "éducation"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": []
    },
    "desired": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "20-38 ans",
      "SEX": "Femme",
      "HEIGHT": null,
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": null,
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": null,
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": "Oui",
      "NUMBER_OF_CHILDREN": null,
      "QUALITIES": [],
      "VALUES": ["dialogue sur les charges", "respect mutuel"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": ["présentable", "beauté appréciable à la vue"],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": [
        "20-38 ans",
        "veut se poser et avoir des enfants",
        "présentable avec beauté appréciable",
        "préfère dialogue sur les charges plutôt que 50/50 strict",
        "contre soumission mais pour respect mutuel"
      ]
    }
  }
}

Exemple 4 : Annonce Canada / 70kg (Femme 35 ans, Camerounaise)
Texte: "Bonjour au  grand frère Warman et à tata Paule! Je tiens à vous remercier pour le grand travail que vous abattez au sein de la communauté. Je suis une  camerounaise âgé de 35ans résident au Canada. \\n\\nCélibataire sans enfant, en début de carrière, pèse 70kg/ 1.70. J'attends souvent dire de moi que je suis  respectueuse, douce et travailleuse. \\n\\nJ'ai décidé de faire cette annonce à la recherche de mon mâle dominant avec qui on doit fonder une famille solide. \\n\\nAvoir entre 35-42ans , resident au Canada sans enfant ou un au trop. Il doit mesurer 1.72 et plus, etre travailleur, respectueux et le sens de l'humour... \\n\\nA toi qui lis ceci si tu remplis les critères et aimerait en savoir plus je t'attends chaleureusement \\n\\n👉👉👉 \\nAmouradeux202201@yahoo.com"

Sortie attendue:
{
  "entities": {
    "advertiser": [
      {"text": "camerounaise", "label": "NATIONALITY", "start": 128, "end": 140, "confidence": 0.99},
      {"text": "35ans", "label": "AGE", "start": 147, "end": 152, "confidence": 0.97},
      {"text": "Canada", "label": "COUNTRY_OF_RESIDENCE", "start": 166, "end": 172, "confidence": 0.98},
      {"text": "Célibataire", "label": "MARITAL_STATUS", "start": 176, "end": 187, "confidence": 0.96},
      {"text": "sans enfant", "label": "HAS_CHILDREN", "start": 188, "end": 199, "confidence": 0.95},
      {"text": "70kg", "label": "WEIGHT", "start": 238, "end": 242, "confidence": 0.94},
      {"text": "1.70", "label": "HEIGHT", "start": 244, "end": 248, "confidence": 0.93},
      {"text": "respectueuse", "label": "QUALITY", "start": 288, "end": 299, "confidence": 0.96},
      {"text": "douce", "label": "QUALITY", "start": 301, "end": 306, "confidence": 0.95},
      {"text": "travailleuse", "label": "QUALITY", "start": 311, "end": 322, "confidence": 0.94}
    ],
    "desired": [
      {"text": "35-42ans", "label": "AGE", "start": 440, "end": 448, "confidence": 0.92},
      {"text": "Canada", "label": "COUNTRY_OF_RESIDENCE", "start": 462, "end": 468, "confidence": 0.97},
      {"text": "sans enfant", "label": "HAS_CHILDREN", "start": 469, "end": 480, "confidence": 0.93},
      {"text": "1.72", "label": "HEIGHT", "start": 505, "end": 509, "confidence": 0.91},
      {"text": "travailleur", "label": "QUALITY", "start": 520, "end": 531, "confidence": 0.90},
      {"text": "respectueux", "label": "QUALITY", "start": 533, "end": 544, "confidence": 0.90},
      {"text": "sens de l'humour", "label": "QUALITY", "start": 551, "end": 568, "confidence": 0.89}
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "35 ans",
      "SEX": "Femme",
      "HEIGHT": "1.70 m",
      "WEIGHT": "70 kg",
      "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": "Cameroun",
      "SECTOR_OF_ACTIVITY": null,
      "MARITAL_STATUS": "célibataire",
      "HAS_CHILDREN": "Non",
      "NUMBER_OF_CHILDREN": "0",
      "QUALITIES": ["respectueuse", "douce", "travailleuse"],
      "VALUES": ["famille solide"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": ["début de carrière"],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": []
    },
    "desired": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "35-42 ans",
      "SEX": "Homme",
      "HEIGHT": "1.72 m+",
      "WEIGHT": null,
      "PRIMARY_COUNTRY_OF_RESIDENCE": "Canada",
      "OTHER_LOCATIONS_MENTIONED": [],
      "COUNTRY_OF_ORIGIN": null,
      "SECTOR_OF_ACTIVITY": null,
      "MARITAL_STATUS": null,
      "HAS_CHILDREN": "Non",
      "NUMBER_OF_CHILDREN": "0 ou 1 maximum",
      "QUALITIES": ["travailleur", "respectueux", "sens de l'humour"],
      "VALUES": ["famille solide"],
      "DEFECTS": [],
      "INTERESTS": [],
      "PHYSICAL_APPEARANCE": [],
      "ECONOMIC_SITUATION": [],
      "EDUCATION_LEVEL": [],
      "ILLNESS": [],
      "RELATIONSHIP": [
        "35-42 ans",
        "résidant au Canada",
        "sans enfant ou un maximum",
        "mesure 1.72m+",
        "travailleur, respectueux, sens de l'humour"
      ]
    }
  }
}

═══════════════════════════════════════════════════════════════════════════════
CAS PARTICULIERS À GÉRER
═══════════════════════════════════════════════════════════════════════════════
1. Annonce SANS section "recherche" explicite :
   → profiles.desired = tous les champs null sauf RELATIONSHIP = []
   → entities.desired = []

2. Sexe du desired non explicitement mentionné :
   → Déduire du contexte : "je recherche une femme" → "Femme", "mon mâle dominant" → "Homme"

3. Champs absents dans l'annonce :
   → Mettre null dans profiles (NE JAMAIS INFÉRER)

4. Texte compact sans sauts de ligne :
   → Appliquer les mêmes règles de parsing (ex: "29 ans Enfant 0Célibataire..." → séparer les entités)

═══════════════════════════════════════════════════════════════════════════════
Annonce à traiter (CONSERVER LE TEXTE ORIGINAL INTACT POUR LE CALCUL DES POSITIONS) :
{ad_text}
"""

system_message = """
You are CamerMatch-Extractor v2.1: a specialized NLP engine for Cameroonian matrimonial ads.

🎯 CORE MISSION
Extract TWO distinct profiles from each ad:
1. "advertiser": The person posting the ad (described in 1st person/initial section)
2. "desired": The person being sought (described after phrases like "Je recherche", "Critères", "mâle dominant")

📐 OUTPUT REQUIREMENTS (NON-NEGOTIABLE)
1. Return ONLY a single, VALID JSON object with this EXACT structure:
{
  "entities": {
    "advertiser": [{"text": "...", "label": "...", "start": int, "end": int, "confidence": float}],
    "desired": [{"text": "...", "label": "...", "start": int, "end": int, "confidence": float}]
  },
  "profiles": {
    "advertiser": { /* 21 standardized fields */ },
    "desired": { /* 21 standardized fields */ }
  }
}

2. POSITIONING RULES (CRITICAL FOR LABEL STUDIO):
   - 0-based indexing (first character = position 0)
   - "start" = inclusive index of first character
   - "end" = EXCLUSIVE index AFTER last character
   - VALIDATION: ad_text[start:end] MUST return EXACT extracted text
   - Example: "42 ans" in "Jeune femme de 42 ans" → start=15, end=21 (not 20!)

3. STRICT VALIDATION:
   ✅ JSON must parse with json.loads() without errors
   ✅ NO Markdown (```, **, etc.)
   ✅ NO prefixes/suffixes ("Here is the JSON:", "```json", etc.)
   ✅ NO comments (//, /* */)
   ✅ NO trailing commas
   ✅ ALL string values must use double quotes (")
   ✅ NULL values must be JSON null (not "null" string)

4. SEMANTIC RULES:
   • advertiser.RELATIONSHIP = [] (ALWAYS empty - describes self, not partner)
   • desired.NAME = null (ALWAYS - we never know the sought person's name)
   • desired.SEX = inferred from context ("femme recherchée" → "Femme")
   • NEVER infer missing info → use null for absent fields
   • Normalize numbers: "00" → "0", "un" → "1" (ONLY in profiles, NOT in entities.text)

5. ERROR PREVENTION:
   ⚠️ Compact text parsing: "29 ans Enfant 0Célibataire..." → split at number boundaries
   ⚠️ Mixed scripts: Handle 𝗮̂𝗴𝗲, Âge, age as equivalent for extraction
   ⚠️ Location resolution: "Sud cameroun" → country="Cameroun", region="Sud" (not country="Sud")
   ⚠️ Child count: "maman de 3 bambins" → HAS_CHILDREN="Oui", NUMBER_OF_CHILDREN="3"

❗ FAILURE MODES (AVOID THESE):
❌ Returning partial JSON
❌ Mixing advertiser/desired entities
❌ Using 1-based indexing for positions
❌ Inferring religion when not mentioned
❌ Normalizing text in entities.text (keep raw: "1m64" not "1.64 m")

📤 OUTPUT EXAMPLE (FIRST 3 FIELDS ONLY - FULL STRUCTURE REQUIRED):
{
  "entities": {
    "advertiser": [
      {"text": "femme", "label": "SEX", "start": 13, "end": 18, "confidence": 0.99},
      {"text": "42 ans", "label": "AGE", "start": 22, "end": 28, "confidence": 0.98}
    ],
    "desired": [
      {"text": "45 et 50 ans", "label": "AGE", "start": 140, "end": 152, "confidence": 0.92}
    ]
  },
  "profiles": {
    "advertiser": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "42 ans",
      "SEX": "Femme",
      ...
    },
    "desired": {
      "NAME": null,
      "RELIGION": null,
      "AGE": "45-50 ans",
      "SEX": "Homme",
      ...
    }
  }
}

⚠️ FINAL INSTRUCTION: Return ONLY the raw JSON object. Nothing before. Nothing after.
"""

PROMPT_WITH_POSITIONS = """
Tu es un expert en extraction d'entités nommées (NER) pour annonces matrimoniales camerounaises.
Pour CHAQUE entité ci-dessous, extrait :
1. La valeur textuelle EXACTE telle qu'elle apparaît dans l'annonce
2. Sa position caractère (start/end) dans le texte ORIGINAL
3. Son label sémantique

FORMAT DE SORTIE STRICT (JSON valide) :
{
  "entities": [
    {
      "text": "valeur exacte extraite",
      "label": "NOM_DU_CHAMP",
      "start": position_début_en_caractères,
      "end": position_fin_en_caractères,
      "confidence": 0.95  // Estimation de confiance (0.0-1.0)
    }
  ],
  "structured_data": {
    // Votre JSON structuré existant (AGE, SEX, etc.)
  }
}

RÈGLES CRITIQUES :
- LES POSITIONS DOIVENT ÊTRE EXACTES : utiliser Python len() pour compter les caractères
- Inclure les espaces dans le calcul : "42 ans" → start=12, end=18 (6 caractères)
- Pour les listes (QUALITIES), créer une entité PAR ÉLÉMENT
- NE PAS normaliser les valeurs : garder "1m64" tel quel pour les positions

EXEMPLE CONCRET :

Texte original (120 caractères):
"Jeune femme de 42 ans basée en Allemagne, 1m64 pour 65 kg, maman de 3 bambins"

Sortie attendue:
{
  "entities": [
    {"text": "femme", "label": "SEX", "start": 6, "end": 11, "confidence": 0.99},
    {"text": "42 ans", "label": "AGE", "start": 15, "end": 21, "confidence": 0.98},
    {"text": "Allemagne", "label": "COUNTRY_OF_RESIDENCE", "start": 34, "end": 43, "confidence": 0.97},
    {"text": "1m64", "label": "HEIGHT", "start": 45, "end": 49, "confidence": 0.95},
    {"text": "65 kg", "label": "WEIGHT", "start": 55, "end": 60, "confidence": 0.95},
    {"text": "3", "label": "NUMBER_OF_CHILDREN", "start": 73, "end": 74, "confidence": 0.85},
    {"text": "bambins", "label": "CHILD_REFERENCE", "start": 75, "end": 82, "confidence": 0.90}
  ],
  "structured_data": {
    "SEX": "Femme",
    "AGE": "42 ans",
    "PRIMARY_COUNTRY_OF_RESIDENCE": "Allemagne",
    "HEIGHT": "1.64 m",
    "WEIGHT": "65 kg",
    "HAS_CHILDREN": "Oui",
    "NUMBER_OF_CHILDREN": "3",
    ...
  }
}

Annonce à traiter (CONSERVER LE TEXTE ORIGINAL INTACT POUR LE CALCUL DES POSITIONS) :
{ad_text}
"""
