"""Beer label models and type definitions."""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
import uuid


class BeerLabelCategory(str, Enum):
    """Beer label category enumeration."""
    NECK = "neck"
    FRONT_BODY = "front_body"
    BACK_BODY = "back_body"
    WRAPAROUND = "wraparound"
    CAN = "can"
    SHRINK_SLEEVE = "shrink_sleeve"


class BeerLabelType(BaseModel):
    """Beer label type with standard dimensions."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Display name")
    category: BeerLabelCategory = Field(..., description="Label category")
    width_mm: float = Field(..., description="Standard width in mm")
    height_mm: float = Field(..., description="Standard height in mm")
    description: Optional[str] = Field(default=None)
    recommended_substrates: List[str] = Field(default_factory=list)
    min_width_mm: Optional[float] = Field(default=None, description="Minimum width")
    max_width_mm: Optional[float] = Field(default=None, description="Maximum width")
    min_height_mm: Optional[float] = Field(default=None, description="Minimum height")
    max_height_mm: Optional[float] = Field(default=None, description="Maximum height")


class BeerSubstrate(BaseModel):
    """Beer-specific substrate with properties."""
    code: str = Field(..., description="Substrate code")
    name: str = Field(..., description="Display name")
    material_id: int = Field(..., description="OGOS material ID")
    is_waterproof: bool = Field(default=False)
    is_biodegradable: bool = Field(default=False)
    finish: str = Field(default="matte", description="matte, glossy, textured")
    recommended_for: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None)


class Allergen(str, Enum):
    """Common beer allergens per EU regulation."""
    GLUTEN = "gluten"
    WHEAT = "wheat"
    BARLEY = "barley"
    RYE = "rye"
    OATS = "oats"
    SULPHITES = "sulphites"
    FISH = "fish"
    MILK = "milk"
    LACTOSE = "lactose"
    EGGS = "eggs"
    NUTS = "nuts"


class RecyclingSymbol(str, Enum):
    """Recycling symbols for beer packaging."""
    GREEN_DOT = "green_dot"
    GLASS_RECYCLING = "glass_recycling"
    ALUMINUM_RECYCLING = "aluminum_recycling"
    TIDYMAN = "tidyman"
    MOBIUS_LOOP = "mobius_loop"
    DEPOSIT_RETURN_DE = "deposit_return_de"
    DEPOSIT_RETURN_NL = "deposit_return_nl"
    DEPOSIT_RETURN_BE = "deposit_return_be"


class NutritionalInfo(BaseModel):
    """Nutritional information per 100ml."""
    energy_kj: Optional[float] = Field(default=None, description="Energy in kJ")
    energy_kcal: Optional[float] = Field(default=None, description="Energy in kcal")
    fat_g: Optional[float] = Field(default=None, description="Fat in grams")
    saturated_fat_g: Optional[float] = Field(default=None, description="Saturated fat")
    carbohydrates_g: Optional[float] = Field(default=None, description="Carbohydrates")
    sugars_g: Optional[float] = Field(default=None, description="Sugars")
    protein_g: Optional[float] = Field(default=None, description="Protein")
    salt_g: Optional[float] = Field(default=None, description="Salt")


class BeerComplianceData(BaseModel):
    """EU-compliant beer label data per Regulation 1169/2011."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: Optional[str] = Field(default=None, description="Associated order ID")
    
    beer_name: str = Field(..., description="Name of the beer")
    beer_style: Optional[str] = Field(default=None, description="e.g., IPA, Stout")
    abv_percent: float = Field(..., ge=0, le=100, description="Alcohol by volume %")
    volume_ml: int = Field(..., gt=0, description="Net volume in ml")
    
    ingredients: List[str] = Field(..., description="List of ingredients")
    allergens: List[Allergen] = Field(default_factory=list, description="Detected allergens")
    
    country_of_origin: str = Field(..., description="Country code (ISO 3166-1)")
    producer_name: str = Field(..., description="Producer/brewery name")
    producer_address: str = Field(..., description="Producer address")
    
    lot_number: Optional[str] = Field(default=None, description="Batch/lot number")
    best_before: Optional[date] = Field(default=None, description="Best before date")
    
    nutritional_info: Optional[NutritionalInfo] = Field(default=None)
    recycling_symbols: List[RecyclingSymbol] = Field(default_factory=list)
    
    additional_claims: List[str] = Field(
        default_factory=list, 
        description="e.g., 'Organic', 'Vegan', 'Gluten-Free'"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "beer_name": "Hoppy Days IPA",
                "beer_style": "IPA",
                "abv_percent": 6.5,
                "volume_ml": 330,
                "ingredients": ["Water", "Barley malt", "Hops", "Yeast"],
                "allergens": ["gluten", "barley"],
                "country_of_origin": "NL",
                "producer_name": "Dutch Craft Brewery",
                "producer_address": "Brouwerijstraat 1, 1234 AB Amsterdam",
                "lot_number": "L2026-03-001",
                "best_before": "2027-03-19",
                "recycling_symbols": ["glass_recycling", "deposit_return_nl"],
            }
        }


