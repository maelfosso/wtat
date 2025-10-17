system_message = """
You are an expert JSON extractor for Cameroonian dating ads.

Your task is to extract two profiles — "advertiser" and "desired" — in a single valid JSON object with the exact keys and structure shown in the examples.

⚠ Return only the raw JSON object. Do not include any comments, introduction, explanations, Markdown (like back-ticks or headings), or trailing commas.

The output must be strictly valid JSON, with no additional text before or after.
"""

def sunday_rn_prompt(text_to_analyze):
  prompt = f"""
Tu es un expert en extraction d'informations structurées à partir d'annonces matrimoniales camerounaises.

### RÈGLES FINALES (IMPORTANTES)
- Tu dois répondre **UNIQUEMENT avec un objet JSON valide**.
- **Aucun texte, aucune explication, aucune balise, aucun commentaire** en dehors du JSON.
- Si une information n’existe pas → `null`.
- Utilise exactement les clés du template fourni ci-dessous.
- Respecte les formats suivants :
  - Âge → "35 ans", "30-39 ans", "max 26 ans".
  - Taille → "1.80 m" (et jamais "1m80").
  - Poids → "70 kg".
  - Pays / Régions → toujours sous forme de **liste JSON**, ex. ["Cameroun"] ou ["France","Île-de-France"].
  - `HAS_CHILDREN` → "Oui", "Non", ou null.
  - `NUMBER_OF_CHILDREN` → nombre entier ou null.
  - Tableaux → toujours en liste JSON, même vide : `[]`.

### TEMPLATE À RESPECTER STRICTEMENT
{{
  "advertiser": {{
    "NAME": null,
    "AGE": null,
    "SEX": null,
    "HEIGHT": null,
    "WEIGHT": null,
    "COUNTRY_OF_RESIDENCE": [],
    "COUNTRY_OF_ORIGIN": [],
    "REGION_OF_ORIGIN": [],
    "VILLAGE_OF_ORIGIN": null,
    "SECTOR_OF_ACTIVITY": null,
    "MARITAL_STATUS": null,
    "HAS_CHILDREN": null,
    "NUMBER_OF_CHILDREN": null,
    "QUALITIES": [],
    "VALUES": [],
    "DEFECTS": [],
    "INTERESTS": [],
    "PHYSICAL_APPEARANCE": null,
    "ECONOMIC_SITUATION": null,
    "EDUCATION_LEVEL": null,
    "ILLNESS": null,
    "RELATIONSHIP": []
  }},
  "desired": {{
    "NAME": null,
    "AGE": null,
    "SEX": null,
    "HEIGHT": null,
    "WEIGHT": null,
    "COUNTRY_OF_RESIDENCE": [],
    "COUNTRY_OF_ORIGIN": [],
    "REGION_OF_ORIGIN": [],
    "VILLAGE_OF_ORIGIN": null,
    "SECTOR_OF_ACTIVITY": null,
    "MARITAL_STATUS": null,
    "HAS_CHILDREN": null,
    "NUMBER_OF_CHILDREN": null,
    "QUALITIES": [],
    "VALUES": [],
    "DEFECTS": [],
    "INTERESTS": [],
    "PHYSICAL_APPEARANCE": null,
    "ECONOMIC_SITUATION": null,
    "EDUCATION_LEVEL": null,
    "ILLNESS": null,
    "RELATIONSHIP": []
  }}
}}

### TEXTE À ANALYSER :
{text_to_analyze}

### RÉPONDS UNIQUEMENT AVEC LE JSON :
"""

  return prompt

