# 1. Imports
# 2. Load data
# 3. Variables
# 4. Global cleaning helpers (functions)
# 5. Re-naming columns
# 6. Mappings
# 7. Multi-choice question processing
# 8. Column-by-column cleaning
# 9. Delete unnecessary Columns
# 10. Save CSV file

# 1. Imports
import pandas as pd
import re
import numpy as np


# 2. Load data
file_id = "1lfH64MX8NHuxn7745leZ6LaXRVLAAer77J336ZFOTIk"
gid = "1900938527"  # onglet cible
url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"

df = pd.read_csv(url)
df_clean = pd.DataFrame()

df_clean = df


# 3. Variables
MAX_CHOICES = 5
MAX_CHOICES_DIFF = 5


# 4. Global cleaning helpers (functions)
def normalize_text(s):
    if pd.isna(s): return s
    return (str(s)
            .strip()
            .lower()
            .replace("à", "a").replace("â", "a").replace("ä", "a")
            .replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")
            .replace("ï", "i").replace("î", "i")
            .replace("ô", "o")
            .replace("ù", "u").replace("û", "u").replace("ū", "u")
            .replace("ç", "c")
            .replace("$", "").replace("€", "").replace("-"," "))

def clean_age (age):
    if pd.isna(age):
        return None
    age = str(age).strip()
    if age.startswith("18"):
        return "18-24"
    elif age.startswith("25"):
        return "25-34"
    elif age.startswith("35"):
        return "35-44"
    elif age.startswith("45"):
        return "45-54"
    elif age.startswith("55"):
        return "55-64"
    elif age.startswith("65"):
        return "65 and over"
    else:
        return "18 and less"

def smart_split(val):
    if pd.isna(val):
        return[]
    s = str(val)
    parts = re.split(r',(?![^()]*\))', s)
    parts = [p.strip() for p in parts if p.strip()]
    return parts

def list_to_fixed_cols_prefs(lst, k=MAX_CHOICES):
    lst = (lst + [np.nan]*k) [:k]
    return pd.Series(lst, index=[f"most_wanted_pref_to_visit_{i+1}" for i in range(k)])

def list_to_fixed_cols_japan_diffs(lst, k=MAX_CHOICES_DIFF):
    lst = (lst + [np.nan]*k) [:k]
    return pd.Series(lst, index=[f"Japan_most_difficulties_{i+1}" for i in range(k)])

def list_to_fixed_cols_alt_diffs(lst, k=MAX_CHOICES_DIFF):
    lst = (lst + [np.nan]*k) [:k]
    return pd.Series(lst, index=[f"alt_dest_most_difficulties_{i+1}" for i in range(k)])


