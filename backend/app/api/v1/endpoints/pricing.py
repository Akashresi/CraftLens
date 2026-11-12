import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models import Inventory, PricingHistory, Product, ProductVariant, User
from app.schemas.common import APIResponse
from app.schemas.pricing import PricingCalculateIn, PricingEstimateOut, SavePricingIn
from app.services.pricing_engine import compute_craft_pricing

router = APIRouter()


@router.post("/calculate", response_model=APIResponse[PricingEstimateOut])
def calculate_price_breakdown(
    pricing_in: PricingCalculateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Calculates production cost, fair artisan wage, retail/wholesale/export price tiers,
    and returns a transparent explainable recommendation.
    """
    require_role("ARTISAN")(current_user)
    result = compute_craft_pricing(
        material_cost=pricing_in.material_cost,
        labor_hours=pricing_in.labor_hours,
        labor_hourly_rate=pricing_in.labor_hourly_rate,
        packaging_cost=pricing_in.packaging_cost,
        transportation_cost=pricing_in.transportation_cost,
        overhead_cost=pricing_in.overhead_cost,
        heritage_rarity_score=pricing_in.heritage_rarity_score,
        category_slug=pricing_in.category_slug,
        db=db,
    )
    return APIResponse(
        success=True,
        message="Dynamic pricing calculations completed",
        data=PricingEstimateOut(**result),
    )


@router.post("/apply/{product_id}", response_model=APIResponse[dict])
def apply_pricing_to_product(
    product_id: str,
    pricing_in: SavePricingIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Applies artisan approved retail and wholesale prices to product,
    creates/updates the ProductVariant and Inventory records.
    """
    require_role("ARTISAN")(current_user)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sku = pricing_in.sku or f"{product.slug[:10].upper()}-{str(uuid.uuid4())[:4].upper()}"

    # Check for existing primary variant
    variant = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).first()
    if not variant:
        variant = ProductVariant(
            product_id=product.id,
            sku=sku,
            title="Standard Handmade Edition",
            price_retail=pricing_in.retail_price,
            price_wholesale=pricing_in.wholesale_price,
            min_wholesale_qty=pricing_in.min_wholesale_qty,
            stock_quantity=pricing_in.stock_quantity,
        )
        db.add(variant)
        db.flush()

        # Create Inventory record
        inv = Inventory(
            product_variant_id=variant.id,
            quantity_on_hand=pricing_in.stock_quantity,
            reserved_quantity=0,
            low_stock_threshold=3,
        )
        db.add(inv)
    else:
        # Record pricing change in pricing_history
        hist = PricingHistory(
            product_id=product.id,
            changed_by_user_id=current_user.id,
            old_retail_price=variant.price_retail,
            new_retail_price=pricing_in.retail_price,
            reason="Artisan adjusted pricing recommendation",
        )
        db.add(hist)
        variant.price_retail = pricing_in.retail_price
        variant.price_wholesale = pricing_in.wholesale_price
        variant.stock_quantity = pricing_in.stock_quantity

    # Set product status to active so it appears in the marketplace
    product.status = "ACTIVE"
    db.commit()

    return APIResponse(
        success=True,
        message="Product pricing and inventory initialized successfully",
        data={
            "product_id": product.id,
            "variant_id": variant.id,
            "retail_price": float(variant.price_retail),
            "wholesale_price": float(variant.price_wholesale),
            "stock_quantity": variant.stock_quantity,
        },
    )
