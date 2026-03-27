"""Tests for pricing_policy."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.pricing_policy import (
    QuotePresentation,
    apply_discount_to_subtotal_ex_vat,
    build_customer_totals,
    clamp_discount_percent,
    margin_eur,
    meets_minimum_margin_eur,
    meets_minimum_order,
    round_currency,
    sell_subtotal_ex_vat_from_cost,
)


def test_sell_subtotal_margin_formula() -> None:
    # 35% margin on revenue: revenue = 65 / 0.65 = 100
    assert sell_subtotal_ex_vat_from_cost(Decimal("65"), Decimal("0.35")) == Decimal("100.00")
    assert sell_subtotal_ex_vat_from_cost(Decimal("0"), Decimal("0.35")) == Decimal("0")


def test_sell_subtotal_invalid_margin() -> None:
    with pytest.raises(ValueError):
        sell_subtotal_ex_vat_from_cost(Decimal("10"), Decimal("1"))
    with pytest.raises(ValueError):
        sell_subtotal_ex_vat_from_cost(Decimal("-1"), Decimal("0.2"))


def test_round_currency_half_up() -> None:
    assert round_currency(Decimal("10.125")) == Decimal("10.13")
    assert round_currency(Decimal("10.124")) == Decimal("10.12")


def test_clamp_discount() -> None:
    assert clamp_discount_percent(Decimal("0.15"), Decimal("0.10")) == Decimal("0.10")
    assert clamp_discount_percent(Decimal("0.05"), Decimal("0.10")) == Decimal("0.05")


def test_apply_discount() -> None:
    assert apply_discount_to_subtotal_ex_vat(Decimal("100"), Decimal("0.10")) == Decimal("90.00")


def test_build_customer_totals_b2b_b2c() -> None:
    b2b = build_customer_totals(Decimal("100"), Decimal("0.21"), QuotePresentation.EX_VAT)
    assert b2b.subtotal_ex_vat == Decimal("100.00")
    assert b2b.vat_amount == Decimal("21.00")
    assert b2b.total_incl_vat == Decimal("121.00")
    assert b2b.primary_display_amount == Decimal("100.00")

    b2c = build_customer_totals(Decimal("100"), Decimal("0.21"), QuotePresentation.INCL_VAT)
    assert b2c.primary_display_amount == Decimal("121.00")


def test_margin_and_minimums() -> None:
    assert margin_eur(Decimal("100"), Decimal("70")) == Decimal("30.00")
    assert meets_minimum_order(Decimal("99"), Decimal("100")) is False
    assert meets_minimum_order(Decimal("100"), Decimal("100")) is True
    assert meets_minimum_order(Decimal("50"), None) is True
    assert meets_minimum_margin_eur(Decimal("100"), Decimal("70"), Decimal("25")) is True
    assert meets_minimum_margin_eur(Decimal("100"), Decimal("80"), Decimal("25")) is False