class BeerLabelValidationResult(BaseModel):
    """Validation result for beer label PDFs."""
    is_valid: bool = Field(..., description="Overall validation status")
    errors: List[str] = Field(default_factory=list, description="Blocking errors")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")
    
    has_abv: bool = Field(default=False, description="ABV text detected")
    has_allergens: bool = Field(default=False, description="Allergen info detected")
    has_ingredients: bool = Field(default=False, description="Ingredients list detected")
    has_producer_info: bool = Field(default=False, description="Producer info detected")
    has_volume: bool = Field(default=False, description="Volume info detected")
    has_country_origin: bool = Field(default=False, description="Country of origin detected")
    
    detected_text: Optional[str] = Field(default=None, description="Extracted text")
    font_sizes_mm: List[float] = Field(default_factory=list, description="Detected font sizes")
    min_font_size_mm: Optional[float] = Field(default=None, description="Smallest font size")
    
    barcode_detected: bool = Field(default=False)
    barcode_type: Optional[str] = Field(default=None, description="e.g., EAN-13")
    barcode_value: Optional[str] = Field(default=None)


STANDARD_BEER_LABEL_TYPES: List[BeerLabelType] = [
    # Bottle Labels
    BeerLabelType(
        id="neck-standard",
        name="Neck Label (Standard)",
        category=BeerLabelCategory.NECK,
        width_mm=40,
        height_mm=100,
        description="Standard bottle neck wrap label",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=30,
        max_width_mm=50,
        min_height_mm=80,
        max_height_mm=120,
    ),
    BeerLabelType(
        id="front-body-standard",
        name="Front Body Label (Standard)",
        category=BeerLabelCategory.FRONT_BODY,
        width_mm=80,
        height_mm=100,
        description="Main front label for brand and beer name",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit", "Tintoretto Gesso"],
        min_width_mm=70,
        max_width_mm=90,
        min_height_mm=90,
        max_height_mm=120,
    ),
    BeerLabelType(
        id="back-body-standard",
        name="Back Body Label (Standard)",
        category=BeerLabelCategory.BACK_BODY,
        width_mm=80,
        height_mm=60,
        description="Back label for ingredients and legal info",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=70,
        max_width_mm=90,
        min_height_mm=50,
        max_height_mm=80,
    ),
    BeerLabelType(
        id="wraparound-330ml",
        name="Wraparound Label (330ml Bottle)",
        category=BeerLabelCategory.WRAPAROUND,
        width_mm=240,
        height_mm=100,
        description="Full wrap label for 330ml bottles",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit", "PP transparant"],
        min_width_mm=200,
        max_width_mm=280,
        min_height_mm=80,
        max_height_mm=120,
    ),
    # Can Labels - Standard Dutch Formats
    BeerLabelType(
        id="can-25cl-slim",
        name="Blik 25cl Slim Can",
        category=BeerLabelCategory.CAN,
        width_mm=160,
        height_mm=110,
        description="25cl slim can label (160 x 110 mm)",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=158,
        max_width_mm=162,
        min_height_mm=108,
        max_height_mm=112,
    ),
    BeerLabelType(
        id="can-25cl-sleek",
        name="Blik 25cl Sleek Can",
        category=BeerLabelCategory.CAN,
        width_mm=175,
        height_mm=90,
        description="25cl sleek can label (175 x 90 mm)",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=173,
        max_width_mm=177,
        min_height_mm=88,
        max_height_mm=92,
    ),
    BeerLabelType(
        id="can-33cl-standard",
        name="Blik 33cl Standaard",
        category=BeerLabelCategory.CAN,
        width_mm=205,
        height_mm=85,
        description="33cl standard can label (205 x 85 mm)",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=203,
        max_width_mm=207,
        min_height_mm=83,
        max_height_mm=87,
    ),
    BeerLabelType(
        id="can-44cl-standard",
        name="Blik 44cl Standaard",
        category=BeerLabelCategory.CAN,
        width_mm=205,
        height_mm=120,
        description="44cl standard can label (205 x 120 mm)",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=203,
        max_width_mm=207,
        min_height_mm=118,
        max_height_mm=122,
    ),
    BeerLabelType(
        id="can-50cl-standard",
        name="Blik 50cl Standaard",
        category=BeerLabelCategory.CAN,
        width_mm=205,
        height_mm=135,
        description="50cl standard can label (205 x 135 mm)",
        recommended_substrates=["PP Glans Wit", "PP Mat Wit"],
        min_width_mm=203,
        max_width_mm=207,
        min_height_mm=133,
        max_height_mm=137,
    ),
]


