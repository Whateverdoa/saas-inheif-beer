"""
EU Language Support for Beer Labels
Covers all 24 official EU languages for compliance labeling
"""

from enum import Enum
from pydantic import BaseModel


class EULanguage(str, Enum):
    """Official EU languages"""
    BG = "bg"  # Bulgarian
    CS = "cs"  # Czech
    DA = "da"  # Danish
    DE = "de"  # German
    EL = "el"  # Greek
    EN = "en"  # English
    ES = "es"  # Spanish
    ET = "et"  # Estonian
    FI = "fi"  # Finnish
    FR = "fr"  # French
    GA = "ga"  # Irish
    HR = "hr"  # Croatian
    HU = "hu"  # Hungarian
    IT = "it"  # Italian
    LT = "lt"  # Lithuanian
    LV = "lv"  # Latvian
    MT = "mt"  # Maltese
    NL = "nl"  # Dutch
    PL = "pl"  # Polish
    PT = "pt"  # Portuguese
    RO = "ro"  # Romanian
    SK = "sk"  # Slovak
    SL = "sl"  # Slovenian
    SV = "sv"  # Swedish


LANGUAGE_NAMES = {
    EULanguage.BG: {"native": "Български", "english": "Bulgarian"},
    EULanguage.CS: {"native": "Čeština", "english": "Czech"},
    EULanguage.DA: {"native": "Dansk", "english": "Danish"},
    EULanguage.DE: {"native": "Deutsch", "english": "German"},
    EULanguage.EL: {"native": "Ελληνικά", "english": "Greek"},
    EULanguage.EN: {"native": "English", "english": "English"},
    EULanguage.ES: {"native": "Español", "english": "Spanish"},
    EULanguage.ET: {"native": "Eesti", "english": "Estonian"},
    EULanguage.FI: {"native": "Suomi", "english": "Finnish"},
    EULanguage.FR: {"native": "Français", "english": "French"},
    EULanguage.GA: {"native": "Gaeilge", "english": "Irish"},
    EULanguage.HR: {"native": "Hrvatski", "english": "Croatian"},
    EULanguage.HU: {"native": "Magyar", "english": "Hungarian"},
    EULanguage.IT: {"native": "Italiano", "english": "Italian"},
    EULanguage.LT: {"native": "Lietuvių", "english": "Lithuanian"},
    EULanguage.LV: {"native": "Latviešu", "english": "Latvian"},
    EULanguage.MT: {"native": "Malti", "english": "Maltese"},
    EULanguage.NL: {"native": "Nederlands", "english": "Dutch"},
    EULanguage.PL: {"native": "Polski", "english": "Polish"},
    EULanguage.PT: {"native": "Português", "english": "Portuguese"},
    EULanguage.RO: {"native": "Română", "english": "Romanian"},
    EULanguage.SK: {"native": "Slovenčina", "english": "Slovak"},
    EULanguage.SL: {"native": "Slovenščina", "english": "Slovenian"},
    EULanguage.SV: {"native": "Svenska", "english": "Swedish"},
}


