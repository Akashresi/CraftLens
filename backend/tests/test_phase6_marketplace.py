import pytest
from app.models import User, Product, ProductVariant, Inventory, Order, StockMovement, Payment
from app.api.v1.endpoints.auth import register_user
from app.schemas.user import UserRegister
from app.api.v1.endpoints.voice import apply_catalog_to_product
from app.schemas.voice import ApplyCatalogIn
from app.api.v1.endpoints.pricing import apply_pricing_to_product
from app.schemas.pricing import SavePricingIn
from app.schemas.marketplace import OrderCreateIn, CartItemIn
from app.api.v1.endpoints.marketplace import list_categories, discover_products, get_product_detail
from app.api.v1.endpoints.orders import create_order_checkout, get_buyer_orders, get_artisan_incoming_orders


def test_marketplace_discovery_and_checkout_flow(db):
    # 1. Check categories
    cat_res = list_categories(db=db)
    assert cat_res.success is True
    assert len(cat_res.data) >= 6

    # 2. Register artisan & create product
    artisan_reg = register_user(
        user_in=UserRegister(
            email="market.artisan@craftlens.org",
            password="MarketPass#123",
            full_name="Woodcraft Master",
            role_code="ARTISAN"
        ),
        db=db
    )
    artisan_user = db.query(User).filter(User.email == "market.artisan@craftlens.org").first()

    prod_res = apply_catalog_to_product(
        payload=ApplyCatalogIn(
            title="Channapatna Wooden Rocking Horse",
            summary="Traditional lacquered non-toxic wooden toy",
            primary_material="Wrightia tinctoria wood",
            technique="Lathe turning & natural lacquering",
            category_slug="woodcraft-toys",
            source_language="kn"
        ),
        db=db,
        current_user=artisan_user
    )
    product_id = prod_res.data["product_id"]

    # Price and stock the product (10 units in inventory)
    pricing_res = apply_pricing_to_product(
        product_id=product_id,
        pricing_in=SavePricingIn(
            retail_price=850.0,
            wholesale_price=650.0,
            stock_quantity=10,
        ),
        db=db,
        current_user=artisan_user
    )
    variant_id = pricing_res.data["variant_id"]

    # 3. Discover products in marketplace
    discover_res = discover_products(
        category_slug="woodcraft-toys",
        search="Channapatna",
        db=db
    )
    assert discover_res.success is True
    assert discover_res.data.total >= 1
    found_prod = discover_res.data.items[0]
    assert "Channapatna" in found_prod.title

    # 4. Product details
    detail_res = get_product_detail(slug_or_id=product_id, db=db)
    assert detail_res.success is True
    assert detail_res.data.view_count >= 1

    # 5. Register retail buyer and checkout 2 units
    buyer_reg = register_user(
        user_in=UserRegister(
            email="craft.enthusiast@gmail.com",
            password="BuyerPass#123",
            full_name="Pooja Sharma",
            role_code="RETAIL_BUYER"
        ),
        db=db
    )
    buyer_user = db.query(User).filter(User.email == "craft.enthusiast@gmail.com").first()

    checkout_payload = OrderCreateIn(
        items=[CartItemIn(variant_id=variant_id, quantity=2)],
        order_type="RETAIL",
        delivery_address={"street": "45 Green Park", "city": "Bengaluru", "pincode": "560001"},
        payment_method="SANDBOX"
    )
    order_res = create_order_checkout(order_in=checkout_payload, db=db, current_user=buyer_user)
    assert order_res.success is True
    order_data = order_res.data
    # 2 * 850 = 1700 subtotal, >= 1000 => free shipping => 1700 total
    assert order_data.subtotal == 1700.0
    assert order_data.total_amount == 1700.0
    assert order_data.status == "CONFIRMED"

    # 6. Verify inventory was deducted: 10 - 2 = 8
    inv = db.query(Inventory).filter(Inventory.product_variant_id == variant_id).first()
    assert inv.quantity_on_hand == 8

    # Verify stock movement recorded
    movement = db.query(StockMovement).filter(StockMovement.inventory_id == inv.id).first()
    assert movement is not None
    assert movement.quantity_change == -2

    # 7. Verify buyer orders
    my_orders = get_buyer_orders(db=db, current_user=buyer_user)
    assert len(my_orders.data) == 1

    # 8. Verify artisan incoming orders
    artisan_orders = get_artisan_incoming_orders(db=db, current_user=artisan_user)
    assert len(artisan_orders.data) == 1
    assert artisan_orders.data[0]["quantity"] == 2
    assert artisan_orders.data[0]["total_payout"] == 1700.0
