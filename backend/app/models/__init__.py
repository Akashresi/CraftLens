from app.db.base import Base
from app.models.user import User, Role, Permission, user_roles, role_permissions, AuditLog, ConsentRecord
from app.models.artisan import ArtisanGroup, ArtisanProfile, ArtisanVerification, ArtisanStory
from app.models.buyer import Buyer, BuyerBusinessProfile
from app.models.category import Category, CraftOrigin
from app.models.product import Product, ProductVariant, ProductImage, ProductTranslation, GeneratedDescription
from app.models.pricing import CostComponent, PricingEstimate, PricingHistory, MarketComparable
from app.models.inventory import Inventory, StockMovement
from app.models.order import Order, OrderItem, Payment, Shipment
from app.models.b2b import PurchaseRequest, Quotation, PurchaseOrder
from app.models.heritage import ProvenanceRecord, ProductQR
from app.models.marketing import MarketingCampaign, MarketingAsset, BusinessExpense, DemandPrediction
from app.models.ai_job import ImageProcessingJob, AIJob
from app.models.review import Review, Notification

__all__ = [
    "Base",
    "User",
    "Role",
    "Permission",
    "user_roles",
    "role_permissions",
    "AuditLog",
    "ConsentRecord",
    "ArtisanGroup",
    "ArtisanProfile",
    "ArtisanVerification",
    "ArtisanStory",
    "Buyer",
    "BuyerBusinessProfile",
    "Category",
    "CraftOrigin",
    "Product",
    "ProductVariant",
    "ProductImage",
    "ProductTranslation",
    "GeneratedDescription",
    "CostComponent",
    "PricingEstimate",
    "PricingHistory",
    "MarketComparable",
    "Inventory",
    "StockMovement",
    "Order",
    "OrderItem",
    "Payment",
    "Shipment",
    "PurchaseRequest",
    "Quotation",
    "PurchaseOrder",
    "ProvenanceRecord",
    "ProductQR",
    "MarketingCampaign",
    "MarketingAsset",
    "BusinessExpense",
    "DemandPrediction",
    "ImageProcessingJob",
    "AIJob",
    "Review",
    "Notification",
]