def special_rn_prompt(text_to_analyze):
  prompt = f"""
Tu es un expert en extraction d'informations structurées à partir d'annonces matrimoniales camerounaises.

### RÈGLES STRICTES
- Réponds UNIQUEMENT avec un objet JSON valide.
- Aucune explication, aucun commentaire, aucune balise, aucun texte hors JSON.
- Utilise exactement les clés du template ci-dessous.
- Si une information est absente → `null`.
- Formats obligatoires :
  - Âge → "35 ans", "18-24 ans", "max 26 ans".
  - Taille → "1.80 m".
  - Poids → "70 kg".
  - Pays / régions → liste JSON : ["Cameroun"], ["France","Île-de-France"].
  - `HAS_CHILDREN` → "Oui", "Non", ou null.
  - `NUMBER_OF_CHILDREN` → string ("sans enfant", "1 enfant", "2 enfants", "0-1 enfant") ou null.
  - Listes (`QUALITIES`, `VALUES`, `DEFECTS`, `INTERESTS`, `RELATIONSHIP`) → toujours **liste JSON valide** ([] si vide).

### TEMPLATE À REMPLIR
{{
  "advertiser": {{
    "NAME": null,
    "RELIGION": null,
    "AGE": null,
    "SEX": null,
    "HEIGHT": null,
    "WEIGHT": null,
    "COUNTRY_OF_RESIDENCE": [],
    "COUNTRY_OF_ORIGIN": null,
    "REGION_OF_ORIGIN": null,
    "VILLAGE_OF_ORIGIN": null,
    "SECTOR_OF_ACTIVITY": null,
    "MARITAL_STATUS": null,
    "HAS_CHILDREN": null,
    "NUMBER_OF_CHILDREN": null,
    "QUALITIES": [],
    "VALUES": [],
    "DEFECTS": [],
    "INTERESTS": [],
    "PHYSICAL_APPEARANCE": null,
    "ECONOMIC_SITUATION": null,
    "EDUCATION_LEVEL": null,
    "ILLNESS": null,
    "RELATIONSHIP": []
  }},
  "desired": {{
    "NAME": null,
    "RELIGION": null,
    "AGE": null,
    "SEX": null,
    "HEIGHT": null,
    "WEIGHT": null,
    "COUNTRY_OF_RESIDENCE": [],
    "COUNTRY_OF_ORIGIN": null,
    "REGION_OF_ORIGIN": null,
    "VILLAGE_OF_ORIGIN": null,
    "SECTOR_OF_ACTIVITY": null,
    "MARITAL_STATUS": null,
    "HAS_CHILDREN": null,
    "NUMBER_OF_CHILDREN": null,
    "QUALITIES": [],
    "VALUES": [],
    "DEFECTS": [],
    "INTERESTS": [],
    "PHYSICAL_APPEARANCE": null,
    "ECONOMIC_SITUATION": null,
    "EDUCATION_LEVEL": null,
    "ILLNESS": null,
    "RELATIONSHIP": []
  }}
}}

### TEXTE À ANALYSER
{text_to_analyze}

### JSON SEUL :
"""
  return prompt


# def special_rn_prompt(text_to_analyze):
#   prompt = f"""Tu es un expert en extraction d'informations structurées à partir d'annonces matrimoniales camerounaises.
  
#   INSTRUCTIONS:
#   - Extrait EXACTEMENT les informations demandées
#   - Sépare clairement Profile (annonceur) et Partner (recherché)
#   - Si une information n'existe pas → null
#   - Respecte les formats imposés
#   - Retourne UNIQUEMENT le JSON final
  
#   EXEMPLE D'EXTRACTION:
  
