from pydantic import BaseModel


class QualityAnalysisOut(BaseModel):
    quality_score: float
    sharpness_variance: float
    mean_brightness: float
    contrast_std: float
    is_blurry: bool
    is_too_dark: bool
    is_overexposed: bool
    is_low_contrast: bool
    subject_coverage_ratio: float = 0.0
    is_cropped_at_edge: bool = False
    is_subject_too_small: bool = False
    cropping_feedback: str = "Framing looks balanced"
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


class AsyncJobStatusOut(BaseModel):
    job_id: str
    job_type: str
    status: str
    attempts: int = 1
    result: dict | None = None
    error_message: str | None = None