# 5. Renaming columns
df_clean = df_clean.rename(columns={
    "Quel est votre nationalité?": "nationality",
    "  Dans quel pays résidez-vous actuellement ?  ": "country",
    "Quelle est votre tranche d’âge ?  ": "age_group",
    "Quelle est votre situation familiale ? ": "family_situation",
    "Quelle est votre tranche de revenus mensuels nets du foyer ? ": "household_income_in_€",
    "À quelle fréquence voyagez vous à l’étranger (hors Europe) ?  ": "travel_frequency",
    "Avez-vous déjà voyagé au Japon ?  ": "been_to_Japan",
    "Quelle durée de séjour avez-vous prévue ?  ": "Japan_vac_duration",
    "Quelles régions du Japon vous intéressent le plus ? (Choisissez 3 max.)  ": "most_wanted_pref_to_visit",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Découverte de la culture et de l’histoire (temples, traditions, samouraïs, geishas, etc.)]": "rating_interest_culture_and_history",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Gastronomie japonaise (sushis, ramen, wagyu, street food, etc.)]": "rating_interest_food",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Paysages naturels et randonnées (montagnes, volcans, cerisiers en fleurs, etc.)]": "rating_interest_nature_hiking",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Technologie, innovation et shopping (Tokyo high-tech, Akihabara, mode, etc.)]": "rating_interest_shopping_and_techno",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Festivals et événements (matsuri, concerts, sport, sumo, etc.)]": "rating_interest_events_and_festivals",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Bien-être (onsen, ryokan, détente)]": "rating_interest_wellness",
    "À quel point ces motivations influencent elles votre envie de voyager au Japon ? [Parc d'attraction (Disneyland, Universal...)]": "rating_interest_theme_park",
    "Quel budget global prévoyez vous pour un voyage au Japon (par personne et par semaine , hors vol international ) ?  ": "Japan_budget_per_week",
    "Parmi les types d’hébergement suivants, lequel correspond le mieux à vos préférences principales pour un séjour au Japon ? ": "Japan_prefered_accomodation",
    "Quels sont les principaux freins ou difficultés que vous rencontrez (ou pourriez rencontrer) lors d’un voyage au Japon ? (Choisissez 3 max.)  ": "Japan_most_difficulties",
    "Si vous ne pouviez pas voyager au Japon, quelle destination alternative choisiriez-vous ?": "alternative_destination",
    "Quelle a été la principale raison pour laquelle vous auriez choisi cette destination plutôt que le Japon ? ": "alt_dest_main_reason",
    "Parmi les types d’hébergement suivants, lequel correspond le mieux à vos préférences principales lors de vos voyages dans d’autres pays (hors Japon)   ? ": "alt_dest_prefered_accomodation",
    "Lors de vos voyages dans d’autres pays (hors Japon), quel est votre budget moyen par semaine et par personne , hors vol international ?  ": "alt_dest_budget_per_week",
    "Lors de vos voyages dans d’autres pays (hors Japon), quel(s) mode(s) de transport utilisez-vous le plus souvent ?": "alt_dest_transportation",
    "Comment préparez-vous vos voyages en général ? (Multiple choix possible)": "trip_prep",
    "Quel canal utilisez-vous le plus pour réserver vos voyages ?  ": "booking_trip_channel",
    "Parmi les éléments suivants, lequel influence le plus votre choix de destination de vacances (hors Japon) ? ": "most_influencial_reason_to_choose_dest",
    "Lorsque vous voyagez en dehors du Japon, quelles sont les principales difficultés que vous rencontrez habituellement ?\n(Choisissez jusqu’à 3 réponses)": "alt_dest_most_difficulties",
    "Qu’est-ce qui rendrait le Japon plus attractif comme destination pour vous ?  ": "recomendation_to_improve_attractiveness"
})


# 6. Mappings
# Country + Origins (normalize_text)
mapping = {
    #France
    "france": "France",
    "francais": "France",
    "francaise": "France",
    "french": "France",
    "法国": "France",
    "fucking french": "France",

    #China
    "chine": "China",
    "chinoise": "China",
    "chinois": "China",
    "中国": "China",
    "chinese": "China",

    #Taiwan
    "taiwan": "Taiwan",
    "taiwanais": "Taiwan",
    "taiwanaise": "Taiwan",

    #Vietnam
    "vietnam": "Vietnam",
    "vietnamien": "Vietnam",
    "vietnamienne": "Vietnam",

    #Portugal
    "portuguese": "Portugal",

    #Israel
    "israel": "Israel",
    "israelien": "Israel",
    "israelienne": "Israel",

    #Spain
    "espagne": "Spain",

    #Germany
    "allemagne": "Germany",

    #USA
    "united states of america my friend": "USA",
}

# family_situation
family_situation_map = {
    
    "Single": "Single",
    "Célibataire": "Single",

    "En couple sans enfant": "Relationship_no_kids",
    "In a relationship, no children": "Relationship_no_kids",

    "En couple avec enfant(s)": "Relationship_with_kids",
    "In a relationship, with children": "Relationship_with_kids",

    "Marié(e)/Pacsé(e) sans enfant": "Married_no_kids",
    "Married / in a civil partnership, no children": "Married_no_kids",

    "Marié(e)/Pacsé(e) avec enfant(s)": "Married_with_kids",
    "Married / in a civil partnership, with children": "Married_with_kids",

    "Préfère ne pas répondre": "Unknown",
    "Prefer not to say": "Unknown"
}

