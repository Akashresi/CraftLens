import pytest
from app.models import User, Product, GeneratedDescription, ProductTranslation, AIJob
from app.api.v1.endpoints.auth import register_user
from app.schemas.user import UserRegister
from app.schemas.voice import VoiceCatalogGenerateIn, ApplyCatalogIn
from app.api.v1.endpoints.voice import generate_catalog_from_speech, apply_catalog_to_product
from app.services.voice_catalog import extract_and_generate_catalog


def test_tamil_voice_catalog_generation():
    # Spoken Tamil input by an artisan weaver
    tamil_speech = "இது தூய காஞ்சிபுரம் பட்டுப் புடவை, பாரம்பரிய தறி முறையில் நெசவு செய்யப்பட்டது."
    catalog = extract_and_generate_catalog(tamil_speech, source_language="ta")
    
    assert "title_en" in catalog
    assert "Silk" in catalog["title_en"] or "Kanchipuram" in catalog["title_en"]
    assert "title_hi" in catalog
    assert "description_en" in catalog
    assert catalog["primary_material"] != ""
    assert catalog["technique"] != ""
    assert len(catalog["seo_keywords"]) >= 3
    assert catalog["suggested_category_slug"] == "handloom-textiles"


def test_hindi_voice_catalog_generation():
    # Spoken Hindi input by a pottery artisan
    hindi_speech = "यह शुद्ध मिट्टी से बना टेराकोटा कुल्हड़ और हांडी है, जो हाथ से चाक पर तैयार किया गया है।"
    catalog = extract_and_generate_catalog(hindi_speech, source_language="hi")

    assert "Terracotta" in catalog["title_en"] or "Clay" in catalog["title_en"]
    assert catalog["suggested_category_slug"] == "terracotta-pottery"
    assert "Alluvial Clay" in catalog["primary_material"] or "Clay" in catalog["primary_material"]


def test_apply_catalog_persists_multilingual_entities(db):
    from tests.conftest import create_test_artisan
    user = create_test_artisan(
        db=db,
        email="voice.weaver@craftlens.org",
        password="VoiceWeaver#2026",
        full_name="Govindhan Weaver",
        preferred_language="ta"
    )

    payload = ApplyCatalogIn(
        title="Handcrafted Pure Silk Wedding Saree",
        summary="Finely woven silk saree with traditional temple borders.",
        primary_material="Mulberry Silk",
        technique="Handloom Pit Loom",
        category_slug="handloom-textiles",
        title_hi="पारंपरिक शुद्ध रेशम विवाह साड़ी",
        description_hi="पारंपरिक मंदिर किनारों के साथ बारीकी से बुनी गई रेशम साड़ी।",
        seo_keywords=["silk saree", "handloom", "wedding"],
        source_transcript="இது தூய பட்டு புடவை",
        source_language="ta"
    )

    res = apply_catalog_to_product(payload=payload, db=db, current_user=user)
    assert res.success is True
    product_id = res.data["product_id"]

    # Verify Product in DB
    product = db.query(Product).filter(Product.id == product_id).first()
    assert product is not None
    assert product.title == "Handcrafted Pure Silk Wedding Saree"
    assert product.primary_material == "Mulberry Silk"

    # Verify GeneratedDescription
    gen_desc = db.query(GeneratedDescription).filter(GeneratedDescription.product_id == product_id).first()
    assert gen_desc is not None
    assert gen_desc.source_language == "ta"
    assert gen_desc.raw_speech_transcript == "இது தூய பட்டு புடவை"

    # Verify Translations (en and hi)
    translations = db.query(ProductTranslation).filter(ProductTranslation.product_id == product_id).all()
    lang_codes = {t.language_code for t in translations}
    assert "en" in lang_codes
    assert "hi" in lang_codes

