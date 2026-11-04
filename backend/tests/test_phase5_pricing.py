import pytest
from app.models import User, Product, ProductVariant, Inventory, PricingHistory
from app.services.pricing_engine import compute_craft_pricing
from app.schemas.pricing import PricingCalculateIn, SavePricingIn
from app.api.v1.endpoints.auth import register_user
from app.schemas.user import UserRegister
from app.api.v1.endpoints.voice import apply_catalog_to_product
from app.schemas.voice import ApplyCatalogIn
from app.api.v1.endpoints.pricing import calculate_price_breakdown, apply_pricing_to_product


def test_craft_pricing_calculation():
    # 8 hours of handloom work, ₹1200 raw silk, ₹150 packaging, ₹200 transport
    res = compute_craft_pricing(
        material_cost=1200.0,
        labor_hours=8.0,
        labor_hourly_rate=150.0,  # 8 * 150 = 1200
        packaging_cost=150.0,
        transportation_cost=200.0,
        overhead_cost=50.0,
        heritage_rarity_score=1.2,
    )
    # Total cost = 1200 + 1200 + 150 + 200 + 50 = 2800.0
    assert res["total_production_cost"] == 2800.0
    assert res["labor_total_cost"] == 1200.0
    assert res["min_selling_price"] == round(2800.0 * 1.15, 2)
    assert res["recommended_wholesale_price"] == round(2800.0 * 1.25, 2)
    assert res["recommended_retail_price"] == round(2800.0 * 1.45, 2)
    assert res["premium_export_price"] > res["recommended_retail_price"]
    assert res["profit_margin_percent"] > 25.0
    assert "Your direct production cost is ₹2,800.00" in res["explanation"]


def test_apply_pricing_to_product_flow(db):
    reg = register_user(
        user_in=UserRegister(
            email="pricing.artisan@craftlens.org",
            password="ArtisanPass#123",
            full_name="Master Weaving Artisan",
            role_code="ARTISAN"
        ),
        db=db
    )
    user = db.query(User).filter(User.email == "pricing.artisan@craftlens.org").first()

    # Create draft product
    prod_res = apply_catalog_to_product(
        payload=ApplyCatalogIn(
            title="Temple Border Kanchipuram Saree",
            summary="Silk saree with handcrafted zari pallu",
            primary_material="Silk",
            technique="Korvai",
            category_slug="handloom-textiles",
            source_language="ta"
        ),
        db=db,
        current_user=user
    )
    product_id = prod_res.data["product_id"]

    # Apply approved pricing
    save_in = SavePricingIn(
        retail_price=4200.0,
        wholesale_price=3500.0,
        min_wholesale_qty=10,
        stock_quantity=8,
    )
    apply_res = apply_pricing_to_product(
        product_id=product_id,
        pricing_in=save_in,
        db=db,
        current_user=user
    )
    assert apply_res.success is True
    assert apply_res.data["retail_price"] == 4200.0
    assert apply_res.data["wholesale_price"] == 3500.0

    # Verify database state
    product = db.query(Product).filter(Product.id == product_id).first()
    assert product.status == "ACTIVE"

    variant = db.query(ProductVariant).filter(ProductVariant.product_id == product_id).first()
    assert variant is not None
    assert float(variant.price_retail) == 4200.0
    assert variant.stock_quantity == 8

    # Verify inventory record
    inv = db.query(Inventory).filter(Inventory.product_variant_id == variant.id).first()
    assert inv is not None
    assert inv.quantity_on_hand == 8
