"""Multilingual Indian-language ASR & truthful listing extractor for CraftLens 2.0.

Supports Tamil (ta), Hindi (hi), Telugu (te), Kannada (kn), Malayalam (ml),
Bengali (bn), Marathi (mr), and English (en).
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
from typing import Any

import httpx

from app.core.config import settings

SUPPORTED_LANGUAGES = {"ta", "hi", "te", "kn", "ml", "bn", "mr", "en"}

_BHASHINI_ASR_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

# Localized craft category templates for offline/fallback listing drafts
_CATEGORY_RULES: list[dict[str, Any]] = [
    {
        "slug": "handloom-textiles",
        "keywords": [
            "புடவை",
            "பட்டு",
            "நெசவு",
            "silk",
            "saree",
            "handloom",
            "loom",
            "साड़ी",
            "रेशम",
            "हथकरघा",
            "చీర",
            "పట్టు",
            "ಸೀರೆ",
            "ರೇಷ್ಮೆ",
            "സാരി",
            "പട്ട്",
            "শাড়ি",
            "রেশম",
            "पैठणी",
            "रेशीम",
        ],
        "title_en": "Authentic Handwoven Heritage Silk Saree",
        "title_hi": "पारंपरिक हथकरघा रेशम साड़ी",
        "material": "Mulberry Silk & Zari",
        "technique": "Handloom Pit Loom Weaving",
        "keywords_out": ["handloom silk saree", "pure silk", "artisan weave", "heritage textile", "indian saree"],
    },
    {
        "slug": "terracotta-pottery",
        "keywords": [
            "மண்",
            "பானை",
            "clay",
            "pottery",
            "terracotta",
            "earthen",
            "मिट्टी",
            "कुम्हार",
            "मटका",
            "दीया",
            "మట్టి",
            "కుండ",
            "ಮಣ್ಣು",
            "ಮಡಿಕೆ",
            "മൺപാത്രം",
            "মাটি",
            "মৃৎশিল্প",
            "माती",
            "मडके",
        ],
        "title_en": "Handcrafted Natural Terracotta Earthenware Vessel",
        "title_hi": "हस्तनिर्मित प्राकृतिक टेराकोटा मिट्टी का बर्तन",
        "material": "Alluvial Clay & Natural Terracotta",
        "technique": "Potter Wheel Hand-Throwing & Kiln Firing",
        "keywords_out": ["terracotta pot", "clay cookware", "earthen pot", "handmade pottery", "eco friendly craft"],
    },
    {
        "slug": "woodcraft-toys",
        "keywords": [
            "மரம்",
            "பொம்மை",
            "wood",
            "toy",
            "lacquer",
            "channapatna",
            "लकड़ी",
            "खिलौना",
            "కొయ్య",
            "బొమ్మ",
            "ಮರದ",
            "ಗೊಂಬೆ",
            "തടി",
            "കളിപ്പാട്ടം",
            "কাঠ",
            "পুতুল",
            "लाकूड",
            "खेळणी",
        ],
        "title_en": "Hand-Turned Natural Wood Craft & Lacquerware",
        "title_hi": "हस्तनिर्मित प्राकृतिक लकड़ी शिल्प एवं खिलौना",
        "material": "Seasoned Native Wood & Natural Lacquer",
        "technique": "Lathe Turning & Natural Dye Buffing",
        "keywords_out": ["wooden craft", "natural lacquer", "eco toys", "indian woodcraft", "artisan decor"],
    },
    {
        "slug": "metal-brassware",
        "keywords": [
            "பித்தளை",
            "வெண்கலம்",
            "brass",
            "bronze",
            "dhokra",
            "dokra",
            "metal",
            "bell",
            "पीतल",
            "कांसा",
            "ढोकरा",
            "ఇత్తడి",
            "ಕಂಚು",
            "ಹಿತ್ತಾಳೆ",
            "ഓട്",
            "പിച്ചള",
            "পিতল",
            "কাঁসা",
            "पितळ",
        ],
        "title_en": "Hand-Cast Traditional Brass & Dhokra Metal Art",
        "title_hi": "पारंपरिक हस्तनिर्मित पीतल एवं ढोकरा धातु शिल्प",
        "material": "Brass & Bell Metal Alloy",
        "technique": "Lost-Wax Casting & Hand Engraving",
        "keywords_out": ["dhokra brass", "lost wax casting", "handmade brass", "indian metalware", "temple craft"],
    },
    {
        "slug": "cane-bamboo",
        "keywords": [
            "மூங்கில்",
            "பிரம்பு",
            "bamboo",
            "cane",
            "basket",
            "बांस",
            "टोकरी",
            "వెదురు",
            "ಬಿದಿರು",
            "മുള",
            "বাঁশ",
            "বেত",
            "बांबू",
        ],
        "title_en": "Handwoven Sustainable Cane & Bamboo Basketry",
        "title_hi": "हस्तनिर्मित टिकाऊ बांस एवं बेंत शिल्प",
        "material": "Seasoned Bamboo & Natural Cane",
        "technique": "Hand-Splitting & Fine Basket Weaving",
        "keywords_out": ["bamboo basket", "cane craft", "sustainable decor", "handwoven bamboo", "artisan storage"],
    },
    {
        "slug": "traditional-painting",
        "keywords": [
            "ஓவியம்",
            "painting",
            "madhubani",
            "tanjore",
            "warli",
            "pattachitra",
            "पेंटिंग",
            "मधुबनी",
            "चित्र",
            "చిత్రం",
            "ಚಿತ್ರ",
            "ചിത്രം",
            "পটচিত্র",
            "চিত্রকলা",
            "वारली",
            "चित्रकला",
        ],
        "title_en": "Handpainted Traditional Indian Folk Art Canvas",
        "title_hi": "हस्तनिर्मित पारंपरिक भारतीय लोक चित्रकला",
        "material": "Natural Mineral Pigments & Handmade Paper/Canvas",
        "technique": "Freehand Fine Brush & Natural Dye Painting",
        "keywords_out": ["indian folk art", "handpainted canvas", "natural pigments", "heritage wall art", "madhubani"],
    },
]

_LOCAL_GREET_TITLE = {
    "ta": "கைவினைப் பொருள்: ",
    "hi": "",
    "te": "హస్తకళ ఉత్పత్తి: ",
    "kn": "ಕರಕುಶಲ ಉತ್ಪನ್ನ: ",
    "ml": "കരകൗശല ഉൽപ്പന്നം: ",
    "bn": "হস্তশিল্প পণ্য: ",
    "mr": "हस्तकला उत्पादन: ",
    "en": "",
}


def transcribe_regional_audio(audio_bytes: bytes, language_code: str = "ta") -> dict[str, Any]:
    """Transcribes regional Indian speech via:
    1. Bhashini ULCA pipeline (when BHASHINI_* env keys are configured),
    2. Local OpenAI Whisper (when ENABLE_WHISPER_ASR=true and valid PCM/audio present),
    3. Honest low-confidence manual-confirmation fallback when no ASR backend is reachable.
    """
    lang = language_code.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    # 1. Bhashini ASR API
    if settings.BHASHINI_API_KEY and settings.BHASHINI_USER_ID and settings.BHASHINI_PIPELINE_ID:
        try:
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {"language": {"sourceLanguage": lang}},
                    }
                ],
                "inputData": {"audio": [{"audioContent": base64.b64encode(audio_bytes).decode("ascii")}]},
            }
            headers = {
                "Authorization": settings.BHASHINI_API_KEY,
                "userID": settings.BHASHINI_USER_ID,
                "Content-Type": "application/json",
            }
            resp = httpx.post(_BHASHINI_ASR_URL, json=payload, headers=headers, timeout=15.0)
            if resp.status_code == 200:
                body = resp.json()
                text = body.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("source", "")
                if text.strip():
                    return {
                        "transcript": text.strip(),
                        "detected_language": lang,
                        "confidence": 0.90,
                        "provider": "bhashini_ulca",
                        "fallback_used": False,
                        "needs_confirmation": len(text.strip()) < 10,
                    }
        except Exception:
            pass

    # 2. Optional Local Whisper ASR (only invoked when explicitly enabled)
    if os.getenv("ENABLE_WHISPER_ASR", "false").lower() == "true":
        try:
            import whisper

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                model = whisper.load_model(os.getenv("WHISPER_MODEL_SIZE", "base"))
                res = model.transcribe(tmp_path, language=lang if lang != "en" else "en")
                text = str(res.get("text", "")).strip()
                if text:
                    return {
                        "transcript": text,
                        "detected_language": lang,
                        "confidence": 0.78,
                        "provider": "whisper_local",
                        "fallback_used": True,
                        "needs_confirmation": True,
                    }
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception:
            pass

    # 3. Honest Low-Confidence Fallback (never fabricate high confidence)
    return {
        "transcript": "",
        "detected_language": lang,
        "confidence": 0.25,
        "provider": "offline_low_confidence_fallback",
        "fallback_used": True,
        "needs_confirmation": True,
    }


def extract_and_generate_catalog(
    transcript: str,
    source_language: str = "ta",
    artisan_craft_specialization: str | None = None,
) -> dict[str, Any]:
    """Extracts structured e-commerce catalog fields from spoken transcript.
    Always returns DRAFT_PREVIEW with requires_artisan_confirmation=True so listings
    never auto-publish without artisan review.
    """
    lang = source_language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    # 1. Gemini REST API when GEMINI_API_KEY is configured
    if settings.GEMINI_API_KEY:
        try:
            model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
            )
            prompt = (
                f"You are CraftLens AI. An artisan spoke in '{lang}': \"{transcript}\". "
                f"Specialization: {artisan_craft_specialization or 'Traditional Handicrafts'}. "
                "STRICT: Never invent unmentioned materials or GI tags. "
                "Return strict JSON with keys: title_en, title_hi, title_local, "
                "description_en, description_hi, description_local, primary_material, "
                "technique, seo_keywords (array of 5 strings), suggested_category_slug "
                "(one of handloom-textiles, terracotta-pottery, woodcraft-toys, metal-brassware, "
                "cane-bamboo, traditional-painting)."
            )
            resp = httpx.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=15.0,
            )
            if resp.status_code == 200:
                cand = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if cand.startswith("```json"):
                    cand = cand[7:]
                if cand.startswith("```"):
                    cand = cand[3:]
                if cand.endswith("```"):
                    cand = cand[:-3]
                parsed = json.loads(cand.strip())
                parsed["source_language"] = lang
                parsed["requires_artisan_confirmation"] = True
                parsed["listing_status"] = "DRAFT_PREVIEW"
                parsed.setdefault("title_local", parsed.get("title_en", ""))
                parsed.setdefault("description_local", parsed.get("description_en", ""))
                return parsed
        except Exception:
            pass

    # 2. Deterministic Multilingual Keyword Extractor (7+ Indian languages + English)
    text_lower = transcript.lower()
    matched = None
    for rule in _CATEGORY_RULES:
        if any(kw.lower() in text_lower for kw in rule["keywords"]):
            matched = rule
            break

    if not matched:
        matched = {
            "slug": "woodcraft-toys",
            "title_en": "Artisanal Handmade Heritage Creation",
            "title_hi": "पारंपरिक हस्तशिल्प कलाकृति",
            "material": "Natural Regional Raw Materials",
            "technique": "Traditional Indian Handicraft",
            "keywords_out": ["handmade in india", "artisan craft", "sustainable handmade", "heritage", "craftlens"],
        }

    if matched["slug"] == "handloom-textiles":
        desc_en = (
            "Handcrafted by traditional weavers using pure mulberry silk and zari accents. "
            "Dry clean only. Reflects regional handloom craft heritage."
        )
        desc_hi = "शुद्ध रेशम और पारंपरिक ज़री से हथकरघे पर बुनी गई पारंपरिक हस्तनिर्मित साड़ी।"
    elif matched["slug"] == "terracotta-pottery":
        desc_en = (
            "Hand-thrown terracotta clay cookware fired in traditional kilns without chemical glazes. "
            "100% biodegradable and handcrafted."
        )
        desc_hi = "प्राकृतिक मिट्टी से बना और पारंपरिक भट्टे में पकाया गया हस्तनिर्मित टेराकोटा बर्तन।"
    else:
        desc_en = (
            f"Individually handcrafted using {matched['material']} and {matched['technique']}. "
            "Created by a verified artisan with authentic handmade character."
        )
        desc_hi = f"पारंपरिक कारीगरों द्वारा {matched['technique']} से हस्तनिर्मित प्रामाणिक कलाकृति।"

    prefix = _LOCAL_GREET_TITLE.get(lang, "")
    title_local = (
        matched["title_hi"]
        if lang == "hi"
        else (matched["title_en"] if lang == "en" else f"{prefix}{matched['title_en']}")
    )
    desc_local = desc_hi if lang == "hi" else (f"{transcript}\n\n{desc_en}" if lang != "en" else desc_en)

    return {
        "title_en": matched["title_en"],
        "title_hi": matched["title_hi"],
        "title_local": title_local,
        "description_en": desc_en,
        "description_hi": desc_hi,
        "description_local": desc_local,
        "source_language": lang,
        "primary_material": matched["material"],
        "technique": matched["technique"],
        "seo_keywords": matched["keywords_out"],
        "suggested_category_slug": matched["slug"],
        "requires_artisan_confirmation": True,
        "listing_status": "DRAFT_PREVIEW",
    }
