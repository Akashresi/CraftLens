from decimal import Decimal
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models import Category, MarketComparable


def compute_craft_pricing(
    material_cost: float,
    labor_hours: float,
    labor_hourly_rate: float = 150.0,  # Fair artisan living wage baseline (INR/hour)
    packaging_cost: float = 0.0,
    transportation_cost: float = 0.0,
    overhead_cost: float = 0.0,
    heritage_rarity_score: float = 1.0,  # 1.0 (standard) to 1.5 (master artisan / GI certified)
    category_slug: Optional[str] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Calculates explainable, fair, and profitable pricing tiers for handmade craft products:
    - Base Production Cost
    - Minimum Viable Selling Price (15% baseline)
    - Recommended Retail Selling Price (40-55% healthy margin)
    - Recommended Wholesale Price (20-25% volume margin)
    - Premium / Export Price (incorporating heritage rarity factor)
    """
    mat_cost = round(float(material_cost), 2)
    lab_hours = round(float(labor_hours), 2)
    hourly_rate = round(float(labor_hourly_rate), 2)
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

    # Recommended Retail Price (45% margin for sustainable artisan livelihood)
    retail_price = round(base_cost * 1.45, 2)

    # Premium / Export Price (Retail * heritage factor)
    rarity_mult = max(1.0, min(1.6, float(heritage_rarity_score)))
    premium_price = round(retail_price * rarity_mult, 2)

    retail_profit = round(retail_price - base_cost, 2)
    margin_percent = round((retail_profit / retail_price) * 100, 1)

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

    # Transparent, explainable explanation
    explanation = (
        f"Your direct production cost is ₹{base_cost:,.2f} (Materials: ₹{mat_cost:,.2f}, "
        f"{lab_hours} hrs of skilled hand labor @ ₹{hourly_rate}/hr = ₹{labor_total:,.2f}, and packaging/transport: ₹{pack_cost + trans_cost:,.2f}). "
        f"At our recommended retail price of ₹{retail_price:,.2f}, you earn a healthy profit of ₹{retail_profit:,.2f} ({margin_percent}% margin). "
        f"For bulk/wholesale orders of 10+ units, charge ₹{wholesale_price:,.2f} per unit."
    )

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
        "market_benchmark": {
            "category_slug": category_slug,
            "sample_comparables_count": comparables_count,
            "market_min_price": market_min,
            "market_max_price": market_max,
        },
    }
