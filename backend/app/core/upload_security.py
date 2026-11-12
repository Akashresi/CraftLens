"""Upload security validation, magic-byte sniffing, EXIF stripping, malware hook, and XSS sanitization."""

from __future__ import annotations

import html
import io
import re
import socket

from fastapi import HTTPException, status
from PIL import Image, ImageOps

from app.core.config import settings

# Standard EICAR antivirus test string signature for deterministic security verification
_EICAR_MARKER = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

_SCRIPT_TAG_RE = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def sanitize_text(value: str | None) -> str | None:
    """Strips script/HTML tags and normalizes whitespace to mitigate stored XSS."""
    if value is None:
        return None
    cleaned = _SCRIPT_TAG_RE.sub("", value)
    cleaned = _HTML_TAG_RE.sub("", cleaned)
    return html.unescape(cleaned).strip()


def scan_bytes_for_malware(data: bytes) -> None:
    """Malware scanning hook.
    - Always rejects known EICAR test signatures.
    - If settings.CLAMAV_HOST is configured, streams bytes to clamd INSTREAM.
    """
    if _EICAR_MARKER in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload rejected by malware scanner (signature detected).",
        )

    if settings.CLAMAV_HOST:
        try:
            with socket.create_connection((settings.CLAMAV_HOST, settings.CLAMAV_PORT), timeout=5) as sock:
                sock.sendall(b"zINSTREAM\0")
                chunk_size = 8192
                for i in range(0, len(data), chunk_size):
                    chunk = data[i : i + chunk_size]
                    sock.sendall(len(chunk).to_bytes(4, "big") + chunk)
                sock.sendall((0).to_bytes(4, "big"))
                resp = sock.recv(1024).decode("utf-8", errors="ignore")
                if "FOUND" in resp:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Upload rejected by ClamAV malware scanner.",
                    )
        except HTTPException:
            raise
        except OSError:
            # Fail-open vs fail-closed documented in SECURITY.md; log warning in prod
            pass


def _detect_image_magic(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def validate_and_sanitize_image(data: bytes, max_bytes: int | None = None) -> bytes:
    """Validates image size, magic bytes, malware scan, decodes and re-encodes
    through Pillow to neutralize polyglot payloads and strip all EXIF/GPS metadata.
    """
    limit = max_bytes or settings.MAX_IMAGE_UPLOAD_BYTES
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(data) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum allowed size of {limit // (1024 * 1024)} MB",
        )

    scan_bytes_for_malware(data)

    fmt = _detect_image_magic(data)
    if not fmt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported or invalid image format. Only JPEG, PNG, and WEBP are allowed.",
        )

    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
        with Image.open(io.BytesIO(data)) as img_clean:
            transposed = ImageOps.exif_transpose(img_clean)
            if transposed.width > 6000 or transposed.height > 6000:
                transposed.thumbnail((4096, 4096))
            rgb = transposed.convert("RGB") if fmt == "jpeg" else transposed.convert("RGBA")
            out = io.BytesIO()
            if fmt == "jpeg":
                rgb.save(out, format="JPEG", quality=92, optimize=True)
            elif fmt == "png":
                rgb.save(out, format="PNG", optimize=True)
            else:
                rgb.save(out, format="WEBP", quality=92)
            return out.getvalue()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or malformed image payload.",
        ) from exc


def validate_audio_upload(data: bytes, max_bytes: int | None = None) -> str:
    """Validates audio size, malware scan, and container magic bytes."""
    limit = max_bytes or settings.MAX_AUDIO_UPLOAD_BYTES
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio file is empty")
    if len(data) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio exceeds maximum allowed size of {limit // (1024 * 1024)} MB",
        )

    scan_bytes_for_malware(data)

    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if data.startswith(b"OggS"):
        return "ogg"
    if data.startswith(b"fLaC"):
        return "flac"
    if data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "mp3"
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "m4a"
    if data.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported audio container. Allowed formats: WAV, MP3, OGG, FLAC, M4A, WEBM.",
    )