BEER_SUBSTRATES: List[BeerSubstrate] = [
    BeerSubstrate(
        code="PP_GLANS_WIT",
        name="PP Glans Wit",
        material_id=6,
        is_waterproof=True,
        is_biodegradable=False,
        finish="glossy",
        recommended_for=["chilled_bottles", "cans", "premium"],
        description="Waterproof glossy white polypropylene, ideal for chilled beverages",
    ),
    BeerSubstrate(
        code="PP_MAT_WIT",
        name="PP Mat Wit",
        material_id=5,
        is_waterproof=True,
        is_biodegradable=False,
        finish="matte",
        recommended_for=["craft_beer", "premium", "artisan"],
        description="Waterproof matte white polypropylene, premium craft look",
    ),
    BeerSubstrate(
        code="PP_TRANSPARANT",
        name="PP Transparant",
        material_id=7,
        is_waterproof=True,
        is_biodegradable=False,
        finish="glossy",
        recommended_for=["minimalist", "no_label_look", "modern"],
        description="Clear polypropylene for no-label look designs",
    ),
    BeerSubstrate(
        code="NATUREFLEX_WHITE",
        name="Natureflex White",
        material_id=18,
        is_waterproof=False,
        is_biodegradable=True,
        finish="matte",
        recommended_for=["eco_friendly", "organic", "sustainable"],
        description="Biodegradable cellulose film, eco-conscious choice",
    ),
    BeerSubstrate(
        code="TINTORETTO_GESSO",
        name="Tintoretto Gesso",
        material_id=76,
        is_waterproof=False,
        is_biodegradable=False,
        finish="textured",
        recommended_for=["artisan", "craft_beer", "premium", "limited_edition"],
        description="Textured premium paper with embossed feel",
    ),
    BeerSubstrate(
        code="KRAFT_BRUIN",
        name="Kraft Bruin Permanent",
        material_id=13,
        is_waterproof=False,
        is_biodegradable=True,
        finish="matte",
        recommended_for=["craft_beer", "natural", "rustic"],
        description="Brown kraft paper for natural, rustic aesthetic",
    ),
]


def detect_allergens(ingredients: List[str]) -> List[Allergen]:
    """Auto-detect allergens from ingredients list."""
    detected: List[Allergen] = []
    ingredients_lower = " ".join(ingredients).lower()
    
    gluten_sources = ["barley", "wheat", "rye", "oats", "malt", "grist"]
    if any(source in ingredients_lower for source in gluten_sources):
        detected.append(Allergen.GLUTEN)
        if "barley" in ingredients_lower:
            detected.append(Allergen.BARLEY)
        if "wheat" in ingredients_lower:
            detected.append(Allergen.WHEAT)
        if "rye" in ingredients_lower:
            detected.append(Allergen.RYE)
        if "oats" in ingredients_lower:
            detected.append(Allergen.OATS)
    
    if "sulphite" in ingredients_lower or "sulfite" in ingredients_lower:
        detected.append(Allergen.SULPHITES)
    
    if "isinglass" in ingredients_lower or "fish" in ingredients_lower:
        detected.append(Allergen.FISH)
    
    milk_sources = ["milk", "lactose", "cream", "whey", "casein"]
    if any(source in ingredients_lower for source in milk_sources):
        detected.append(Allergen.MILK)
        if "lactose" in ingredients_lower:
            detected.append(Allergen.LACTOSE)
    
    if "egg" in ingredients_lower:
        detected.append(Allergen.EGGS)
    
    nut_sources = ["nut", "almond", "hazelnut", "walnut", "pecan", "pistachio"]
    if any(source in ingredients_lower for source in nut_sources):
        detected.append(Allergen.NUTS)
    
    return list(set(detected))
