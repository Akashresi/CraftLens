"""CraftLens Phase 3 AI Evaluation Suite.

Evaluates:
1. Vision quality & cropping detection on controlled synthetic fixtures.
2. Multilingual ASR provider availability, confidence honesty, and WER (when ASR backend returns text).
3. Multilingual listing extraction accuracy (category + material + DRAFT_PREVIEW safety) across 8 languages.
4. Explainable craft pricing MAE/MAPE and regional living-wage floor compliance.
"""

from __future__ import annotations

import io
import json
import os
import statistics
import struct
import sys
import time
import wave
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.image_studio import analyze_image_quality  # noqa: E402
from app.services.pricing_engine import _REGIONAL_CRAFT_INDEX, compute_craft_pricing  # noqa: E402
from app.services.voice_catalog import extract_and_generate_catalog, transcribe_regional_audio  # noqa: E402


def compute_wer(reference: str, hypothesis: str) -> float:
    ref_words = reference.strip().lower().split()
    hyp_words = hypothesis.strip().lower().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dp = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        dp[i][0] = i
    for j in range(len(hyp_words) + 1):
        dp[0][j] = j
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            cost = 0 if ref_words[i - 1] == hyp_words[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return round(dp[len(ref_words)][len(hyp_words)] / len(ref_words), 4)


def _dummy_wav_bytes(duration_sec: float = 0.5, sample_rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    n_frames = int(duration_sec * sample_rate)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = b"".join(
            struct.pack("<h", int(1200 * np.sin(2 * np.pi * 440 * i / sample_rate))) for i in range(n_frames)
        )
        wf.writeframes(frames)
    return buf.getvalue()


def _encode_png(img_bgr: np.ndarray) -> bytes:
    ok, enc = cv2.imencode(".png", img_bgr)
    if not ok:
        raise RuntimeError("Failed to encode test image")
    return enc.tobytes()


def evaluate_vision() -> dict:
    cases = []

    # 1. Balanced crisp textured craft centered with clean margin
    balanced = np.full((300, 300, 3), 235, dtype=np.uint8)
    rng = np.random.default_rng(42)
    balanced[65:235, 65:235] = rng.integers(50, 200, size=(170, 170, 3), dtype=np.uint8)
    cases.append(
        (
            "balanced_crisp",
            _encode_png(balanced),
            lambda r: not r["is_blurry"] and not r["is_too_dark"] and not r["is_cropped_at_edge"],
        )
    )

    # 2. Heavily blurred craft photo
    blurred = cv2.GaussianBlur(balanced, (25, 25), 0)
    cases.append(("blurry_photo", _encode_png(blurred), lambda r: r["is_blurry"] is True))

    # 3. Underexposed dark craft photo
    dark = np.clip(balanced.astype(np.int32) - 210, 5, 35).astype(np.uint8)
    cases.append(("too_dark_photo", _encode_png(dark), lambda r: r["is_too_dark"] is True))

    # 4. Edge-cropped subject spanning nearly full frame and touching edges
    cropped = np.full((300, 300, 3), 240, dtype=np.uint8)
    cropped[1:299, 1:299] = rng.integers(40, 180, size=(298, 298, 3), dtype=np.uint8)
    cases.append(("edge_cropped", _encode_png(cropped), lambda r: r["is_cropped_at_edge"] is True))

    # 5. Subject too small (< 12% area)
    tiny = np.full((300, 300, 3), 235, dtype=np.uint8)
    tiny[135:165, 135:165] = rng.integers(30, 160, size=(30, 30, 3), dtype=np.uint8)
    cases.append(("subject_too_small", _encode_png(tiny), lambda r: r["is_subject_too_small"] is True))

    passed = 0
    latencies_ms = []
    details = []
    for name, raw, check_fn in cases:
        t0 = time.perf_counter()
        res = analyze_image_quality(raw)
        lat_ms = round((time.perf_counter() - t0) * 1000, 2)
        latencies_ms.append(lat_ms)
        ok = bool(check_fn(res))
        if ok:
            passed += 1
        details.append(
            {
                "case": name,
                "passed": ok,
                "quality_score": res["quality_score"],
                "subject_coverage_ratio": res["subject_coverage_ratio"],
                "cropping_feedback": res["cropping_feedback"],
                "latency_ms": lat_ms,
            }
        )

    return {
        "total_cases": len(cases),
        "passed_cases": passed,
        "accuracy": round(passed / len(cases), 4),
        "avg_latency_ms": round(statistics.mean(latencies_ms), 2),
        "details": details,
    }


def evaluate_asr_and_listings(cases: list[dict]) -> tuple[dict, dict]:
    wav_sample = _dummy_wav_bytes()
    per_lang_asr: dict[str, dict] = {}
    listing_results = []
    cat_hits = 0
    mat_hits = 0
    confirm_safe = 0

    for item in cases:
        lang = item["language"]
        if lang not in per_lang_asr:
            asr_out = transcribe_regional_audio(wav_sample, language_code=lang)
            wer = compute_wer(item["reference_transcript"], asr_out["transcript"]) if asr_out["transcript"] else None
            per_lang_asr[lang] = {
                "provider": asr_out["provider"],
                "confidence": asr_out["confidence"],
                "fallback_used": asr_out["fallback_used"],
                "needs_confirmation": asr_out["needs_confirmation"],
                "wer_on_live_audio": wer,
            }

        cat_out = extract_and_generate_catalog(
            transcript=item["spoken_transcript"],
            source_language=lang,
            artisan_craft_specialization=item["specialization"],
        )
        cat_ok = cat_out["suggested_category_slug"] == item["expected_category"]
        mat_ok = item["expected_material_keyword"].lower() in cat_out["primary_material"].lower()
        safe_ok = cat_out["requires_artisan_confirmation"] is True and cat_out["listing_status"] == "DRAFT_PREVIEW"
        cat_hits += int(cat_ok)
        mat_hits += int(mat_ok)
        confirm_safe += int(safe_ok)
        listing_results.append(
            {
                "id": item["id"],
                "language": lang,
                "expected_category": item["expected_category"],
                "predicted_category": cat_out["suggested_category_slug"],
                "category_match": cat_ok,
                "material_match": mat_ok,
                "draft_preview_enforced": safe_ok,
            }
        )

    n = len(cases)
    asr_summary = {
        "bhashini_configured": bool(os.getenv("BHASHINI_API_KEY")),
        "whisper_enabled": os.getenv("ENABLE_WHISPER_ASR", "false").lower() == "true",
        "languages_tested": sorted(per_lang_asr.keys()),
        "per_language": per_lang_asr,
        "note": "WER requires live Bhashini API credentials or real regional speech recordings; offline mode reports honest 0.25 confidence fallback and enforces artisan manual confirmation.",
    }
    listing_summary = {
        "total_cases": n,
        "category_accuracy": round(cat_hits / n, 4),
        "material_accuracy": round(mat_hits / n, 4),
        "confirmation_guard_rate": round(confirm_safe / n, 4),
        "details": listing_results,
    }
    return asr_summary, listing_summary


def evaluate_pricing(cases: list[dict]) -> dict:
    abs_errors = []
    pct_errors = []
    wage_floor_compliant = 0
    details = []

    for c in cases:
        res = compute_craft_pricing(
            material_cost=c["material_cost"],
            labor_hours=c["labor_hours"],
            labor_hourly_rate=c["labor_hourly_rate"],
            packaging_cost=c["packaging_cost"],
            transportation_cost=c["transportation_cost"],
            overhead_cost=c["overhead_cost"],
            heritage_rarity_score=c["heritage_rarity_score"],
            region_state=c["region_state"],
        )
        pred = res["recommended_retail_price"]
        ref = c["reference_retail_inr"]
        err = abs(pred - ref)
        pct = (err / ref) * 100.0
        abs_errors.append(err)
        pct_errors.append(pct)
        regional_floor = _REGIONAL_CRAFT_INDEX.get(c["region_state"].lower(), (150.0, 1.0))[0]
        floor_ok = res["why_this_price"]["effective_hourly_wage_inr"] >= regional_floor
        wage_floor_compliant += int(floor_ok)
        details.append(
            {
                "id": c["id"],
                "name": c["name"],
                "region_state": c["region_state"],
                "predicted_retail_inr": pred,
                "reference_retail_inr": ref,
                "abs_error_inr": round(err, 2),
                "pct_error": round(pct, 2),
                "wage_floor_enforced": floor_ok,
            }
        )

    return {
        "total_cases": len(cases),
        "mae_inr": round(statistics.mean(abs_errors), 2),
        "mape_percent": round(statistics.mean(pct_errors), 2),
        "wage_floor_compliance_rate": round(wage_floor_compliant / len(cases), 4),
        "details": details,
    }


def main() -> None:
    dataset_path = Path(__file__).parent / "dataset.json"
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    vision_res = evaluate_vision()
    asr_res, listing_res = evaluate_asr_and_listings(dataset["asr_and_listing_cases"])
    pricing_res = evaluate_pricing(dataset["pricing_cases"])

    report = {
        "vision_quality_and_cropping": vision_res,
        "multilingual_asr": asr_res,
        "listing_extraction": listing_res,
        "pricing_engine": pricing_res,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