#   EXEMPLE D'ANNONCE:
#   "💚❤️💛 SPECIAL RECHERCHE NDOLO 100% KMER🇨🇲 VENANT DE FRANCE 🇨🇵
#   Salam Warman, merci pour ce que tu fais pour la communauté.
#   Je suis Aminou (nom d'emprunt). Musulman originaire de l'Adamaoua et vivant en île de France, je suis âgé de 30 ans et mesure 1m73 pour 88 kg. 
#   Célibataire et sans enfant, je suis stable professionnellement et travaille en finances.
#   Je suis attentionné, empathique et à l'écoute. Je sais aussi m'amuser et être sérieux quand il le faut..
#   À 30 ans, je me dis qu'il est grand temps de fonder ma petite famille insha Allah...
#   Je suis donc à la recherche d'une fille qui ressent le même appel du destin. Sérieuse et âgée de 18 à 24 ans, elle vit de préférence en France. Au delà, elle devrait vivre en Europe ou au Cameroun. 
#   Ma promise devra être pieuse, attentionnée et avoir le sens de la famille. Pour le reste, on apprendra à se compléter...
#   Assalamou alaykoum à toi qui me lit. Si tu te retrouves dans mes lignes, je serai ravi de te lire.
#   Je t'attends par ici halalhouse15@gmail.com"
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": "Aminou",
#       "RELIGION": "Mulsulman",
#       "AGE": "30 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_RESIDENCE": ["France", "île de France"],
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": "Adamaoua",
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "finances",
#       "MARITAL_STATUS": "Célibataire",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": "sans enfant",
#       "QUALITIES": ["attentionné", "empathique", "à l'écoute"],
#       "VALUES": ["famille", "religion musulmane"],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": "1.73 m",
#       "WEIGHT": "88 kg",
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "stable professionnellement",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": "fonder une famille"
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "18-24 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": ["France", "Cameroun", "Europe"],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": null,
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": ["sérieuse", "pieuse", "attentionnée", "sens de la famille"],
#       "VALUES": ["famille", "religion"],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": "fonder une famille"
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "💚❤️💛 SPECIAL RECHERCHE NDOLO 100% KMER🇨🇲 VENANT DU CANADA 🇨🇦
#   Si vous aussi souhaitez faire passer une annonce spéciale Recherche Ndolo sur la page, cliquez sur ce lien pour demander les modalités: https://wa.me/+237696493067
#   Bonjour au  grand frère Warman et à tata Paule! Je tiens à vous remercier pour le grand travail que vous abattez au sein de la communauté. Je suis une  camerounaise âgé de 35ans résident au Canada.
#   Célibataire sans enfant, en début de carrière, pèse 70kg/ 1.70. J'attends souvent dire de moi que je suis  respectueuse, douce et travailleuse.
#   J'ai décidé de faire cette annonce à la recherche de mon mâle dominant avec qui on doit fonder une famille solide.
#   Avoir entre 35-42ans , resident au Canada sans enfant ou un au trop. Il doit mesurer 1.72 et plus, etre travailleur, respectueux et le sens de l'humour...
#   A toi qui lis ceci si tu remplis les critères et aimerait en savoir plus je t'attends chaleureusement 
#   Amouradeux202201@yahoo.com"
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "35 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": ["Canada"],
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "en début de carrière",
#       "MARITAL_STATUS": "Célibataire",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": "sans enfant",
#       "QUALITIES": ["respectueuse", "douce", "travailleuse"],
#       "VALUES": ["famille solide"],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": "1.70 m",
#       "WEIGHT": "70 kg",
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "en début de carrière",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": "fonder une famille solide"
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "35-42 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_RESIDENCE": ["Canada"],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "sans enfant ou un au maximum",
#       "NUMBER_OF_CHILDREN": "0-1 enfant",
#       "QUALITIES": ["travailleur", "respectueux", "sens de l'humour"],
#       "VALUES": ["famille solide"],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": "1.72 m et plus",
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": "fonder une famille solide"
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "💚❤️💛 SPECIAL RECHERCHE NDOLO 100% KMER🇨🇲 VENANT DE FRANCE 🇫🇷
#   Si vous aussi souhaitez faire passer une annonce spéciale Recherche Ndolo sur la page, cliquez sur ce lien pour demander les modalités: https://wa.me/+237696493067
#   Bonjour warman et au terre. Qui suis-je? Une femme de 39 ans ( déjà!) vivant à Paris, stable professionnellement et maman d'un garçon de bientôt 4 ans.
#   Mes années de célibat m'ont permi de mieux me connaître et de mieux cerner ce à quoi j'aspire sur le long terme, comme quoi dans toute chose il y a du bon!
#   Aujpurd'hui je suis fin prête à écrire une nouvelle page avec toi mon futur partenaire...à partager, à te faire découvrir mon monde et découvrir le tien ( les 2 ne feront plus qu'un à terme),
#   à avancer dans la même direction tout en respectant les rêves et ambitions de chacun, à construire et profiter de la vie car elle mérite d'être vécue à 200%.
#   Je suis férue des voyages, du développement personnel mais aussi des plaisirs simples de la vie.
#   Mes 3 principales qualités: positive, intègre et une joie de vivre contagieuse.
#   Pour les défauts, tu auras le plaisir de t'y frotter plus tard!
#   Générosité, respect, tolérance et famille sont des valeurs chères à mes yeux.
#   J'attache aussi de l'importance à la communication dans un couple et à l'humour.
#   Physiquement on me dit charmante, je mesure 1m68 pour 67kgs.
#   Toi mon futur king, tu résides en France ( idéalement en IDF) ou pays limitrophes si tu es prêt à te déplacer. Stable professionnellement.
#   Agé entre 37 et 45 ans, avec ou sans enfants ( 2 maximum) et désireux de fonder ou d'élargir la famille.
#   Charmant tu l'es, confiance en toi tu l'as, attentionné, conciliant et ouvert au dialogue sans tabou et si tu es sportif c'est le graal! On ira courir ensemble!
#   Préférence pour les grands, au moins 1m77.
#   Si mon annonce a résonné en toi alors lance-toi et écris moi à cette adresse: kely82@yahoo.com accompagné d'une photo de toi sans filtre!"
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "39 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": ["France"],
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "stable professionnellement",
#       "MARITAL_STATUS": "Célibataire",
#       "HAS_CHILDREN": "Oui",
#       "NUMBER_OF_CHILDREN": "1 enfant (garçon de bientôt 4 ans)",
#       "QUALITIES": ["positive", "intègre", "joie de vivre contagieuse"],
#       "VALUES": ["générosité", "respect", "tolérance", "famille", "communication", "humour"],
#       "DEFECTS": "Non révélés (mentionnés comme surprise)",
#       "INTERESTS": ["voyages", "développement personnel", "plaisirs simples", "sport/course"],
#       "HEIGHT": "1.68 m",
#       "WEIGHT": "67 kg",
#       "PHYSICAL_APPEARANCE": "charmante",
#       "ECONOMIC_SITUATION": "stable professionnellement",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": ["partager", "découvrir", "voyager", "construire", "profiter de la vie", "courir ensemble"]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "37-45 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_RESIDENCE": ["France (IDF)", "pays limitrophes"],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "avec ou sans enfants",
#       "NUMBER_OF_CHILDREN": "2 maximum",
#       "QUALITIES": ["charmant", "confiance en soi", "attentionné", "conciliant", "ouvert au dialogue", "sportif"],
#       "VALUES": ["dialogue sans tabou"],
#       "DEFECTS": null,
#       "INTERESTS": ["sport/course"],
#       "HEIGHT": "au moins 1.77 m",
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "stable professionnellement",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": ["fonder ou élargir la famille", "courir ensemble"]
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "💚❤️💛 SPECIAL RECHERCHE NDOLO 100% KMER🇨🇲 VENANT DU CANADA 🇨🇦
#   Si vous aussi souhaitez faire passer une annonce spéciale Recherche Ndolo sur la page, cliquez sur ce lien pour demander les modalités: https://wa.me/+237696493067
#   Bonsoir warman merci pour le travail exceptionnel que vous faite dans la communauté camerounaise.
#   Je suis une dame âgée de 38 ans mère célibataire de 3 enfants de l'ouest Cameroun vivant au Canada.
#   Respectueuse,gentille,responsable et qui aime la vie.je suis travailleuse courageuse persévérante et je projette dans un avenir mon sens d'ecoute et d'auto critique m'aide à m'améliorer positivement sur tout les plans de ma vie.
#   jaimerais faire la rencontre d'un homme futur époux aimant responsable ayant des valeurs axée sur le respect la vérité l'amour la communication et les valeurs ancestrales.
#   jaime danser voyager faire des sorties en couple et en famille aller au cinéma soirée romantique .
#   mon coeur si tu es cet homme que je recherche honnête sincère travailleur vrai et ayant le sens de la famille âgée entre 40 et 55 ans, avec ou sans enfants, résident au Canada et pense avoir trouvé celle qu'il te faut alors communique avec moi c'est avec plaisir que je te lirait tu peux m'écrire a macheguianana@gmail.com
#   Si possible joindre des photos
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "38 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": ["Canada"],
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": "Ouest",
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "travailleuse",
#       "MARITAL_STATUS": "mère célibataire",
#       "HAS_CHILDREN": "Oui",
#       "NUMBER_OF_CHILDREN": "3 enfants",
#       "QUALITIES": [
#         "respectueuse",
#         "gentille",
#         "responsable",
#         "travailleuse",
#         "courageuse",
#         "persévérante",
#         "sens d'écoute",
#         "auto-critique"
#       ],
#       "VALUES": [
#         "respect",
#         "vérité",
#         "amour",
#         "communication",
#         "valeurs ancestrales",
#         "famille"
#       ],
#       "DEFECTS": null,
#       "INTERESTS": [
#         "danser",
#         "voyager",
#         "sorties en couple et famille",
#         "cinéma",
#         "soirées romantiques"
#       ],
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "travailleuse",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "sorties en couple et famille",
#         "cinéma",
#         "soirées romantiques"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "40-55 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_RESIDENCE": ["Canada"],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "avec ou sans enfants",
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": [
#         "honnête",
#         "sincère",
#         "travailleur",
#         "vrai",
#         "sens de la famille",
#         "aimant",
#         "responsable"
#       ],
#       "VALUES": [
#         "respect",
#         "vérité",
#         "amour",
#         "communication",
#         "valeurs ancestrales",
#         "famille"
#       ],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "futur époux",
#         "sens de la famille"
#       ]
#     }}
#   }}
  
  
#   Rules
# - Output **pure JSON** (no back-ticks, no comments).
# - Keys must appear exactly as in the template.
# - If a field is missing → use `null`.
# - Use double quotes for strings and arrays.
# - Arrays **must** be valid JSON lists, e.g. `["item1","item2"]`.
# - No trailing commas.