# Compliance label translations
LABEL_TRANSLATIONS = {
    "ingredients": {
        EULanguage.BG: "Съставки",
        EULanguage.CS: "Složení",
        EULanguage.DA: "Ingredienser",
        EULanguage.DE: "Zutaten",
        EULanguage.EL: "Συστατικά",
        EULanguage.EN: "Ingredients",
        EULanguage.ES: "Ingredientes",
        EULanguage.ET: "Koostisosad",
        EULanguage.FI: "Ainesosat",
        EULanguage.FR: "Ingrédients",
        EULanguage.GA: "Comhábhair",
        EULanguage.HR: "Sastojci",
        EULanguage.HU: "Összetevők",
        EULanguage.IT: "Ingredienti",
        EULanguage.LT: "Sudėtis",
        EULanguage.LV: "Sastāvdaļas",
        EULanguage.MT: "Ingredjenti",
        EULanguage.NL: "Ingrediënten",
        EULanguage.PL: "Składniki",
        EULanguage.PT: "Ingredientes",
        EULanguage.RO: "Ingrediente",
        EULanguage.SK: "Zloženie",
        EULanguage.SL: "Sestavine",
        EULanguage.SV: "Ingredienser",
    },
    "contains": {
        EULanguage.BG: "Съдържа",
        EULanguage.CS: "Obsahuje",
        EULanguage.DA: "Indeholder",
        EULanguage.DE: "Enthält",
        EULanguage.EL: "Περιέχει",
        EULanguage.EN: "Contains",
        EULanguage.ES: "Contiene",
        EULanguage.ET: "Sisaldab",
        EULanguage.FI: "Sisältää",
        EULanguage.FR: "Contient",
        EULanguage.GA: "Tá ann",
        EULanguage.HR: "Sadrži",
        EULanguage.HU: "Tartalmaz",
        EULanguage.IT: "Contiene",
        EULanguage.LT: "Sudėtyje yra",
        EULanguage.LV: "Satur",
        EULanguage.MT: "Fih",
        EULanguage.NL: "Bevat",
        EULanguage.PL: "Zawiera",
        EULanguage.PT: "Contém",
        EULanguage.RO: "Conține",
        EULanguage.SK: "Obsahuje",
        EULanguage.SL: "Vsebuje",
        EULanguage.SV: "Innehåller",
    },
    "alcohol_by_volume": {
        EULanguage.BG: "Алкохолно съдържание",
        EULanguage.CS: "Obsah alkoholu",
        EULanguage.DA: "Alkoholindhold",
        EULanguage.DE: "Alkoholgehalt",
        EULanguage.EL: "Περιεκτικότητα σε αλκοόλ",
        EULanguage.EN: "Alcohol by volume",
        EULanguage.ES: "Contenido de alcohol",
        EULanguage.ET: "Alkoholisisaldus",
        EULanguage.FI: "Alkoholipitoisuus",
        EULanguage.FR: "Titre alcoométrique",
        EULanguage.GA: "Alcól de réir toirte",
        EULanguage.HR: "Udio alkohola",
        EULanguage.HU: "Alkoholtartalom",
        EULanguage.IT: "Titolo alcolometrico",
        EULanguage.LT: "Alkoholio kiekis",
        EULanguage.LV: "Spirta tilpumkoncentrācija",
        EULanguage.MT: "Alkoħol skont il-volum",
        EULanguage.NL: "Alcoholgehalte",
        EULanguage.PL: "Zawartość alkoholu",
        EULanguage.PT: "Teor alcoólico",
        EULanguage.RO: "Concentrație alcoolică",
        EULanguage.SK: "Obsah alkoholu",
        EULanguage.SL: "Vsebnost alkohola",
        EULanguage.SV: "Alkoholhalt",
    },
    "best_before": {
        EULanguage.BG: "Най-добър до",
        EULanguage.CS: "Minimální trvanlivost do",
        EULanguage.DA: "Bedst før",
        EULanguage.DE: "Mindestens haltbar bis",
        EULanguage.EL: "Ανάλωση κατά προτίμηση πριν από",
        EULanguage.EN: "Best before",
        EULanguage.ES: "Consumir preferentemente antes de",
        EULanguage.ET: "Parim enne",
        EULanguage.FI: "Parasta ennen",
        EULanguage.FR: "À consommer de préférence avant",
        EULanguage.GA: "Is fearr roimh",
        EULanguage.HR: "Najbolje upotrijebiti do",
        EULanguage.HU: "Minőségét megőrzi",
        EULanguage.IT: "Da consumarsi preferibilmente entro",
        EULanguage.LT: "Geriausias iki",
        EULanguage.LV: "Ieteicams līdz",
        EULanguage.MT: "Preferibbilment jintuża sa",
        EULanguage.NL: "Ten minste houdbaar tot",
        EULanguage.PL: "Najlepiej spożyć przed",
        EULanguage.PT: "Consumir de preferência antes de",
        EULanguage.RO: "A se consuma de preferință înainte de",
        EULanguage.SK: "Minimálna trvanlivosť do",
        EULanguage.SL: "Uporabno najmanj do",
        EULanguage.SV: "Bäst före",
    },
    "nutritional_info": {
        EULanguage.BG: "Хранителна информация",
        EULanguage.CS: "Výživové údaje",
        EULanguage.DA: "Næringsindhold",
        EULanguage.DE: "Nährwertangaben",
        EULanguage.EL: "Διατροφικές πληροφορίες",
        EULanguage.EN: "Nutritional information",
        EULanguage.ES: "Información nutricional",
        EULanguage.ET: "Toitumisalane teave",
        EULanguage.FI: "Ravintosisältö",
        EULanguage.FR: "Informations nutritionnelles",
        EULanguage.GA: "Faisnéis chothaithe",
        EULanguage.HR: "Nutritivne informacije",
        EULanguage.HU: "Tápértékek",
        EULanguage.IT: "Informazioni nutrizionali",
        EULanguage.LT: "Maistinė vertė",
        EULanguage.LV: "Uzturvērtība",
        EULanguage.MT: "Informazzjoni dwar in-nutrizzjoni",
        EULanguage.NL: "Voedingswaarde",
        EULanguage.PL: "Wartość odżywcza",
        EULanguage.PT: "Informação nutricional",
        EULanguage.RO: "Informații nutriționale",
        EULanguage.SK: "Výživové údaje",
        EULanguage.SL: "Hranilna vrednost",
        EULanguage.SV: "Näringsvärde",
    },
    "energy": {
        EULanguage.BG: "Енергия",
        EULanguage.CS: "Energie",
        EULanguage.DA: "Energi",
        EULanguage.DE: "Energie",
        EULanguage.EL: "Ενέργεια",
        EULanguage.EN: "Energy",
        EULanguage.ES: "Energía",
        EULanguage.ET: "Energia",
        EULanguage.FI: "Energia",
        EULanguage.FR: "Énergie",
        EULanguage.GA: "Fuinneamh",
        EULanguage.HR: "Energija",
        EULanguage.HU: "Energia",
        EULanguage.IT: "Energia",
        EULanguage.LT: "Energinė vertė",
        EULanguage.LV: "Enerģētiskā vērtība",
        EULanguage.MT: "Enerġija",
        EULanguage.NL: "Energie",
        EULanguage.PL: "Energia",
        EULanguage.PT: "Energia",
        EULanguage.RO: "Energie",
        EULanguage.SK: "Energia",
        EULanguage.SL: "Energija",
        EULanguage.SV: "Energi",
    },
    "produced_by": {
        EULanguage.BG: "Произведено от",
        EULanguage.CS: "Vyrobeno",
        EULanguage.DA: "Produceret af",
        EULanguage.DE: "Hergestellt von",
        EULanguage.EL: "Παραγωγός",
        EULanguage.EN: "Produced by",
        EULanguage.ES: "Producido por",
        EULanguage.ET: "Tootja",
        EULanguage.FI: "Valmistaja",
        EULanguage.FR: "Produit par",
        EULanguage.GA: "Táirgthe ag",
        EULanguage.HR: "Proizvođač",
        EULanguage.HU: "Gyártó",
        EULanguage.IT: "Prodotto da",
        EULanguage.LT: "Gamintojas",
        EULanguage.LV: "Ražotājs",
        EULanguage.MT: "Prodott minn",
        EULanguage.NL: "Geproduceerd door",
        EULanguage.PL: "Producent",
        EULanguage.PT: "Produzido por",
        EULanguage.RO: "Produs de",
        EULanguage.SK: "Výrobca",
        EULanguage.SL: "Proizvajalec",
        EULanguage.SV: "Producerad av",
    },
    "country_of_origin": {
        EULanguage.BG: "Страна на произход",
        EULanguage.CS: "Země původu",
        EULanguage.DA: "Oprindelsesland",
        EULanguage.DE: "Ursprungsland",
        EULanguage.EL: "Χώρα προέλευσης",
        EULanguage.EN: "Country of origin",
        EULanguage.ES: "País de origen",
        EULanguage.ET: "Päritolumaa",
        EULanguage.FI: "Alkuperämaa",
        EULanguage.FR: "Pays d'origine",
        EULanguage.GA: "Tír thionscnaimh",
        EULanguage.HR: "Zemlja podrijetla",
        EULanguage.HU: "Származási ország",
        EULanguage.IT: "Paese d'origine",
        EULanguage.LT: "Kilmės šalis",
        EULanguage.LV: "Izcelsmes valsts",
        EULanguage.MT: "Pajjiż tal-oriġini",
        EULanguage.NL: "Land van herkomst",
        EULanguage.PL: "Kraj pochodzenia",
        EULanguage.PT: "País de origem",
        EULanguage.RO: "Țara de origine",
        EULanguage.SK: "Krajina pôvodu",
        EULanguage.SL: "Država porekla",
        EULanguage.SV: "Ursprungsland",
    },
    "drink_responsibly": {
        EULanguage.BG: "Пийте отговорно",
        EULanguage.CS: "Pijte zodpovědně",
        EULanguage.DA: "Drik ansvarligt",
        EULanguage.DE: "Trinken Sie verantwortungsvoll",
        EULanguage.EL: "Πίνετε υπεύθυνα",
        EULanguage.EN: "Drink responsibly",
        EULanguage.ES: "Bebe con responsabilidad",
        EULanguage.ET: "Joo vastutustundlikult",
        EULanguage.FI: "Juo vastuullisesti",
        EULanguage.FR: "À consommer avec modération",
        EULanguage.GA: "Ól go freagrach",
        EULanguage.HR: "Pijte odgovorno",
        EULanguage.HU: "Fogyassza felelősségteljesen",
        EULanguage.IT: "Bevi responsabilmente",
        EULanguage.LT: "Gerkite atsakingai",
        EULanguage.LV: "Dzeriet atbildīgi",
        EULanguage.MT: "Ixrob b'responsabbiltà",
        EULanguage.NL: "Drink met mate",
        EULanguage.PL: "Pij odpowiedzialnie",
        EULanguage.PT: "Beba com moderação",
        EULanguage.RO: "Consumați responsabil",
        EULanguage.SK: "Pite zodpovedne",
        EULanguage.SL: "Pijte odgovorno",
        EULanguage.SV: "Drick ansvarsfullt",
    },
    "not_for_minors": {
        EULanguage.BG: "Не е подходящо за лица под 18 години",
        EULanguage.CS: "Nevhodné pro osoby mladší 18 let",
        EULanguage.DA: "Ikke egnet for personer under 18 år",
        EULanguage.DE: "Nicht für Personen unter 18 Jahren",
        EULanguage.EL: "Ακατάλληλο για άτομα κάτω των 18 ετών",
        EULanguage.EN: "Not suitable for persons under 18",
        EULanguage.ES: "No apto para menores de 18 años",
        EULanguage.ET: "Ei sobi alla 18-aastastele",
        EULanguage.FI: "Ei sovellu alle 18-vuotiaille",
        EULanguage.FR: "Interdit aux moins de 18 ans",
        EULanguage.GA: "Níl sé oiriúnach do dhaoine faoi 18",
        EULanguage.HR: "Nije za osobe mlađe od 18 godina",
        EULanguage.HU: "18 éven aluliak számára nem ajánlott",
        EULanguage.IT: "Non adatto ai minori di 18 anni",
        EULanguage.LT: "Netinka asmenims iki 18 metų",
        EULanguage.LV: "Nav piemērots personām līdz 18 gadiem",
        EULanguage.MT: "Mhux adattat għal persuni taħt it-18-il sena",
        EULanguage.NL: "Niet geschikt voor personen onder 18 jaar",
        EULanguage.PL: "Nieodpowiednie dla osób poniżej 18 lat",
        EULanguage.PT: "Não adequado para menores de 18 anos",
        EULanguage.RO: "Nu este potrivit pentru persoane sub 18 ani",
        EULanguage.SK: "Nevhodné pre osoby mladšie ako 18 rokov",
        EULanguage.SL: "Ni primerno za osebe mlajše od 18 let",
        EULanguage.SV: "Ej lämpligt för personer under 18 år",
    },
}


