from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PricingCalculateIn(BaseModel):
    material_cost: float = Field(..., ge=0)
    labor_hours: float = Field(..., ge=0)
    labor_hourly_rate: float = Field(default=150.0, ge=50)
    packaging_cost: float = Field(default=0.0, ge=0)
    transportation_cost: float = Field(default=0.0, ge=0)
    overhead_cost: float = Field(default=0.0, ge=0)
    heritage_rarity_score: float = Field(default=1.0, ge=1.0, le=2.0)
    category_slug: Optional[str] = None


class MarketBenchmarkOut(BaseModel):
    category_slug: Optional[str] = None
    sample_comparables_count: int = 0
    market_min_price: Optional[float] = None
    market_max_price: Optional[float] = None


class PricingEstimateOut(BaseModel):
    material_cost: float
    labor_hours: float
    labor_hourly_rate: float
    labor_total_cost: float
    packaging_cost: float
    transportation_cost: float
    overhead_cost: float
    total_production_cost: float
    min_selling_price: float
    recommended_wholesale_price: float
    recommended_retail_price: float
    premium_export_price: float
    profit_amount: float
    profit_margin_percent: float
    confidence_score: float
    explanation: str
    market_benchmark: MarketBenchmarkOut


class SavePricingIn(BaseModel):
    retail_price: float
    wholesale_price: float
    min_wholesale_qty: int = 10
    stock_quantity: int = 5
    sku: Optional[str] = None

