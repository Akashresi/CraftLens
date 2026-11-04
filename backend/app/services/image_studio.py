import io
import os
import time
from typing import Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

ENABLE_REMBG = os.getenv("ENABLE_REMBG_DOWNLOAD", "false").lower() == "true"
REMBG_AVAILABLE = False
if ENABLE_REMBG:
    try:
        import onnxruntime
        from rembg import remove as rembg_remove
        REMBG_AVAILABLE = True
    except Exception:
        REMBG_AVAILABLE = False


def analyze_image_quality(image_bytes: bytes) -> Dict[str, Any]:
    """Analyzes image sharpness (Laplacian variance), exposure, and contrast.
    Returns metrics and a 0.0 to 10.0 overall quality score.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return {"quality_score": 0.0, "is_blurry": True, "error": "Invalid image format"}

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Blur Detection via Laplacian Variance
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_score = min(10.0, max(0.0, (lap_var / 30.0)))
    is_blurry = bool(lap_var < 90.0)

    # 2. Exposure Analysis
    mean_brightness = float(np.mean(gray))
    is_too_dark = bool(mean_brightness < 40.0)
    is_overexposed = bool(mean_brightness > 225.0)

    # 3. Contrast Evaluation
    contrast_std = float(np.std(gray))
    is_low_contrast = bool(contrast_std < 35.0)

    base_score = 7.0
    if is_blurry:
        base_score -= 3.5
    else:
        base_score += min(2.0, (lap_var - 90.0) / 150.0)

    if is_too_dark or is_overexposed:
        base_score -= 2.0
    if is_low_contrast:
        base_score -= 1.0

    final_score = round(max(1.0, min(10.0, base_score)), 2)

    return {
        "quality_score": final_score,
        "sharpness_variance": round(lap_var, 2),
        "mean_brightness": round(mean_brightness, 2),
        "contrast_std": round(contrast_std, 2),
        "is_blurry": is_blurry,
        "is_too_dark": is_too_dark,
        "is_overexposed": is_overexposed,
        "is_low_contrast": is_low_contrast,
        "recommendations": (
            "Hold camera steady or use better lighting"
            if is_blurry
            else "Lighting is good for studio processing"
        ),
    }


def remove_product_background(image_bytes: bytes) -> bytes:
    """Removes the background using rembg (if enabled) or high-precision OpenCV GrabCut.
    Returns PNG bytes with transparent alpha channel.
    """
    if REMBG_AVAILABLE:
        try:
            return rembg_remove(image_bytes)
        except Exception:
            pass

    # OpenCV GrabCut + morphological refinement
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]

    mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (max(2, int(w * 0.05)), max(2, int(h * 0.05)), min(w - 4, int(w * 0.9)), min(h - 4, int(h * 0.9)))
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 2, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    mask_smooth = cv2.GaussianBlur(mask2.astype(np.float32), (7, 7), 0)
    alpha = (mask_smooth * 255).astype(np.uint8)

    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_rgba[:, :, 3] = alpha
    _, buffer = cv2.imencode(".png", img_rgba)
    return buffer.tobytes()


def correct_lighting_and_color(image_bytes: bytes) -> bytes:
    """Applies Adaptive Histogram Equalization (CLAHE) on LAB color space."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return image_bytes

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl, a, b))
    enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.0)
    sharpened = cv2.addWeighted(enhanced_bgr, 1.3, gaussian, -0.3, 0)

    _, buffer = cv2.imencode(".jpg", sharpened, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return buffer.tobytes()


def generate_studio_white_background(transparent_png_bytes: bytes) -> bytes:
    """Composites product onto e-commerce pure white (#FFFFFF) background with soft drop shadow."""
    foreground = Image.open(io.BytesIO(transparent_png_bytes)).convert("RGBA")
    canvas = Image.new("RGBA", foreground.size, (255, 255, 255, 255))
    alpha = foreground.split()[-1]
    shadow = Image.new("RGBA", foreground.size, (40, 43, 39, 0))
    shadow_mask = alpha.filter(ImageFilter.GaussianBlur(radius=8))
    shadow.paste((30, 30, 30, 70), (0, 4), mask=shadow_mask)

    canvas.paste(shadow, (0, 0), shadow)
    canvas.paste(foreground, (0, 0), foreground)

    output = io.BytesIO()
    canvas.convert("RGB").save(output, format="JPEG", quality=95)
    return output.getvalue()


def generate_lifestyle_background(transparent_png_bytes: bytes, theme: str = "wood") -> bytes:
    """Composites product onto warm artisan-themed surfaces."""
    foreground = Image.open(io.BytesIO(transparent_png_bytes)).convert("RGBA")
    w, h = foreground.size

    if theme == "terracotta":
        bg_color = (214, 155, 120)
    elif theme == "linen":
        bg_color = (243, 239, 230)
    else:  # wood
        bg_color = (220, 205, 185)

    canvas = Image.new("RGB", (w, h), bg_color)
    canvas.paste(foreground, (0, 0), foreground)
    output = io.BytesIO()
    canvas.save(output, format="JPEG", quality=95)
    return output.getvalue()
