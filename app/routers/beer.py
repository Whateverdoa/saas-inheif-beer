"""Beer label endpoints."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

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
