from typing import Any

from sqlalchemy.orm import Session

from app.models import Category, MarketComparable

# Regional skilled artisan living wage baselines & market demand multipliers (INR/hr baseline, index)
_REGIONAL_CRAFT_INDEX: dict[str, tuple[float, float]] = {
    "tamil nadu": (155.0, 1.04),
    "karnataka": (160.0, 1.05),
    "kerala": (170.0, 1.06),
    "maharashtra": (165.0, 1.06),
    "uttar pradesh": (140.0, 1.00),
    "rajasthan": (150.0, 1.03),
    "west bengal": (145.0, 1.02),
    "bihar": (135.0, 1.00),
    "chhattisgarh": (135.0, 1.00),
    "odisha": (140.0, 1.01),
}


def compute_craft_pricing(
    material_cost: float,
    labor_hours: float,
    labor_hourly_rate: float = 150.0,
    packaging_cost: float = 0.0,
    transportation_cost: float = 0.0,
    overhead_cost: float = 0.0,
    heritage_rarity_score: float = 1.0,
    category_slug: str | None = None,
    db: Session | None = None,
    region_state: str | None = None,
) -> dict[str, Any]:
    """Calculates explainable, fair, and profitable pricing tiers for handmade craft products
    using materials, labour hours (enforcing regional living-wage baseline when region_state given),
    overhead, heritage rarity, and verified market comparables.
    """
    mat_cost = round(float(material_cost), 2)
    lab_hours = round(float(labor_hours), 2)
    requested_rate = round(float(labor_hourly_rate), 2)

    region_key = (region_state or "").strip().lower()
    regional_floor, regional_multiplier = _REGIONAL_CRAFT_INDEX.get(region_key, (150.0, 1.0))
    hourly_rate = max(requested_rate, regional_floor) if region_state else requested_rate

    pack_cost = round(float(packaging_cost), 2)
    trans_cost = round(float(transportation_cost), 2)
    ovh_cost = round(float(overhead_cost), 2)

    labor_total = round(lab_hours * hourly_rate, 2)
    base_cost = round(mat_cost + labor_total + pack_cost + trans_cost + ovh_cost, 2)

    if base_cost <= 0:
        base_cost = 100.0

    # Minimum Selling Price (Break-even + 15% safety buffer)
    min_price = round(base_cost * 1.15, 2)

    # Wholesale Price (25% margin for bulk/B2B buyers)
    wholesale_price = round(base_cost * 1.25, 2)

    # Recommended Retail Price (45% baseline margin adjusted by regional cluster index)
    retail_price = round(base_cost * 1.45 * regional_multiplier, 2)

    # Check for verified market comparables if DB session and category provided
    market_min = None
    market_max = None
    comparables_count = 0
    confidence_score = 0.85

    if db and category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            comps = db.query(MarketComparable).filter(MarketComparable.category_id == cat.id).all()
            if comps:
                market_min = float(min(c.price_range_min for c in comps))
                market_max = float(max(c.price_range_max for c in comps))
                comparables_count = len(comps)
                confidence_score = 0.95
                # Blend lightly toward market midpoint while strictly preserving min_price floor
                market_mid = (market_min + market_max) / 2.0
                blended = round((retail_price * 0.75) + (market_mid * 0.25), 2)
                retail_price = max(min_price, blended)

    # Premium / Export Price (Retail * heritage factor)
    rarity_mult = max(1.0, min(1.6, float(heritage_rarity_score)))
    premium_price = round(retail_price * rarity_mult, 2)

    retail_profit = round(retail_price - base_cost, 2)
    margin_percent = round((retail_profit / retail_price) * 100, 1)

    explanation = (
        f"Your direct production cost is ₹{base_cost:,.2f} (Materials: ₹{mat_cost:,.2f}, "
        f"{lab_hours} hrs of skilled hand labor @ ₹{hourly_rate}/hr = ₹{labor_total:,.2f}, and packaging/transport: ₹{pack_cost + trans_cost:,.2f}). "
        f"At our recommended retail price of ₹{retail_price:,.2f}, you earn a healthy profit of ₹{retail_profit:,.2f} ({margin_percent}% margin). "
        f"For bulk/wholesale orders of 10+ units, charge ₹{wholesale_price:,.2f} per unit."
    )

    why_this_price = {
        "materials_inr": mat_cost,
        "labor_inr": labor_total,
        "labor_hours": lab_hours,
        "effective_hourly_wage_inr": hourly_rate,
        "packaging_and_shipping_inr": round(pack_cost + trans_cost, 2),
        "overhead_inr": ovh_cost,
        "region_state": region_state or "National Baseline",
        "regional_index": regional_multiplier,
        "heritage_rarity_multiplier": rarity_mult,
        "comparables_matched": comparables_count,
        "retail_margin_percent": margin_percent,
    }

    return {
        "material_cost": mat_cost,
        "labor_hours": lab_hours,
        "labor_hourly_rate": hourly_rate,
        "labor_total_cost": labor_total,
        "packaging_cost": pack_cost,
        "transportation_cost": trans_cost,
        "overhead_cost": ovh_cost,
        "total_production_cost": base_cost,
        "min_selling_price": min_price,
        "recommended_wholesale_price": wholesale_price,
        "recommended_retail_price": retail_price,
        "premium_export_price": premium_price,
        "profit_amount": retail_profit,
        "profit_margin_percent": margin_percent,
        "confidence_score": confidence_score,
        "explanation": explanation,
        "why_this_price": why_this_price,
        "market_benchmark": {
            "category_slug": category_slug,
            "sample_comparables_count": comparables_count,
            "market_min_price": market_min,
            "market_max_price": market_max,
        },
    }
