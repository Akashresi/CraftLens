import pytest

from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.business import (
    ask_ai_business_assistant,
    generate_marketing_campaign_copy,
    get_dashboard_analytics,
    record_business_expense,
)
from app.api.v1.endpoints.pricing import apply_pricing_to_product
from app.api.v1.endpoints.voice import apply_catalog_to_product
from app.models import BusinessExpense, Product, User
from app.schemas.business import AssistantQueryIn, ExpenseCreateIn, MarketingGenerateIn
from app.schemas.pricing import SavePricingIn
from app.schemas.user import UserRegister
from app.schemas.voice import ApplyCatalogIn


def test_business_dashboard_and_ai_assistant_flow(db):
    from tests.conftest import create_test_artisan

    # 1. Register Artisan
    user = create_test_artisan(
        db=db,
        email="biz.artisan@craftlens.org",
        password="ArtisanPass#123",
        full_name="Kalaivani Saree Studio",
        preferred_language="ta",
    )

    # 2. Add product with low inventory (2 units on hand, threshold 3)
    prod_res = apply_catalog_to_product(
        payload=ApplyCatalogIn(
            title="Temple Weave Pure Silk Dupatta",
            summary="Handcrafted silk stole with zari borders",
            primary_material="Silk",
            technique="Korvai",
            category_slug="handloom-textiles",
            source_language="ta",
        ),
        db=db,
        current_user=user,
    )
    apply_pricing_to_product(
        product_id=prod_res.data["product_id"],
        pricing_in=SavePricingIn(retail_price=1800.0, wholesale_price=1400.0, stock_quantity=2),
        db=db,
        current_user=user,
    )

    # 3. Record business expense (raw materials: ₹1500)
    exp_res = record_business_expense(
        expense_in=ExpenseCreateIn(amount=1500.0, category="RAW_MATERIALS", notes="Purchased mulberry silk yarn"),
        db=db,
        current_user=user,
    )
    assert exp_res.success is True

    # 4. Check dashboard analytics
    metrics_res = get_dashboard_analytics(db=db, current_user=user)
    assert metrics_res.success is True
    data = metrics_res.data
    assert data.total_expenses == 1500.0
    assert data.low_stock_count == 1
    assert data.active_products_count == 1

    # 5. Test AI Business Assistant natural language answers
    # Query: Low stock check
    stock_answer = ask_ai_business_assistant(
        query_in=AssistantQueryIn(query="Which products have low stock?"), db=db, current_user=user
    )
    assert stock_answer.success is True
    assert "Temple Weave Pure Silk Dupatta" in stock_answer.data.answer

    # Query: Revenue check
    rev_answer = ask_ai_business_assistant(
        query_in=AssistantQueryIn(query="How much did I earn this month?"), db=db, current_user=user
    )
    assert rev_answer.success is True
    assert "monthly revenue" in rev_answer.data.answer.lower()

    # 6. Test Marketing Assistant Generation
    marketing_res = generate_marketing_campaign_copy(
        copy_in=MarketingGenerateIn(
            product_title="Temple Weave Pure Silk Dupatta",
            craft_technique="Korvai Silk Weaving",
            platform="INSTAGRAM",
            festival="Diwali",
        ),
        current_user=user,
    )
    assert marketing_res.success is True
    copy_data = marketing_res.data
    assert "#CraftLens" in copy_data.generated_content
    assert "Diwali" in copy_data.generated_content
