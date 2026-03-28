"""Beer label endpoints."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.models.pdf_validation import PDFValidationResult
from app.models.beer_label import (
    BeerLabelType,
    BeerLabelCategory,
    BeerSubstrate,
    BeerComplianceData,
    Allergen,
    STANDARD_BEER_LABEL_TYPES,
    BEER_SUBSTRATES,
    detect_allergens,
)
from app.services.pdf_validator import get_pdf_validator
from app.models.beer_i18n import (
    EULanguage,
    LanguageInfo,
    LANGUAGE_NAMES,
    LABEL_TRANSLATIONS,
    ALLERGEN_TRANSLATIONS,
    get_all_languages,
    get_language_info,
    translate_label,
    translate_allergen,
    get_compliance_text,
)

router = APIRouter(prefix="/beer", tags=["beer"])
logger = logging.getLogger("uvicorn.error")


@router.get("/label-types", response_model=List[BeerLabelType])
async def list_label_types(
    category: Optional[BeerLabelCategory] = None,
) -> List[BeerLabelType]:
    """
    List available beer label types.
    
    Optionally filter by category (neck, front_body, back_body, wraparound, can, shrink_sleeve).
    """
    label_types = STANDARD_BEER_LABEL_TYPES
    
    if category:
        label_types = [lt for lt in label_types if lt.category == category]
    
    return label_types


@router.get("/label-types/{label_type_id}", response_model=BeerLabelType)
async def get_label_type(label_type_id: str) -> BeerLabelType:
    """Get a specific beer label type by ID."""
    for label_type in STANDARD_BEER_LABEL_TYPES:
        if label_type.id == label_type_id:
            return label_type
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Label type '{label_type_id}' not found",
    )


@router.get("/substrates", response_model=List[BeerSubstrate])
async def list_substrates(
    waterproof: Optional[bool] = None,
    biodegradable: Optional[bool] = None,
    finish: Optional[str] = None,
) -> List[BeerSubstrate]:
    """
    List available beer-specific substrates.
    
    Optionally filter by:
    - waterproof: True for waterproof materials (recommended for chilled beverages)
    - biodegradable: True for eco-friendly materials
    - finish: 'matte', 'glossy', or 'textured'
    """
    substrates = BEER_SUBSTRATES
    
    if waterproof is not None:
        substrates = [s for s in substrates if s.is_waterproof == waterproof]
    
    if biodegradable is not None:
        substrates = [s for s in substrates if s.is_biodegradable == biodegradable]
    
    if finish:
        substrates = [s for s in substrates if s.finish == finish]
    
    return substrates


@router.get("/substrates/{substrate_code}", response_model=BeerSubstrate)
async def get_substrate(substrate_code: str) -> BeerSubstrate:
    """Get a specific substrate by code."""
    for substrate in BEER_SUBSTRATES:
        if substrate.code == substrate_code:
            return substrate
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Substrate '{substrate_code}' not found",
    )


@router.post("/detect-allergens", response_model=List[Allergen])
async def detect_allergens_endpoint(ingredients: List[str]) -> List[Allergen]:
    """
    Auto-detect allergens from a list of ingredients.
    
    Returns a list of detected allergens based on EU Regulation 1169/2011.
    Common beer allergens include gluten (barley, wheat), sulphites, and lactose.
    """
    if not ingredients:
        return []
    
    return detect_allergens(ingredients)


@router.get("/label-types/{label_type_id}/recommended-substrates")
async def get_recommended_substrates(label_type_id: str) -> List[BeerSubstrate]:
    """Get recommended substrates for a specific label type."""
    label_type = None
    for lt in STANDARD_BEER_LABEL_TYPES:
        if lt.id == label_type_id:
            label_type = lt
            break
    
    if not label_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Label type '{label_type_id}' not found",
        )
    
    recommended = []
    for substrate in BEER_SUBSTRATES:
        if substrate.name in label_type.recommended_substrates:
            recommended.append(substrate)
    
    return recommended


@router.get("/categories")
async def list_categories() -> List[dict]:
    """List all beer label categories with descriptions."""
    return [
        {
            "value": BeerLabelCategory.NECK.value,
            "label": "Neck Label",
            "description": "Wraps around the bottle neck",
        },
        {
            "value": BeerLabelCategory.FRONT_BODY.value,
            "label": "Front Body Label",
            "description": "Main label on the front of the bottle",
        },
        {
            "value": BeerLabelCategory.BACK_BODY.value,
            "label": "Back Body Label",
            "description": "Back label for ingredients and legal info",
        },
        {
            "value": BeerLabelCategory.WRAPAROUND.value,
            "label": "Wraparound Label",
            "description": "Full wrap around the bottle",
        },
        {
            "value": BeerLabelCategory.CAN.value,
            "label": "Can Label",
            "description": "Label for beer cans",
        },
        {
            "value": BeerLabelCategory.SHRINK_SLEEVE.value,
            "label": "Shrink Sleeve",
            "description": "Full coverage shrink wrap label",
        },
    ]


# ============================================================================
# EU Language / i18n Endpoints
# ============================================================================

@router.get("/languages", response_model=List[LanguageInfo])
async def list_languages() -> List[LanguageInfo]:
    """
    List all 24 official EU languages.
    
    Returns language code, native name, and English name for each.
    """
    return get_all_languages()


@router.get("/languages/{lang_code}", response_model=LanguageInfo)
async def get_language(lang_code: str) -> LanguageInfo:
    """Get info for a specific EU language by code (e.g., 'nl', 'de', 'fr')."""
    try:
        lang = EULanguage(lang_code.lower())
        return get_language_info(lang)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{lang_code}' not found. Use ISO 639-1 codes.",
        )


@router.get("/translations/labels")
async def get_label_translations(
    keys: List[str] = Query(
        default=["ingredients", "contains", "alcohol_by_volume"],
        description="Label keys to translate",
    ),
    languages: List[str] = Query(
        default=["en", "nl", "de", "fr"],
        description="Language codes (ISO 639-1)",
    ),
) -> dict:
    """
    Get translations for compliance label text.
    
    Available keys:
    - ingredients, contains, alcohol_by_volume, best_before
    - nutritional_info, energy, produced_by, country_of_origin
    - drink_responsibly, not_for_minors
    """
    lang_enums = []
    for code in languages:
        try:
            lang_enums.append(EULanguage(code.lower()))
        except ValueError:
            pass
    
    if not lang_enums:
        lang_enums = [EULanguage.EN]
    
    result = {}
    for key in keys:
        if key in LABEL_TRANSLATIONS:
            result[key] = translate_label(key, lang_enums)
    
    return result


@router.get("/translations/allergens")
async def get_allergen_translations(
    allergens: List[str] = Query(
        default=["gluten", "barley", "wheat", "sulphites"],
        description="Allergen names to translate",
    ),
    languages: List[str] = Query(
        default=["en", "nl", "de", "fr"],
        description="Language codes (ISO 639-1)",
    ),
) -> dict:
    """
    Get translations for allergen names.
    
    Common beer allergens: gluten, barley, wheat, sulphites
    """
    lang_enums = []
    for code in languages:
        try:
            lang_enums.append(EULanguage(code.lower()))
        except ValueError:
            pass
    
    if not lang_enums:
        lang_enums = [EULanguage.EN]
    
    result = {}
    for allergen in allergens:
        result[allergen] = translate_allergen(allergen, lang_enums)
    
    return result


class ComplianceTextRequest(BaseModel):
    languages: List[str] = ["en", "nl"]
    abv: float = 5.0
    ingredients: List[str] = ["water", "barley malt", "hops", "yeast"]
    allergens: List[str] = ["gluten", "barley"]
    producer: str = "Brewery Name"
    country: str = "Netherlands"


@router.post("/compliance-text")
async def generate_compliance_text(request: ComplianceTextRequest) -> dict:
    """
    Generate full EU-compliant label text in multiple languages.
    
    Returns all required label sections translated into each requested language.
    Use this to generate the text content for back labels.
    """
    lang_enums = []
    for code in request.languages:
        try:
            lang_enums.append(EULanguage(code.lower()))
        except ValueError:
            pass
    
    if not lang_enums:
        lang_enums = [EULanguage.EN]
    
    return get_compliance_text(
        languages=lang_enums,
        abv=request.abv,
        ingredients=request.ingredients,
        allergens=request.allergens,
        producer=request.producer,
        country=request.country,
    )


@router.post("/preflight-pdf", response_model=PDFValidationResult)
async def preflight_pdf(file: UploadFile = File(..., description="Print-ready PDF to analyse")) -> PDFValidationResult:
    """
    Run PyMuPDF preflight (size, pages, boxes, pragmatic CMYK hints) without creating an order.

    **No authentication** — intended for the label intake UI and quick checks; rate-limit at the edge in production.
    """
    name = (file.filename or "").lower()
    if not name.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a .pdf extension",
        )
    data = await file.read()
    return get_pdf_validator().validate(data)
