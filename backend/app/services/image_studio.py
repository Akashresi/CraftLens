import io
import os
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageFilter

ENABLE_REMBG = os.getenv("ENABLE_REMBG_DOWNLOAD", "false").lower() == "true"
REMBG_AVAILABLE = False
if ENABLE_REMBG:
    try:
        from rembg import remove as rembg_remove

        REMBG_AVAILABLE = True
    except Exception:
        REMBG_AVAILABLE = False


def analyze_image_quality(image_bytes: bytes) -> dict[str, Any]:
    """Analyzes image sharpness (Laplacian variance), exposure, contrast, and subject cropping/framing.
    Returns objective metrics, cropping feedback, and a 1.0 to 10.0 quality score.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return {
            "quality_score": 0.0,
            "sharpness_variance": 0.0,
            "mean_brightness": 0.0,
            "contrast_std": 0.0,
            "is_blurry": True,
            "is_too_dark": True,
            "is_overexposed": False,
            "is_low_contrast": True,
            "subject_coverage_ratio": 0.0,
            "is_cropped_at_edge": False,
            "is_subject_too_small": True,
            "cropping_feedback": "Invalid image format",
            "recommendations": "Upload a valid JPEG, PNG, or WEBP craft photo",
            "error": "Invalid image format",
        }

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    # 1. Blur Detection via Laplacian Variance
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = bool(lap_var < 90.0)

    # 2. Exposure Analysis
    mean_brightness = float(np.mean(gray))
    is_too_dark = bool(mean_brightness < 40.0)
    is_overexposed = bool(mean_brightness > 225.0)

    # 3. Contrast Evaluation
    contrast_std = float(np.std(gray))
    is_low_contrast = bool(contrast_std < 35.0)

    # 4. Subject Cropping & Framing Analysis via Canny Edge Bounding Box
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 40, 140)
    pts = cv2.findNonZero(edges)
    subject_coverage_ratio = 0.0
    is_cropped_at_edge = False
    is_subject_too_small = False

    if pts is not None and len(pts) > 10:
        x, y, bw, bh = cv2.boundingRect(pts)
        subject_coverage_ratio = round((bw * bh) / max(1, w * h), 3)
        margin_x = max(2, int(w * 0.015))
        margin_y = max(2, int(h * 0.015))
        touches_border = x <= margin_x or y <= margin_y or (x + bw) >= (w - margin_x) or (y + bh) >= (h - margin_y)
        is_cropped_at_edge = bool(touches_border and subject_coverage_ratio > 0.75)
        is_subject_too_small = bool(subject_coverage_ratio < 0.12)
    else:
        is_subject_too_small = True

    if is_cropped_at_edge:
        cropping_feedback = "Craft subject touches frame edge; step back slightly so edges are visible."
    elif is_subject_too_small:
        cropping_feedback = "Craft occupies too little of the frame; move camera closer to center the item."
    else:
        cropping_feedback = "Framing looks balanced with clean margin around the craft."

    base_score = 7.5
    if is_blurry:
        base_score -= 3.0
    else:
        base_score += min(1.8, (lap_var - 90.0) / 150.0)

    if is_too_dark or is_overexposed:
        base_score -= 2.0
    if is_low_contrast:
        base_score -= 1.0
    if is_cropped_at_edge or is_subject_too_small:
        base_score -= 0.8

    final_score = round(max(1.0, min(10.0, base_score)), 2)

    recs = []
    if is_blurry:
        recs.append("Hold camera steady or tap to focus")
    if is_too_dark:
        recs.append("Move to natural daylight")
    if is_overexposed:
        recs.append("Avoid harsh direct glare")
    if is_cropped_at_edge or is_subject_too_small:
        recs.append(cropping_feedback)

    return {
        "quality_score": final_score,
        "sharpness_variance": round(lap_var, 2),
        "mean_brightness": round(mean_brightness, 2),
        "contrast_std": round(contrast_std, 2),
        "is_blurry": is_blurry,
        "is_too_dark": is_too_dark,
        "is_overexposed": is_overexposed,
        "is_low_contrast": is_low_contrast,
        "subject_coverage_ratio": subject_coverage_ratio,
        "is_cropped_at_edge": is_cropped_at_edge,
        "is_subject_too_small": is_subject_too_small,
        "cropping_feedback": cropping_feedback,
        "recommendations": "; ".join(recs) if recs else "Lighting and framing are great for studio processing",
    }


def remove_product_background(image_bytes: bytes) -> bytes:
    """Removes background using rembg (if enabled) or OpenCV GrabCut + morphological cleanup."""
    if REMBG_AVAILABLE:
        try:
            return rembg_remove(image_bytes)
        except Exception:
            pass

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Unable to decode image for background removal")
    h, w = img.shape[:2]

    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    rect = (max(2, int(w * 0.05)), max(2, int(h * 0.05)), min(w - 4, int(w * 0.9)), min(h - 4, int(h * 0.9)))
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # Morphological open/close removes isolated background specks cleanly
    kernel = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask_smooth = cv2.GaussianBlur(mask_clean.astype(np.float32), (7, 7), 0)
    alpha = (mask_smooth * 255).astype(np.uint8)

    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_rgba[:, :, 3] = alpha
    _, buffer = cv2.imencode(".png", img_rgba)
    return buffer.tobytes()


def correct_lighting_and_color(image_bytes: bytes) -> bytes:
    """Applies Adaptive Histogram Equalization (CLAHE) on LAB color space + gentle unsharp mask."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return image_bytes

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    limg = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), 2.0)
    sharpened = cv2.addWeighted(enhanced_bgr, 1.25, gaussian, -0.25, 0)

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
