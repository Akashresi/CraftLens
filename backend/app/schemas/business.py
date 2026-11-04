from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DashboardMetricsOut(BaseModel):
    today_revenue: float
    month_revenue: float
    total_revenue: float
    total_expenses: float
    estimated_net_profit: float
    total_orders_count: int
    pending_orders_count: int
    active_products_count: int
    low_stock_count: int
    low_stock_items: List[Dict[str, Any]] = []


class AssistantQueryIn(BaseModel):
    query: str = Field(..., min_length=2)


class AssistantAnswerOut(BaseModel):
    query: str
    answer: str
    metrics_snapshot: DashboardMetricsOut


class MarketingGenerateIn(BaseModel):
    product_title: str
    craft_technique: str = "Traditional Indian Craft"
    platform: str = Field(default="INSTAGRAM", description="INSTAGRAM, WHATSAPP, FESTIVAL_CATALOG")
    festival: Optional[str] = None
    language: str = "en"


class MarketingGenerateOut(BaseModel):
    platform: str
    festival: Optional[str] = None
    generated_content: str
    suggested_hashtags: List[str]


class ExpenseCreateIn(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., description="RAW_MATERIALS, TOOLS, DYE, LOGISTICS, WORKSHOP_RENT")
    notes: Optional[str] = None
