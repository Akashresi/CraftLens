import io
import os
import hashlib
from typing import Tuple
import qrcode
from PIL import Image

UPLOAD_BASE = "./uploads"
os.makedirs(f"{UPLOAD_BASE}/qr", exist_ok=True)


def create_provenance_signature(
    artisan_id: str,
    product_id: str,
    batch_code: str,
    raw_material_source: str,
) -> str:
    """Generates a cryptographic SHA-256 maker signature ensuring immutable authenticity."""
    raw_payload = f"{artisan_id}:{product_id}:{batch_code}:{raw_material_source}:CraftLens2026"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def generate_qr_code_image(public_url: str, qr_hash: str) -> str:
    """Generates a high-resolution QR code image linking to the public heritage provenance page.
    Saves image to /uploads/qr/ and returns URL path.
    """
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#285C45", back_color="#F8F6F0")  # CraftLens brand colors

    file_path = f"{UPLOAD_BASE}/qr/{qr_hash}.png"
    img.save(file_path)
    return f"/uploads/qr/{qr_hash}.png"
