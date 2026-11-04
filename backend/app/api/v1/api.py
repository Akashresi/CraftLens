from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    artisans,
    buyers,
    studio,
    voice,
    pricing,
    marketplace,
    orders,
    b2b,
    heritage,
    business,
    compliance,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Access"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(artisans.router, prefix="/artisans", tags=["Artisans"])
api_router.include_router(buyers.router, prefix="/buyers", tags=["Buyers"])
api_router.include_router(studio.router, prefix="/studio", tags=["AI Product Studio"])
api_router.include_router(voice.router, prefix="/voice", tags=["Multilingual Voice AI"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Dynamic Pricing Engine"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace Discovery"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders & Commerce"])
api_router.include_router(b2b.router, prefix="/b2b", tags=["B2B Wholesale & RFQ"])
api_router.include_router(heritage.router, prefix="/heritage", tags=["Heritage Identity & QR"])
api_router.include_router(business.router, prefix="/business", tags=["AI Business Manager & Marketing"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance, Privacy & Consent"])
