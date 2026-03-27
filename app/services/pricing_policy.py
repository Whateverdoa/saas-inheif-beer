"""Customer pricing from supplier cost: margin, VAT, rounding, floors, discount cap."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QuotePresentation(str, Enum):
    """How the primary price is shown to the customer."""

    EX_VAT = "ex_vat"
    INCL_VAT = "incl_vat"


def round_currency(value: Decimal, places: int = 2) -> Decimal:
    """Round to `places` decimal digits (half-up), for EUR cents use places=2."""
    if places < 0:
        raise ValueError("places must be non-negative")
    quant = Decimal(10) ** -places
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def sell_subtotal_ex_vat_from_cost(
    supplier_cost_ex_vat: Decimal,
    target_gross_margin_on_revenue: Decimal,
) -> Decimal:
    """
    Revenue ex-VAT so that (revenue - cost) / revenue == target margin.

    Parameters
    ----------
    supplier_cost_ex_vat :
        Landed supplier / OG cost excluding VAT.
    target_gross_margin_on_revenue :
        Margin as fraction of revenue, in [0, 1).

    Returns
    -------
    Decimal
        Rounded sell subtotal ex-VAT.
    """
    if supplier_cost_ex_vat < 0:
        raise ValueError("supplier_cost_ex_vat must be non-negative")
    if not Decimal("0") <= target_gross_margin_on_revenue < Decimal("1"):
        raise ValueError("target_gross_margin_on_revenue must be in [0, 1)")
    if supplier_cost_ex_vat == 0 and target_gross_margin_on_revenue > 0:
        return Decimal("0")
    raw = supplier_cost_ex_vat / (Decimal("1") - target_gross_margin_on_revenue)
    return round_currency(raw)


def clamp_discount_percent(
    requested_discount_pct: Decimal,
    max_discount_pct: Decimal,
) -> Decimal:
    """Return discount % applied after governance (0..max)."""
    if requested_discount_pct < 0:
        raise ValueError("requested_discount_pct must be non-negative")
    if max_discount_pct < 0:
        raise ValueError("max_discount_pct must be non-negative")
    capped = min(requested_discount_pct, max_discount_pct)
    return round_currency(capped, places=4)


def apply_discount_to_subtotal_ex_vat(
    subtotal_ex_vat: Decimal,
    discount_pct: Decimal,
) -> Decimal:
    """Apply discount percent to ex-VAT subtotal; result >= 0, rounded."""
    if subtotal_ex_vat < 0:
        raise ValueError("subtotal_ex_vat must be non-negative")
    if not Decimal("0") <= discount_pct <= Decimal("1"):
        raise ValueError("discount_pct must be in [0, 1]")
    factor = Decimal("1") - discount_pct
    return round_currency(subtotal_ex_vat * factor)


class CustomerPriceTotals(BaseModel):
    """Rounded VAT breakdown for quotes / API responses."""

    subtotal_ex_vat: Decimal = Field(..., description="After margin & discount, ex-VAT")
    vat_rate: Decimal = Field(..., ge=Decimal("0"))
    vat_amount: Decimal
    total_incl_vat: Decimal
    presentation: QuotePresentation
    primary_display_amount: Decimal = Field(
        ...,
        description="Main price shown to customer (ex or incl VAT per presentation).",
    )


def build_customer_totals(
    subtotal_ex_vat: Decimal,
    vat_rate: Decimal,
    presentation: QuotePresentation,
) -> CustomerPriceTotals:
    """Compute VAT lines and pick primary display amount per B2B vs B2C style."""
    if subtotal_ex_vat < 0:
        raise ValueError("subtotal_ex_vat must be non-negative")
    if vat_rate < 0:
        raise ValueError("vat_rate must be non-negative")
    ex = round_currency(subtotal_ex_vat)
    vat_amt = round_currency(ex * vat_rate)
    incl = round_currency(ex + vat_amt)
    if presentation == QuotePresentation.EX_VAT:
        primary = ex
    else:
        primary = incl
    return CustomerPriceTotals(
        subtotal_ex_vat=ex,
        vat_rate=vat_rate,
        vat_amount=vat_amt,
        total_incl_vat=incl,
        presentation=presentation,
        primary_display_amount=primary,
    )


def margin_eur(subtotal_ex_vat: Decimal, cost_ex_vat: Decimal) -> Decimal:
    """Gross margin in EUR (ex-VAT subtotal minus cost)."""
    return round_currency(subtotal_ex_vat - cost_ex_vat)


def meets_minimum_order(subtotal_ex_vat: Decimal, minimum_order_ex_vat: Optional[Decimal]) -> bool:
    """True if no minimum configured or subtotal meets floor."""
    if minimum_order_ex_vat is None:
        return True
    return subtotal_ex_vat >= minimum_order_ex_vat


def meets_minimum_margin_eur(
    subtotal_ex_vat: Decimal,
    cost_ex_vat: Decimal,
    minimum_margin_eur: Optional[Decimal],
) -> bool:
    """True if no floor or (subtotal - cost) >= minimum margin."""
    if minimum_margin_eur is None:
        return True
    return margin_eur(subtotal_ex_vat, cost_ex_vat) >= minimum_margin_eur