# household_income_in_€
clean_income = {
    
    "Moins de 1 500 €": "1500 and less",
    "Less than $1,700 (~€1,500)": "1500 and less",

    "1 500 – 1 999 €": "1500-1999",
    "$1,700 – $2,200 (~€1,500 – €1,999)": "1500-1999",

    "2 000 – 2 499 €": "2000-2499",
    "$2,200 – $2,700 (~€2,000 – €2,499)": "2000-2499",

    "2 500 – 2 999 €": "2500-2999",
    "$2,800 – $3,300 (~€2,500 – €2,999)": "2500-2999",

    "3 000 – 3 999 €": "3000-3999",
    "$3,400 – $4,400 (~€3,000 – €3,999)": "3000-3999",

    "4 000 – 4 999 €": "4000–4999",
    "$4,500 – $5,500 (~€4,000 – €4,999)": "4000–4999",

    "5000 – 5 999 €": "5000–5999",
    "$5,600 – $6,600 (~€5,000 – €5,999)": "5000–5999",

    "6 000 – 6 999 €": "6000–6999",
    "$6,700 – $7,700 (~€6,000 – €6,999)": "6000–6999",

    "Supérieur à 7 000 €": "7000 and more",
    "More than $7,800 (~€7,000+)": "7000 and more",

    "Préfère ne pas répondre": "Unknown",
    "Prefer not to say": "Unknown",
}

# travel_frequency 
clean_travel_frequency = {
    
    "Jamais": "Never",
    "Une fois tous les 5 ans ou plus": "Once every 5 years or more",
    "Tous les 2-3 ans": "Every 2–3 years",
    "Une fois par an": "Once a year",
    "Plusieurs fois par an": "Several times a year",
}

# been_to_Japan 
clean_been_to_japan = {

    "Oui, une fois": "Yes, once",
    "Oui, plusieurs fois": "Yes, several times",
    "Non, mais j’aimerais y aller": "No, but I would like to go",
    "Non, et je ne suis pas intéressé": "No, and I’m not interested",
}

# Japan_vac_duration
clean_Japan_vac_duration = {
    
    "1 semaine": "1 week",
    "2 semaines": "2 weeks",
    "3 semaines": "3 weeks",
    "4 semaines": "4 weeks",
    "Plus de 4 semaines": "More than 4 weeks",
    "Je ne sais pas / Pas assez renseigné": "I don’t know yet / Not sure"
}

# most_wanted_pref_to_visit_* 
clean_most_wanted_pref_to_visit = {
    
    "Tokyo et sa région (Kanto)": "Kanto",
    "Tokyo and its region (Kanto)": "Kanto",

    "Kyoto / Osaka / Nara (Kansai)": "Kansai",

    "Région du Tohoku (ex. Yamagata, Sendai)": "Tohoku",
    "Tohoku region (e.g. Yamagata, Sendai)": "Tohoku",

    "Chūgoku (Hiroshima, Miyajima, Okayama, Matsue)": "Chūgoku",

    "Shikoku (île du pèlerinage des 88 temples, Matsuyama, Iya Valley)": "Shikoku",
    "Shikoku (88 Temple Pilgrimage Island, Matsuyama, Iya Valley)": "Shikoku",

    "Chūbu (Nagoya, Alpes japonaises, Kanazawa, Takayama, Mont Fuji côté Yamanashi/Shizuoka)": "Chūbu",
    "Chubu (Nagoya, Japanese Alps, Kanazawa, Takayama, Mt. Fuji – Yamanashi/Shizuoka side)": "Chūbu",

    "Hokkaido": "Hokkaido",
    "Okinawa": "Okinawa",

    "Kyushu (Fukuoka, Nagasaki, Beppu)": "Kyushu",

    "Je n’ai pas encore d’idée précise, j’ai besoin d’y réfléchir ou de me renseigner.": "Unknown",
    "j’ai besoin d’y réfléchir ou de me renseigner.": None,
    "Je n’ai pas encore d’idée précise": None,
    "I don’t have a clear idea yet / I need to think or find out more": "Unknown",
}

