from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class QualityAnalysisOut(BaseModel):
    quality_score: float
    sharpness_variance: float
    mean_brightness: float
    contrast_std: float
    is_blurry: bool
    is_too_dark: bool
    is_overexposed: bool
    is_low_contrast: bool
    recommendations: str


class StudioProcessResult(BaseModel):
    job_id: str
    original_url: str
    white_bg_url: str
    lifestyle_url: str
    transparent_png_url: str
    quality_score: float
    latency_ms: int
    status: str