# Template to fill
# {{
#   "advertiser": {{
#     "NAME": null,
#     "RELIGION": null,
#     "AGE": "XX ans",
#     "SEX": "Homme|Femme",
#     "HEIGHT": "X.XX m",
#     "WEIGHT": "XX kg",
#     "COUNTRY_OF_RESIDENCE": ["Country"],
#     "COUNTRY_OF_ORIGIN": "Country",
#     "REGION_OF_ORIGIN": "Region",
#     "VILLAGE_OF_ORIGIN": null,
#     "SECTOR_OF_ACTIVITY": "Job|Sector",
#     "MARITAL_STATUS": "Status",
#     "HAS_CHILDREN": "Oui|Non",
#     "NUMBER_OF_CHILDREN": 0,
#     "QUALITIES": ["quality1","quality2"],
#     "VALUES": ["value1","value2"],
#     "DEFECTS": ["defect1","defect2"],
#     "INTERESTS": ["interest1","interest2"],
#     "PHYSICAL_APPEARANCE": "Description",
#     "ECONOMIC_SITUATION": "Description",
#     "EDUCATION_LEVEL": "Level",
#     "ILLNESS": null,
#     "RELATIONSHIP": ["goal1","goal2"]
#   }},
#   "desired": {{
#     "NAME": null,
#     "AGE": "XX ans",
#     "SEX": "Homme|Femme",
#     "HEIGHT": "X.XX m",
#     "WEIGHT": "XX kg",
#     "COUNTRY_OF_RESIDENCE": ["Country"],
#     "COUNTRY_OF_ORIGIN": "Country",
#     "REGION_OF_ORIGIN": "Region",
#     "VILLAGE_OF_ORIGIN": null,
#     "SECTOR_OF_ACTIVITY": "Job|Sector",
#     "MARITAL_STATUS": "Status",
#     "HAS_CHILDREN": "Oui|Non",
#     "NUMBER_OF_CHILDREN": 0,
#     "QUALITIES": ["quality1","quality2"],
#     "VALUES": ["value1","value2"],
#     "DEFECTS": ["defect1","defect2"],
#     "INTERESTS": ["interest1","interest2"],
#     "PHYSICAL_APPEARANCE": "Description",
#     "ECONOMIC_SITUATION": "Description",
#     "EDUCATION_LEVEL": "Level",
#     "ILLNESS": null,
#     "RELATIONSHIP": ["goal1","goal2"]
#   }}
# }}