#rating_interest_*
clean_rating_japan = {

    "Pas du tout important": "Not important at all",
    "Peu important": "Slightly important",
    "Assez important": "Moderately important",
    "Très important": "Very important",
    "Essentiel": "Essential",
}

# Japan_budget_per_week 
clean_budget_japan = {

    "Moins de 500 €": "Less than 500",
    "Less than $550 (~€500)": "Less than 500",

    "500 – 1 000 €": "500-1000",
    "$550 – $1,100 (~€500 – €1,000)": "500-1000",

    "1 000 – 1 500 €": "1000-1500",
    "$1,100 – $1,650 (~€1,000 – €1,500)": "1000-1500",

    "1 500 – 2 500 €": "1500-2500",
    "$1,650 – $2,750 (~€1,500 – €2,500)": "1500-2500",

    "Plus de 2 500 €": "More than 2500",
    "More than $2,750 (~€2,500+)": "More than 2500",

    "Je ne sais pas / Pas assez renseigné": "Unknown",
    "I don’t know / Not sure yet": "Unknown",
}

#Japan_prefered_accomodation (normalize_text) 
clean_japan_accomodation = {

    "hotel classique (3 4 etoiles)": "Standard hotel (3–4 stars)",
    "hotel haut de gamme / luxe (5 etoiles)": "Luxury / high-end hotel (5 stars)",
    "ryokan (auberge traditionnelle)": "Ryokan (traditional Japanese inn)",
    "capsule hotel": "Capsule hotel",
    "airbnb / logement chez l’habitant": "Airbnb / homestay",
    "hostel/ auberge de jeunesse": "Hostel"
}

# Japan_most_difficulties_* (normalize_text) 
clean_most_difficulties = {
    
    "la barriere de la langue": "Language",
    "the language barrier": "Language",
    
    "les difficultes liees aux transports (train, navigation, reservations)": "Transportation",
    "difficulties with transportation (trains, navigation, reservations)": "Transportation",

    "les problemes lies a la location de voiture (permis international, conduite a gauche, etc.)": "Car rental",
    "problems with car rental (international license, driving on the left, etc.)": "Car rental",
    
    "le cout de la vie sur place (hebergement, restauration, activites)": "Expensive",
    "the cost of living (accommodation, food, activities)": "Expensive",
    "expensive": "Expensive",

    "l’affluence touristique (lieux bondes, files d’attente)": "Crowded/Popularity",
    "tourist crowds (busy places, long queues)": "Crowded/Popularity",

    "le manque d’information touristique en francais/anglais": "Translation",
    "lack of tourist information in english or french": "Translation",

    "没兴趣": None,
    "catastrophe naturelle": "Disaster",
    "c'est la destination trop a la mode que tout le monde veut faire. je prefere les destinations qui sortent du lot.": "Crowded/Popularity",
    "les insupportables fans du japon": "Crowded/Popularity"
}

# alternative_destination (normalize_text)
clean_alternative_destination = {
    
    "coree du sud": "South Korea",
    "south korea": "South Korea",

    "chine": "China",
    "china": "China",

    "thailande": "Thailand",

    "vietnam": "Vietnam",

    "autres pays d’asie": "Asia",
    "other asian countries": "Asia",
    "asia": "Asia",

    "usa / canada": "USA / Canada",
    "usa": "USA / Canada",
    "canada": "USA / Canada",

    "europe": "Europe",
}

