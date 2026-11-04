from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User, ArtisanProfile, BusinessExpense
from app.schemas.business import (
    DashboardMetricsOut,
    AssistantQueryIn,
    AssistantAnswerOut,
    MarketingGenerateIn,
    MarketingGenerateOut,
    ExpenseCreateIn,
)
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role
from app.services.business_manager import (
    get_artisan_dashboard_metrics,
    answer_business_assistant_query,
    create_promotional_copy,
)

router = APIRouter()


@router.get("/metrics", response_model=APIResponse[DashboardMetricsOut])
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves real-time sales, revenue, profit, pending orders, and inventory metrics."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    metrics = get_artisan_dashboard_metrics(artisan_id=profile.id, db=db)
    return APIResponse(
        success=True,
        message="Business metrics retrieved",
        data=DashboardMetricsOut(**metrics),
    )


@router.post("/ask-assistant", response_model=APIResponse[AssistantAnswerOut])
def ask_ai_business_assistant(
    query_in: AssistantQueryIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Answers natural language business questions using actual verified database records."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    result = answer_business_assistant_query(query=query_in.query, artisan_id=profile.id, db=db)
    return APIResponse(
        success=True,
        message="Assistant response generated",
        data=AssistantAnswerOut(
            query=result["query"],
            answer=result["answer"],
            metrics_snapshot=DashboardMetricsOut(**result["metrics_snapshot"]),
        ),
    )


@router.post("/marketing-copy", response_model=APIResponse[MarketingGenerateOut])
def generate_marketing_campaign_copy(
    copy_in: MarketingGenerateIn,
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Generates promotional posts, Instagram captions, and WhatsApp catalogs."""
    copy_data = create_promotional_copy(
        product_title=copy_in.product_title,
        craft_technique=copy_in.craft_technique,
        platform=copy_in.platform,
        festival=copy_in.festival,
        language=copy_in.language,
    )
    return APIResponse(
        success=True,
        message="Promotional marketing copy generated",
        data=MarketingGenerateOut(**copy_data),
    )


@router.post("/expenses", response_model=APIResponse[dict])
def record_business_expense(
    expense_in: ExpenseCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Records operational and raw material expenses to accurately compute net profitability."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Artisan profile not found")

    expense = BusinessExpense(
        artisan_id=profile.id,
        category=expense_in.category,
        amount=expense_in.amount,
        notes=expense_in.notes,
        expense_date=datetime.now(timezone.utc),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return APIResponse(
        success=True,
        message="Expense recorded successfully",
        data={"expense_id": expense.id, "amount": float(expense.amount), "category": expense.category},
    )