# Allergen translations (EU 14 major allergens)
ALLERGEN_TRANSLATIONS = {
    "gluten": {
        EULanguage.BG: "глутен",
        EULanguage.CS: "lepek",
        EULanguage.DA: "gluten",
        EULanguage.DE: "Gluten",
        EULanguage.EL: "γλουτένη",
        EULanguage.EN: "gluten",
        EULanguage.ES: "gluten",
        EULanguage.ET: "gluteen",
        EULanguage.FI: "gluteeni",
        EULanguage.FR: "gluten",
        EULanguage.GA: "glútan",
        EULanguage.HR: "gluten",
        EULanguage.HU: "glutén",
        EULanguage.IT: "glutine",
        EULanguage.LT: "gliutenas",
        EULanguage.LV: "lipeklis",
        EULanguage.MT: "glutina",
        EULanguage.NL: "gluten",
        EULanguage.PL: "gluten",
        EULanguage.PT: "glúten",
        EULanguage.RO: "gluten",
        EULanguage.SK: "lepok",
        EULanguage.SL: "gluten",
        EULanguage.SV: "gluten",
    },
    "barley": {
        EULanguage.BG: "ечемик",
        EULanguage.CS: "ječmen",
        EULanguage.DA: "byg",
        EULanguage.DE: "Gerste",
        EULanguage.EL: "κριθάρι",
        EULanguage.EN: "barley",
        EULanguage.ES: "cebada",
        EULanguage.ET: "oder",
        EULanguage.FI: "ohra",
        EULanguage.FR: "orge",
        EULanguage.GA: "eorna",
        EULanguage.HR: "ječam",
        EULanguage.HU: "árpa",
        EULanguage.IT: "orzo",
        EULanguage.LT: "miežiai",
        EULanguage.LV: "mieži",
        EULanguage.MT: "xgħir",
        EULanguage.NL: "gerst",
        EULanguage.PL: "jęczmień",
        EULanguage.PT: "cevada",
        EULanguage.RO: "orz",
        EULanguage.SK: "jačmeň",
        EULanguage.SL: "ječmen",
        EULanguage.SV: "korn",
    },
    "wheat": {
        EULanguage.BG: "пшеница",
        EULanguage.CS: "pšenice",
        EULanguage.DA: "hvede",
        EULanguage.DE: "Weizen",
        EULanguage.EL: "σιτάρι",
        EULanguage.EN: "wheat",
        EULanguage.ES: "trigo",
        EULanguage.ET: "nisu",
        EULanguage.FI: "vehnä",
        EULanguage.FR: "blé",
        EULanguage.GA: "cruithneacht",
        EULanguage.HR: "pšenica",
        EULanguage.HU: "búza",
        EULanguage.IT: "frumento",
        EULanguage.LT: "kviečiai",
        EULanguage.LV: "kvieši",
        EULanguage.MT: "qamħ",
        EULanguage.NL: "tarwe",
        EULanguage.PL: "pszenica",
        EULanguage.PT: "trigo",
        EULanguage.RO: "grâu",
        EULanguage.SK: "pšenica",
        EULanguage.SL: "pšenica",
        EULanguage.SV: "vete",
    },
    "sulphites": {
        EULanguage.BG: "сулфити",
        EULanguage.CS: "siřičitany",
        EULanguage.DA: "sulfitter",
        EULanguage.DE: "Sulfite",
        EULanguage.EL: "θειώδη",
        EULanguage.EN: "sulphites",
        EULanguage.ES: "sulfitos",
        EULanguage.ET: "sulfitid",
        EULanguage.FI: "sulfiitit",
        EULanguage.FR: "sulfites",
        EULanguage.GA: "sulfítí",
        EULanguage.HR: "sulfiti",
        EULanguage.HU: "szulfitok",
        EULanguage.IT: "solfiti",
        EULanguage.LT: "sulfitai",
        EULanguage.LV: "sulfīti",
        EULanguage.MT: "sulfiti",
        EULanguage.NL: "sulfieten",
        EULanguage.PL: "siarczyny",
        EULanguage.PT: "sulfitos",
        EULanguage.RO: "sulfiți",
        EULanguage.SK: "siričitany",
        EULanguage.SL: "sulfiti",
        EULanguage.SV: "sulfiter",
    },
}