# alt_dest_main_reason (normalize_text) 
clean_alt_dest_reason = {
    
    # Cost
    "moins cher": "Cost",
    "cheaper": "Cost",

    # Distance / Convenience
    "plus proche": "Convenience",
    "plus pratique": "Convenience",

    # Familiarity
    "deja familier": "Familiarity",
    "already familiar with the destination": "Familiarity",

    # Social Influence
    "influence des amis/de la famille": "Social",
    "influence from friends or family": "Social",

    # Nature / landscapes
    "l'asie en general m'attire enormement et j'ai vu dans des reportages des endroits de chine merveilleux que j'aimerais decouvrir !": "Nature",
    "pour l'histoire, les paysages,...": "Nature",
    "paysages": "Nature",
    "grands espaces": "Nature",

    # Cultural interest
    "drama et k pop": "Cultural",
    "k pop": "Cultural",
    "kpop": "Cultural",
    "plus d'interet personnelle, moins touristique et plus singulier": "Cultural",

    # No specific reason
    "grand interet": "None",
    "没兴趣": "None",
    "aucune": "None",
    "pas trop de raisons particulieres si ce n'est qu'ils sont cousins francais :)": "None",
}

#alt_dest_prefered_accomodation (normalize_text) 
clean_alt_pref_accomodation = {
    
    "hotel classique (3 4 etoiles)": "Standard hotel (3–4 stars)",
    "hotel haut de gamme / luxe (5 etoiles)": "Luxury / high-end hotel (5 stars)",
    "location type airbnb / appartement": "Airbnb-style rental / apartment",
    "auberge de jeunesse": "Hostel",
    "resort / club vacances": "Resort / holiday club",
}

# alt_dest_transportation (normalize_text) 
clean_alt_dest_transport = {

    "transport en commun (bus, metro, train)": "Public transportation",
    "public transportation (bus, subway, train)": "Public transportation",

    "voiture de location": "Rental",
    "rental car": "Rental",

    "taxi / vtc (uber, grab…)": "Taxi",
    "taxi / ride hailing service (uber, grab, etc.)": "Taxi",

    "bus touristiques / circuits organises": "Organized tours",
    "tourist buses / organized tours": "Organized tours",
}

# trip_prep 
clean_trip_prep = {
    
    "Agence de voyages": "Agency",
    "Travel agency": "Agency",

    "Sites spécialisés (Voyageurs du Monde, Comptoir des Voyages…)": "Websites",
    "Specialized travel websites (e.g. Audley Travel, Intrepid Travel, Responsible Travel, etc.)": "Websites",

    "Réseaux sociaux / influenceurs": "Influencers",
    "Social media / influencers": "Influencers",

    "Blogs de voyage": "Blogs",
    "Travel blogs": "Blogs",

    "Guides papier (Lonely Planet, Routard…)": "Books",
    "Printed travel guides (e.g. Lonely Planet, Routard, etc.)": "Books",

    "Bouche-à-oreille / amis": "Social",
    "Word of mouth / friends": "Social",
}

# most_influencial_reason_to_choose_dest (normalize_text)
clean_most_influencial_reason_to_choose_dest = {
    
    "decouvrir la nature et les paysages": "Nature",
    "discovering nature and landscapes": "Nature",

    "profiter de la plage et du climat": "Beaches",
    "enjoying the beach and the climate": "Beaches",

    "explorer le patrimoine culturel et historique (monuments, musees…)": "Cultural",
    "exploring cultural and historical heritage (monuments, museums, etc.)": "Cultural",

    "decouvrir la gastronomie locale": "Food",
    "discovering local gastronomy": "Food",

    "vivre une experience unique ou depaysante": "Uniqueness",
    "experiencing something unique or different": "Uniqueness",

    "rejoindre des proches (famille, amis)": "Family",
    "visiting relatives or friends": "Family",

    "se detendre / se ressourcer": "Relaxing",
    "relaxing / recharging": "Relaxing",
}