#   IMPORTANT:
#   - Please provide the information in JSON format only. Do not include any introductory or concluding remarks, explanations, or additional text. The JSON object should contain the following keys: 'advertiser' and 'desired'.
#   - Réponds uniquement avec un objet JSON valide. 
#   - Pas de commentaires, pas de texte, pas de balises. 
#   - Toujours mettre null quand une info n’est pas donnée
#   Exemple : pas de poids → "WEIGHT": null.
#   Sinon ton validateur JSON interne plante avec "Missing required profile data".
#   - Éviter les formats ambigus
#   Âges → toujours "35 ans", "max 26 ans".
#   Taille → "1.80 m" (et pas "1m80").
#   Pays → en tableau : ["Cameroun"].
  
#   MAINTENANT, EXTRAIT LES INFORMATIONS DE CE TEXTE
  
#   {text_to_analyze}
  
#   JSON:"""

#   return prompt

# def sunday_rn_prompt(text_to_analyze):
#   prompt = f"""Tu es un expert en extraction d'informations structurées à partir d'annonces matrimoniales camerounaises.
  
#   INSTRUCTIONS:
#   - Extrait EXACTEMENT les informations demandées
#   - Sépare clairement Profile (annonceur) et Partner (recherché)
#   - Si une information n'existe pas → null
#   - Respecte les formats imposés
#   - Retourne UNIQUEMENT le JSON final
  
#   EXEMPLE D'EXTRACTION:
  
