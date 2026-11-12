import io

import pytest
from fastapi import UploadFile
from PIL import Image, ImageDraw

from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.studio import process_product_photo
from app.models import ImageProcessingJob, User
from app.schemas.user import UserRegister
from app.services.image_studio import (
    analyze_image_quality,
    correct_lighting_and_color,
    generate_lifestyle_background,
    generate_studio_white_background,
    remove_product_background,
)


def create_sample_craft_image_bytes() -> bytes:
    """Generates an in-memory synthetic craft image (terracotta pot pattern) for testing."""
    img = Image.new("RGB", (400, 400), color=(240, 230, 215))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 300, 320], fill=(196, 123, 82), outline=(138, 77, 44), width=4)
    draw.rectangle([160, 70, 240, 110], fill=(160, 90, 50), outline=(138, 77, 44), width=3)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_image_quality_analysis():
    img_bytes = create_sample_craft_image_bytes()
    analysis = analyze_image_quality(img_bytes)
    assert "quality_score" in analysis
    assert 1.0 <= analysis["quality_score"] <= 10.0
    assert "sharpness_variance" in analysis
    assert "mean_brightness" in analysis
    assert isinstance(analysis["is_blurry"], bool)


def test_lighting_correction_and_enhancement():
    img_bytes = create_sample_craft_image_bytes()
    enhanced = correct_lighting_and_color(img_bytes)
    assert len(enhanced) > 0
    img = Image.open(io.BytesIO(enhanced))
    assert img.size == (400, 400)


def test_background_removal_and_white_studio_generation():
    img_bytes = create_sample_craft_image_bytes()
    transparent_png = remove_product_background(img_bytes)
    assert len(transparent_png) > 0

    trans_img = Image.open(io.BytesIO(transparent_png))
    assert trans_img.mode == "RGBA"

    white_studio = generate_studio_white_background(transparent_png)
    assert len(white_studio) > 0
    studio_img = Image.open(io.BytesIO(white_studio))
    assert studio_img.mode == "RGB"
    corner_pixel = studio_img.getpixel((5, 5))
    assert corner_pixel == (255, 255, 255)


def test_lifestyle_background_generation():
    img_bytes = create_sample_craft_image_bytes()
    transparent_png = remove_product_background(img_bytes)
    lifestyle = generate_lifestyle_background(transparent_png, theme="terracotta")
    assert len(lifestyle) > 0
    lifestyle_img = Image.open(io.BytesIO(lifestyle))
    assert lifestyle_img.size == (400, 400)


def test_studio_process_endpoint(db):
    from tests.conftest import create_test_artisan

    user = create_test_artisan(
        db=db,
        email="studio.artisan@craftlens.org",
        full_name="Master Craftsman",
        password="ArtisanStudio#2026",
    )

    img_bytes = create_sample_craft_image_bytes()
    upload = UploadFile(
        filename="terracotta_pot.jpg",
        file=io.BytesIO(img_bytes),
    )

    res = process_product_photo(file=upload, lifestyle_theme="wood", db=db, current_user=user)
    assert res.success is True
    data = res.data
    assert data.status == "COMPLETED"
    assert data.white_bg_url.startswith("/uploads/processed/")
    assert data.quality_score > 0

    job = db.query(ImageProcessingJob).filter(ImageProcessingJob.id == data.job_id).first()
    assert job is not None
    assert job.user_id == user.id
    assert job.status == "COMPLETED"