class LanguageInfo(BaseModel):
    code: str
    native_name: str
    english_name: str


class TranslatedLabel(BaseModel):
    key: str
    translations: dict[str, str]


def get_language_info(lang: EULanguage) -> LanguageInfo:
    """Get language info for a specific EU language"""
    names = LANGUAGE_NAMES[lang]
    return LanguageInfo(
        code=lang.value,
        native_name=names["native"],
        english_name=names["english"],
    )


def get_all_languages() -> list[LanguageInfo]:
    """Get info for all EU languages"""
    return [get_language_info(lang) for lang in EULanguage]


def translate_label(key: str, languages: list[EULanguage]) -> dict[str, str]:
    """Get translations for a label key in specified languages"""
    if key not in LABEL_TRANSLATIONS:
        return {}
    return {
        lang.value: LABEL_TRANSLATIONS[key].get(lang, key)
        for lang in languages
    }


def translate_allergen(allergen: str, languages: list[EULanguage]) -> dict[str, str]:
    """Get translations for an allergen in specified languages"""
    allergen_lower = allergen.lower()
    if allergen_lower not in ALLERGEN_TRANSLATIONS:
        return {lang.value: allergen for lang in languages}
    return {
        lang.value: ALLERGEN_TRANSLATIONS[allergen_lower].get(lang, allergen)
        for lang in languages
    }