# booking_trip_channel (normalize_text) 
clean_booking_trip_channel = {
    
    "agence en ligne (ex. expedia, booking.com)": "Online agency",
    "online travel agency (e.g. expedia, booking.com)": "Online agency",

    "site officiel de compagnies aeriennes ou hotels": "Direct",
    "official airline or hotel website": "Direct",

    "agence de voyages physique": "Store",
    "physical travel agency": "Store",

    "plateformes collaboratives (airbnb, etc.)": "Platforms",
    "collaborative platforms (e.g. airbnb, etc.)": "Platforms",
}

# alt_dest_most_difficulties_* (normalize_text)
clean_alt_dest_most_difficulties = {
    
    "barriere de la langue": "Language",
    "language barrier": "Language",

    "difficultes avec les transports (train, navigation, reservations)": "Transportation",
    "transportation issues (train, navigation, reservations)": "Transportation",
    "combiner toutes les activites avec les lieux d hebergement": "Transportation",

    "problemes lies a la location de voiture (permis international, conduite a gauche, etc.)": "Car rental",
    "car rental problems (international license, driving on the left, etc.)": "Car rental",

    "cout de la vie (hebergement, nourriture, activites)": "Expensive",
    "cost of living (accommodation, food, activities)": "Expensive",

    "foule touristique (sites bondes, files d’attente)": "Crowded",
    "tourist crowds (busy sites, long queues)": "Crowded",
    "les autres voyageurs": "Crowded",

    "manque d’informations touristiques en anglais": "Translation",
    "lack of tourist information in english": "Translation",

    "没兴趣": "None",
    "la meme": "None",
    "adaptation a la nourriture locale": "Food",
}



# 7. Multi-choice question processing
regions_list = df_clean["most_wanted_pref_to_visit"].apply(smart_split)
df_prefs = regions_list.apply(list_to_fixed_cols_prefs)
df_clean = pd.concat([df_clean, df_prefs], axis=1)

diffs_list = df_clean["Japan_most_difficulties"].apply(smart_split)
df_diffs = diffs_list.apply(list_to_fixed_cols_japan_diffs)
df_clean = pd.concat([df_clean, df_diffs], axis=1)

alt_dest_diff_list = df_clean["alt_dest_most_difficulties"].apply(smart_split)
df_alt_dest_diff_list = alt_dest_diff_list.apply(list_to_fixed_cols_alt_diffs)
df_clean = pd.concat([df_clean, df_alt_dest_diff_list], axis=1)


# 8. Column-by-column cleaning
df_clean["nationality"] = (df_clean["nationality"]
                               .map(normalize_text)
                               .map(mapping)
                               .fillna(df_clean["nationality"]))
    
df_clean["country"] = (df_clean["country"]
                               .map(normalize_text)
                               .map(mapping)
                               .fillna(df_clean["country"]))
    
df_clean["age_group"] = df_clean["age_group"].apply(clean_age)

df_clean["family_situation"] = (df_clean["family_situation"]
                            .map(family_situation_map)
                            .fillna(df_clean["family_situation"]))

df_clean["household_income_in_€"] = (df_clean["household_income_in_€"]
                            .map(clean_income)
                            .fillna(df_clean["household_income_in_€"]))

df_clean["travel_frequency"] = (df_clean["travel_frequency"]
                            .map(clean_travel_frequency)
                            .fillna(df_clean["travel_frequency"]))

df_clean["been_to_Japan"] = (df_clean["been_to_Japan"]
                            .map(clean_been_to_japan)
                            .fillna(df_clean["been_to_Japan"]))

df_clean["Japan_vac_duration"] = (df_clean["Japan_vac_duration"]
                            .map(clean_Japan_vac_duration)
                            .fillna(df_clean["Japan_vac_duration"]))

pref_cols = ["most_wanted_pref_to_visit_1", "most_wanted_pref_to_visit_2", "most_wanted_pref_to_visit_3",
        "most_wanted_pref_to_visit_4", "most_wanted_pref_to_visit_5"]