#   EXEMPLE D'ANNONCE:
#   "RESSE 8
#   Bonjour et merci au terre pour cette initiative.
#   Je suis une demoiselle de 25 ans, 1m80, 70kg originaire de l'ouest, étudiante, célibataire, sans enfants, vivant à Douala.
#   Je recherche mon partenaire de vie. Peu importe ou tu te trouves, tu dois juste être célibataire, Libre et sans enfants, propre, attentionné, respectueux, responsable, humble, aimant, doux, loyal, cultivé, jovial, fidèle et bienveillant. 
#   Aussi, tu dois être âgé entre 28 et 32 ans, avoir 1m85 et plus. Écris moi ici: partenairedevie1@gmail.com"
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "AGE": "25 ans",
#       "HEIGHT": "1.80 m",
#       "WEIGHT": "70 kg",
#       "LIVING_AT": "Douala",
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": "Ouest",
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "étudiante",
#       "MARITAL_STATUS": "célibataire",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "QUALITIES": [],
#       "VALUES": [],
#       "DEFECTS": null,
#       "INTERESTS": [],
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "étudiante",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": []
#     }},
#     "desired": {{
#       "AGE": "28-32 ans",
#       "HEIGHT": "au moins 1.85 m",
#       "WEIGHT": null,
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": "célibataire",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "QUALITIES": [
#         "propre",
#         "attentionné",
#         "respectueux",
#         "responsable",
#         "humble",
#         "aimant",
#         "doux",
#         "loyal",
#         "cultivé",
#         "jovial",
#         "fidèle",
#         "bienveillant"
#       ],
#       "VALUES": [],
#       "DEFECTS": null,
#       "INTERESTS": [],
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": []
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "RESSE 24
#   Salut le terre et au warman j suis une jeune et belle femme camerounaise âgée de 27ans mère d'une petite fillette d 5ans je suis du corps médical aide soignante d profession Fidel affectueuses comiques et j'adore cuisiner et faire du sport.
#   cherche un homme âgé d 30 à 55 ans attentionné , respectueux, sociable et Fidel vivent au Canada Angleterre ou allemand max 4 enfant"
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "27 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": "medecine",
#       "JOB": "aide-soignante",
#       "MARITAL_STATUS": "mère d'une petite fille de 5 ans",
#       "HAS_CHILDREN": "Oui",
#       "NUMBER_OF_CHILDREN": "1",
#       "QUALITIES": [
#         "Fidel",
#         "affectueuses",
#         "comiques"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": [
#         "cuisiner",
#         "faire du sport"
#       ],
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "aide-soignante",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "cuisiner",
#         "faire du sport"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "30-55 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "avec ou sans enfants",
#       "NUMBER_OF_CHILDREN": "max 4",
#       "QUALITIES": [
#         "attentionné",
#         "respectueux",
#         "sociable",
#         "Fidel"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": null
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "Bonjour warman, Merci pour ce que tu fais dans la communauté camerounaise.
#   Voilà je suis un homme de la trentaine, nouvellement affecté à\xa0 l'ouest j'ai 1.80m, teint noir, simple, calme, sans enfants , mon boulot me permet de gérer les factures.
#   Je recherche une femme sans enfants, minimum 1,65m , naturellement brune (étudiante finissante où travailleuse), ambitieuse, qui a fini de rêver et prête à s'engager, surtout respectueuse des valeurs africaines .
#   Si tu te reconnais dans cette description écris moi agneauagneau6@gmail.com 
#   Nb: qui réside de préférence à l'ouest."
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "AGE": "30-39 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": "Ouest",
#       "QUALITIES": [
#         "simple",
#         "calme"
#       ],
#       "VALUES": [
#         "respect des valeurs africaines"
#       ],
#       "HEIGHT": "1.80 m",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "ECONOMIC_SITUATION": ["il travaille", "il parvient à gerer ses factures"],
#       "PHYSICAL_APPEARANCE": ["teint noir"],
#     }},
#     "desired": {{
#       "SEX": "Femme",
#       "QUALITIES": [
#         "ambitieuse",
#         "respectueuse des valeurs africaines"
#       ],
#       "VALUES": [
#         "respect des valeurs africaines"
#       ],
#       "HEIGHT": "minimum 1.65 m",
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "PLACE_OF_RESIDENCE": [
#         "Ouest, Cameroon"
#       ],
#       "ECONOMIC_SITUATION": ["etudiant finissante ou travailleuse", "en fin d'etude"],
#       "PHYSICAL_APPEARANCE": ["naturellement brune"],
#     }},
#   }}
  
#   EXEMPLE D'ANNONCE:
#   "DJO 3
#   Bjr le terre, je suis un trentenaire résidant en France ayant une activité professionnelle et stable financièrement.
#   Je suis une personne calme, attentionnée et respectueuse prêt à s'engager.
#   Je suis à la recherche d'une femme Belle, authentique et séduisante âgé entre 26 et 30 ans vivant en France et sans enfant de préférence qui sait ce qu'elle veut, déjà prête à se poser, à bâtir une relation sur des bonnes bases.
#   Si tu te retrouve dans cette description n'hésites pas à m'écrire à diman.ndolo@gmail.com
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "30-39 ans",
#       "SEX": "Homme",
#       "COUNTRY_OF_RESIDENCE": [
#         "France"
#       ],
#       "COUNTRY_ORIGIN": null,
#       "REGION_ORIGIN": null,
#       "VILLAGE_ORIGIN": null,
#       "SECTOR_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "QUALITIES": [
#         "calme",
#         "attentionnée",
#         "respectueuse"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": "stable financièrement",
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "pret à s'engager",
#         "bâtir une relation sur des bonnes bases"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "26-30 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": [
#         "France"
#       ],
#       "COUNTRY_ORIGIN": null,
#       "REGION_ORIGIN": null,
#       "VILLAGE_ORIGIN": null,
#       "SECTOR_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "Non",
#       "NUMBER_OF_CHILDREN": 0,
#       "QUALITIES": [
#         "belle",
#         "authentique",
#         "séduisante"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "bâtir une relation sur des bonnes bases"
#       ]
#     }}
#   }}

#   EXEMPLE D'ANNONCE:
#   DJO 28
#   Bonjour le terre. Je suis un warboy de 28ans , physiquement 1,74 pour 70kg de teint chocolat. originaire de l'ouest. 
#   Je Boss dans le domaine Informatique dans une entreprise a Douala, et également très entreprenant. 
#   Je suis de nature Posé, très ouvert, blagueur et j'aime les calins. Je suis a la recherche d'une precieuse,qui viendra illuminé ma vie .
#   Elle devra être très belle physiquement avec de jolie courbe africaine,propre, coquette et attentionné, avoir des objectifs de vie claire et être ambitieuse. maxi 26ans.
#   Si cette description te parle, n'hésite pas... hope.loven2@gmail.com
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "28 ans",
#       "SEX": "Homme",
#       "HEIGHT": "1.74 m",
#       "WEIGHT": "70 kg",
#       "COUNTRY_OF_ORIGIN": "Cameroun",
#       "REGION_OF_ORIGIN": "Ouest",
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": ["Informatique, entreprise à Douala", "entrepreneur"],
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": null,
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": [
#         "Posé",
#         "très ouvert",
#         "blagueur",
#         "aime les calins"
#       ],
#       "VALUES": [
#         "beauté physique",
#         "propreté",
#         "style",
#         "ambition"
#       ],
#       "DEFECTS": null,
#       "INTERESTS": [
#         "technologie",
#         " entrepreneuriat",
#         "calins"
#       ],
#       "PHYSICAL_APPEARANCE": "teint chocolat",
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "améliorer la qualité de vie",
#         "construire une relation stable"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "jusqu'à 26 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": null,
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": [
#         "coquette",
#         "attentionnée",
#         "objectifs de vie clairs",
#         "ambitieuse"
#       ],
#       "VALUES": [
#         "beauté physique",
#         "propreté",
#         "style",
#         "ambition"
#       ],
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": ["très belle physiquement, jolie courbe africaine"],
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "améliorer la qualité de vie",
#         "construire une relation stable"
#       ],
#       "CONTACT_INFORMATION": "hope.loven2@gmail.com"
#     }}
#   }}
  
#   EXEMPLE D'ANNONCE:
#   Hello,I am a woman of 26 years old,1m69, 70 kg without children.
#   I work in an NGO in CAR as an expatriate.I am looking for a single man without children who works in NGO as an EXPATRIATE, more than 1m75, less than 35 years old, caring. 
#   I am looking for a man who wants to raise a woman to the rank of a queen, build a solid relationship and found a family in which there is joy, peace, fidelity and trust.
#   To you the apple of my eyes, if you recognize yourself in the description and you are looking for your precious stone with whom to spend your R&R, do not hesitate to write to me at the address: perlerare349@yahoo.com
  
#   JSON ATTENDU:
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "26 years old",
#       "SEX": "Woman",
#       "HEIGHT": "1.69 m",
#       "WEIGHT": "70 kg",
#       "COUNTRY_OF_ORIGIN": "Cameroon",
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "COUNTRY_OF_RESIDENCE": [
#         "CAR Central African Republic"
#       ],
#       "SECTOR_OF_ACTIVITY": ["NGO as expatriate"],
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "No",
#       "NUMBER_OF_CHILDREN": 0,
#       "QUALITIES": null,
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "joy", "peace", "fidelity" , "trust"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "less than 35 years old",
#       "SEX": "Man",
#       "HEIGHT": "more than 1.75m",
#       "WEIGHT": null,
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": ["NGO as expatriate"],
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": null,
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": [
#         "caring",
#         "raise a woman to the rank of a queen"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "joy", "peace", "fidelity" , "trust"
#       ]
#     }}
#   }}

#   EXEMPLE D'ANNONCE
#   Bonjour le terre.
#   Je viens ici pour rechercher ma pars de bonne femme ...
#   Je suis un homme de 52 ans 1.86, 90 kilos je vis en Île de France depuis des années, j'ai un enfant que j'aime bien et j'aimerais en avoir d'autres ,je suis calme et attentionné, 
#   je cherche une femme de 33 à 44 ans facile à vivre,\xa0 recherchant une relation sérieuse pouvant finir dans un bon mariage elle doit vivre en Île de France ou dans les environs car avec le travail et l'âge plus besoin des relations à distance. 
#   Si tu es intéressé et que tu aimerais me connaître, écris moi à cet adresse mail Lifenew654@yahoo.com

#   JSON ATTENDU
#   {{
#     "advertiser": {{
#       "NAME": null,
#       "RELIGION": null,
#       "AGE": "52 ans",
#       "SEX": "Homme",
#       "HEIGHT": "1.86 m",
#       "WEIGHT": "90 kg",
#       "COUNTRY_OF_RESIDENCE": [
#         "France", "Île-de-France"
#       ],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": "Oui",
#       "NUMBER_OF_CHILDREN": 1,
#       "QUALITIES": [
#         "calme",
#         "attentionné"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": ["travail"],
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "relation sérieuse",
#         "mariage"
#       ]
#     }},
#     "desired": {{
#       "NAME": null,
#       "AGE": "33-44 ans",
#       "SEX": "Femme",
#       "COUNTRY_OF_RESIDENCE": [
#         "France", "Île-de-France ou environs"
#       ],
#       "COUNTRY_OF_ORIGIN": null,
#       "REGION_OF_ORIGIN": null,
#       "VILLAGE_OF_ORIGIN": null,
#       "SECTOR_OF_ACTIVITY": null,
#       "MARITAL_STATUS": null,
#       "HAS_CHILDREN": null,
#       "NUMBER_OF_CHILDREN": null,
#       "QUALITIES": [
#         "facile à vivre"
#       ],
#       "VALUES": null,
#       "DEFECTS": null,
#       "INTERESTS": null,
#       "HEIGHT": null,
#       "WEIGHT": null,
#       "PHYSICAL_APPEARANCE": null,
#       "ECONOMIC_SITUATION": null,
#       "EDUCATION_LEVEL": null,
#       "ILLNESS": null,
#       "RELATIONSHIP": [
#         "relation sérieuse",
#         "mariage"
#       ]
#     }}
#   }}

#   Rules
# - Output **pure JSON** (no back-ticks, no comments).
# - Keys must appear exactly as in the template.
# - If a field is missing → use `null`.
# - Use double quotes for strings and arrays.
# - Arrays **must** be valid JSON lists, e.g. `["item1","item2"]`.
# - No trailing commas.

# Template to fill
# {{
#   "advertiser": {{
#     "NAME": null,
#     "AGE": "XX ans",
#     "SEX": "Homme|Femme",
#     "HEIGHT": "X.XX m",
#     "WEIGHT": "XX kg",
#     "COUNTRY_OF_RESIDENCE": ["Country"],
#     "COUNTRY_OF_ORIGIN": "Country",
#     "REGION_OF_ORIGIN": "Region",
#     "VILLAGE_OF_ORIGIN": null,
#     "SECTOR_OF_ACTIVITY": "Job|Sector",
#     "MARITAL_STATUS": "Status",
#     "HAS_CHILDREN": "Oui|Non",
#     "NUMBER_OF_CHILDREN": 0,
#     "QUALITIES": ["quality1","quality2"],
#     "VALUES": ["value1","value2"],
#     "DEFECTS": ["defect1","defect2"],
#     "INTERESTS": ["interest1","interest2"],
#     "PHYSICAL_APPEARANCE": "Description",
#     "ECONOMIC_SITUATION": "Description",
#     "EDUCATION_LEVEL": "Level",
#     "ILLNESS": null,
#     "RELATIONSHIP": ["goal1","goal2"]
#   }},
#   "desired": {{
#     "NAME": null,
#     "AGE": "XX ans",
#     "SEX": "Homme|Femme",
#     "HEIGHT": "X.XX m",
#     "WEIGHT": "XX kg",
#     "COUNTRY_OF_RESIDENCE": ["Country"],
#     "COUNTRY_OF_ORIGIN": "Country",
#     "REGION_OF_ORIGIN": "Region",
#     "VILLAGE_OF_ORIGIN": null,
#     "SECTOR_OF_ACTIVITY": "Job|Sector",
#     "MARITAL_STATUS": "Status",
#     "HAS_CHILDREN": "Oui|Non",
#     "NUMBER_OF_CHILDREN": 0,
#     "QUALITIES": ["quality1","quality2"],
#     "VALUES": ["value1","value2"],
#     "DEFECTS": ["defect1","defect2"],
#     "INTERESTS": ["interest1","interest2"],
#     "PHYSICAL_APPEARANCE": "Description",
#     "ECONOMIC_SITUATION": "Description",
#     "EDUCATION_LEVEL": "Level",
#     "ILLNESS": null,
#     "RELATIONSHIP": ["goal1","goal2"]
#   }}
# }}

#   IMPORTANT:
#   - "Please provide the information in JSON format only. Do not include any introductory or concluding remarks, explanations, or additional text. The JSON object should contain the following keys: 'advertiser' and 'desired'."
#   - Réponds uniquement avec un objet JSON valide. 
#   - Pas de commentaires, pas de texte, pas de balises. 
#   - Toujours mettre null quand une info n’est pas donnée
#   Exemple : pas de poids → "WEIGHT": null.
#   Sinon ton validateur JSON interne plante avec "Missing required profile data".
#   - Éviter les formats ambigus
#   Âges → toujours "35 ans", "max 26 ans".
#   Taille → "1.80 m" (et pas "1m80").
#   Pays → en tableau : ["Cameroun"].
  
#   MAINTENANT, EXTRAIT LES INFORMATIONS DE CE TEXTE
  
#   {text_to_analyze}
  
#   JSON:"""

#   return prompt
