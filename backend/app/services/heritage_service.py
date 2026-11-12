"""Cryptographic Ed25519 provenance signing, verification, public key export, and QR generation."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import UTC, datetime

import qrcode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from app.core.config import settings

UPLOAD_BASE = settings.LOCAL_UPLOAD_DIR or "./uploads"
os.makedirs(f"{UPLOAD_BASE}/qr", exist_ok=True)

_KEY_FILE = os.path.join(UPLOAD_BASE, ".heritage_ed25519_dev.pem")
_CACHED_PRIVATE_KEY: Ed25519PrivateKey | None = None


def _get_private_key() -> Ed25519PrivateKey:
    """Loads Ed25519 signing key from environment or creates/caches a local dev keypair."""
    global _CACHED_PRIVATE_KEY
    if _CACHED_PRIVATE_KEY is not None:
        return _CACHED_PRIVATE_KEY

    env_pem = settings.HERITAGE_ED25519_PRIVATE_KEY_PEM.strip()
    if env_pem:
        normalized = env_pem.replace("\\n", "\n").encode("utf-8")
        loaded = serialization.load_pem_private_key(normalized, password=None)
        if not isinstance(loaded, Ed25519PrivateKey):
            raise ValueError("HERITAGE_ED25519_PRIVATE_KEY_PEM must be an Ed25519 private key")
        _CACHED_PRIVATE_KEY = loaded
        return loaded

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            loaded = serialization.load_pem_private_key(f.read(), password=None)
            if isinstance(loaded, Ed25519PrivateKey):
                _CACHED_PRIVATE_KEY = loaded
                return loaded

    key = Ed25519PrivateKey.generate()
    pem_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    os.makedirs(os.path.dirname(_KEY_FILE), exist_ok=True)
    with open(_KEY_FILE, "wb") as f:
        f.write(pem_bytes)
    _CACHED_PRIVATE_KEY = key
    return key


def get_public_key_info() -> dict[str, str]:
    """Returns PEM-encoded Ed25519 public verification key and SHA-256 fingerprint."""
    pub = _get_private_key().public_key()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    fingerprint = hashlib.sha256(pub_pem.encode("utf-8")).hexdigest()[:32]
    return {
        "algorithm": "Ed25519",
        "public_key_pem": pub_pem,
        "public_key_fingerprint": fingerprint,
    }


def create_signed_provenance(
    artisan_id: str,
    product_id: str,
    batch_code: str,
    raw_material_source: str,
) -> dict[str, str]:
    """Constructs a canonical JSON provenance claim and signs it with the platform Ed25519 key."""
    payload_obj = {
        "v": 2,
        "artisan_id": artisan_id,
        "product_id": product_id,
        "batch_code": batch_code,
        "raw_material_source": raw_material_source,
        "issued_at": datetime.now(UTC).isoformat(),
    }
    canonical_payload = json.dumps(payload_obj, sort_keys=True, separators=(",", ":"))
    priv = _get_private_key()
    signature_bytes = priv.sign(canonical_payload.encode("utf-8"))
    signature_b64 = base64.urlsafe_b64encode(signature_bytes).decode("ascii")
    payload_digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
    pub_info = get_public_key_info()

    return {
        "signed_payload": canonical_payload,
        "signature_ed25519": signature_b64,
        "public_key_fingerprint": pub_info["public_key_fingerprint"],
        "maker_signature_hash": payload_digest,
    }


def verify_provenance_signature(signed_payload: str | None, signature_ed25519: str | None) -> bool:
    """Verifies an Ed25519 provenance signature against the active public key."""
    if not signed_payload or not signature_ed25519:
        return False
    try:
        pub: Ed25519PublicKey = _get_private_key().public_key()
        sig_bytes = base64.urlsafe_b64decode(signature_ed25519.encode("ascii"))
        pub.verify(sig_bytes, signed_payload.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def create_provenance_signature(
    artisan_id: str,
    product_id: str,
    batch_code: str,
    raw_material_source: str,
) -> str:
    """Backward-compatible wrapper returning SHA-256 digest of the canonical claim."""
    return create_signed_provenance(artisan_id, product_id, batch_code, raw_material_source)["maker_signature_hash"]


def generate_qr_code_image(public_url: str, qr_hash: str) -> str:
    """Generates a high-resolution QR code image linking to the public heritage provenance page."""
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#285C45", back_color="#F8F6F0")

    file_path = f"{UPLOAD_BASE}/qr/{qr_hash}.png"
    img.save(file_path)
    return f"/uploads/qr/{qr_hash}.png"