df_clean[pref_cols] = (df_clean[pref_cols]
                            .map(lambda x: clean_most_wanted_pref_to_visit.get(x, x)))

rating_cols = ['rating_interest_culture_and_history', 'rating_interest_food',
       'rating_interest_nature_hiking', 'rating_interest_shopping_and_techno',
       'rating_interest_events_and_festivals', 'rating_interest_wellness',
       'rating_interest_theme_park']
df_clean[rating_cols] = (df_clean[rating_cols]
                            .map(lambda x: clean_rating_japan.get(x, x)))

df_clean["Japan_budget_per_week"] = (df_clean["Japan_budget_per_week"]
                            .map(clean_budget_japan)
                            .fillna(df_clean["Japan_budget_per_week"]))

df_clean["Japan_prefered_accomodation"] = (df_clean["Japan_prefered_accomodation"]
                                           .map(normalize_text)
                                           .map(clean_japan_accomodation)
                                           .fillna(df_clean["Japan_prefered_accomodation"]))

cols = ["Japan_most_difficulties_1", "Japan_most_difficulties_2", "Japan_most_difficulties_3",
        "Japan_most_difficulties_4", "Japan_most_difficulties_5"]
df_clean[cols] = (df_clean[cols]
                            .map(normalize_text)
                            .map(lambda x: clean_most_difficulties.get(x, x)))

df_clean["alternative_destination"] = (df_clean["alternative_destination"]
                            .map(normalize_text)
                            .map(clean_alternative_destination)
                            .fillna(df_clean["alternative_destination"]))

df_clean["alt_dest_main_reason"] = (df_clean["alt_dest_main_reason"]
                            .map(normalize_text)
                            .map(clean_alt_dest_reason)
                            .fillna(df_clean["alt_dest_main_reason"]))

df_clean["alt_dest_prefered_accomodation"] = (df_clean["alt_dest_prefered_accomodation"]
                            .map(normalize_text)
                            .map(clean_alt_pref_accomodation)
                            .fillna(df_clean["alt_dest_prefered_accomodation"]))

df_clean["alt_dest_budget_per_week"] = (df_clean["alt_dest_budget_per_week"]
                            .map(clean_budget_japan)
                            .fillna(df_clean["alt_dest_budget_per_week"]))

df_clean["alt_dest_transportation"] = (df_clean["alt_dest_transportation"]
                                       .map(normalize_text)
                                       .map(clean_alt_dest_transport)
                                       .fillna(df_clean["alt_dest_transportation"]))

df_clean["trip_prep"] = (df_clean["trip_prep"]
                            .map(clean_trip_prep)
                            .fillna(df_clean["trip_prep"]))

df_clean["booking_trip_channel"] = (df_clean["booking_trip_channel"]
                            .map(normalize_text)
                            .map(clean_booking_trip_channel)
                            .fillna(df_clean["booking_trip_channel"]))

df_clean["most_influencial_reason_to_choose_dest"] = (df_clean["most_influencial_reason_to_choose_dest"]
                            .map(normalize_text)
                            .map(clean_most_influencial_reason_to_choose_dest)
                            .fillna(df_clean["most_influencial_reason_to_choose_dest"]))

cols = ["alt_dest_most_difficulties_1", "alt_dest_most_difficulties_2", "alt_dest_most_difficulties_3",
        "alt_dest_most_difficulties_4", "alt_dest_most_difficulties_5"]
df_clean[cols] = (df_clean[cols]
                            .map(normalize_text)
                            .map(lambda x: clean_alt_dest_most_difficulties.get(x, x)))


# 9. Delete unnecessary Columns
df_clean = df_clean.drop(columns= ["most_wanted_pref_to_visit", "Japan_most_difficulties", "alt_dest_most_difficulties"])


# 10. Save CSV file
df_clean.to_csv("data_processed/df_clean.csv", index=False)