def get_compliance_text(
    languages: list[EULanguage],
    abv: float,
    ingredients: list[str],
    allergens: list[str],
    producer: str,
    country: str,
) -> dict[str, dict[str, str]]:
    """Generate full compliance text in multiple languages"""
    result = {}
    
    for lang in languages:
        lang_code = lang.value
        labels = LABEL_TRANSLATIONS
        
        # Translate allergens
        translated_allergens = [
            ALLERGEN_TRANSLATIONS.get(a.lower(), {}).get(lang, a)
            for a in allergens
        ]
        
        result[lang_code] = {
            "ingredients_label": labels["ingredients"].get(lang, "Ingredients"),
            "ingredients_text": ", ".join(ingredients),
            "contains_label": labels["contains"].get(lang, "Contains"),
            "allergens_text": ", ".join(translated_allergens),
            "abv_label": labels["alcohol_by_volume"].get(lang, "ABV"),
            "abv_text": f"{abv}% vol.",
            "producer_label": labels["produced_by"].get(lang, "Produced by"),
            "producer_text": producer,
            "country_label": labels["country_of_origin"].get(lang, "Country of origin"),
            "country_text": country,
            "warning_text": labels["drink_responsibly"].get(lang, "Drink responsibly"),
            "age_warning": labels["not_for_minors"].get(lang, "Not for minors"),
        }
    
    return result
