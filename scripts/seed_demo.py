"""CraftLens 2.0 – Production Demonstration & Pilot Dataset Seeder.

Populates idempotent, realistic artisan craft data across all 6 categories,
including verified master artisans, GI craft origins, Ed25519 digitally signed
provenance records, B2B wholesale buyers, inventory, and order flows.

Usage:
    python scripts/seed_demo.py
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Ensure root and backend are on PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.security import get_password_hash  # noqa: E402
from app.db.init_db import init_db  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    ArtisanProfile,
    Buyer,
    BuyerBusinessProfile,
    Category,
    CraftOrigin,
    Inventory,
    Order,
    OrderItem,
    Payment,
    Product,
    ProductQR,
    ProductVariant,
    ProvenanceRecord,
    PurchaseRequest,
    Role,
    Shipment,
    User,
)
from app.services.heritage_service import create_signed_provenance  # noqa: E402


def seed_demo_data(db: Session) -> dict[str, int]:
    """Idempotently seed rich demonstration dataset."""
    # Ensure base migrations/seed executed
    init_db(db)

    roles = {r.code: r for r in db.query(Role).all()}
    categories = {c.slug: c for c in db.query(Category).all()}
    origins = {o.geographical_indication_code: o for o in db.query(CraftOrigin).all()}

    stats = {
        "artisans_added": 0,
        "buyers_added": 0,
        "products_added": 0,
        "orders_added": 0,
        "rfqs_added": 0,
    }

    # 1. Master Artisans
    artisan_data = [
        {
            "email": "artisan.ravi@craftlens.org",
            "name": "Ravi Shankar Sharma",
            "phone": "+919812345678",
            "lang": "hi",
            "specialization": "Banarasi Katan Silk Brocade",
            "bio": "National Award-winning master weaver preserving 400-year-old Mughal jaal patterns on pit looms.",
            "exp": 28,
            "city": "Varanasi",
            "state": "Uttar Pradesh",
            "pincode": "221001",
            "origin_gi": "GI-002",
        },
        {
            "email": "artisan.nagaraj@craftlens.org",
            "name": "Nagaraj Gowda",
            "phone": "+919823456789",
            "lang": "kn",
            "specialization": "Channapatna Lacquered Toys & Woodcraft",
            "bio": "Crafting eco-friendly ivory wood toys turned on traditional lathe with natural vegetable dyes.",
            "exp": 18,
            "city": "Channapatna",
            "state": "Karnataka",
            "pincode": "562160",
            "origin_gi": "GI-003",
        },
        {
            "email": "artisan.sita@craftlens.org",
            "name": "Sita Devi Mithila",
            "phone": "+919834567890",
            "lang": "hi",
            "specialization": "Mithila Madhubani Folk Painting",
            "bio": "State accredited artist creating intricate Kohbar and Godna folk art with bamboo nibs and natural sap.",
            "exp": 22,
            "city": "Madhubani",
            "state": "Bihar",
            "pincode": "847211",
            "origin_gi": "GI-004",
        },
        {
            "email": "artisan.sukhram@craftlens.org",
            "name": "Sukhram Mandavi",
            "phone": "+919845678901",
            "lang": "hi",
            "specialization": "Bastar Lost-Wax Dhokra Metalcraft",
            "bio": "Ancient non-ferrous metal caster creating heirloom bronze and brass figurines using bee-wax ribbons.",
            "exp": 25,
            "city": "Jagdalpur",
            "state": "Chhattisgarh",
            "pincode": "494001",
            "origin_gi": "GI-005",
        },
        {
            "email": "artisan.kripal@craftlens.org",
            "name": "Kripal Singh Kumhar",
            "phone": "+919856789012",
            "lang": "hi",
            "specialization": "Jaipur Glazed Blue Pottery",
            "bio": "Pioneering blue pottery master artisan crafting Egyptian paste pottery with cobalt oxide glazes.",
            "exp": 30,
            "city": "Jaipur",
            "state": "Rajasthan",
            "pincode": "302001",
            "origin_gi": "GI-006",
        },
    ]

    artisan_profiles = {}
    # Fetch default artisan from init_db
    default_artisan_user = db.query(User).filter(User.email == "artisan@craftlens.org").first()
    if default_artisan_user and default_artisan_user.artisan_profile:
        artisan_profiles["meenakshi"] = default_artisan_user.artisan_profile

    for item in artisan_data:
        u = db.query(User).filter(User.email == item["email"]).first()
        if not u:
            u = User(
                email=item["email"],
                full_name=item["name"],
                phone=item["phone"],
                hashed_password=get_password_hash("Artisan@2026"),
                preferred_language=item["lang"],
                is_active=True,
                is_verified=True,
            )
            u.roles.append(roles["ARTISAN"])
            db.add(u)
            db.flush()

            profile = ArtisanProfile(
                user_id=u.id,
                craft_specialization=item["specialization"],
                bio=item["bio"],
                experience_years=item["exp"],
                city=item["city"],
                state=item["state"],
                pincode=item["pincode"],
                verification_level="GOVT_ID_VERIFIED",
            )
            db.add(profile)
            db.flush()
            stats["artisans_added"] += 1
            artisan_profiles[item["email"]] = profile
        else:
            artisan_profiles[item["email"]] = u.artisan_profile

    # 2. Buyers (Retail & B2B Wholesale)
    retail_email = "buyer@craftlens.org"
    retail_user = db.query(User).filter(User.email == retail_email).first()
    if not retail_user:
        retail_user = User(
            email=retail_email,
            full_name="Ananya Sharma",
            phone="+919876500001",
            hashed_password=get_password_hash("Buyer@2026"),
            preferred_language="en",
            is_active=True,
            is_verified=True,
        )
        retail_user.roles.append(roles["RETAIL_BUYER"])
        db.add(retail_user)
        db.flush()
        addr = {
            "street": "42, Indiranagar 100ft Road",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560038",
            "country": "India",
        }
        db.add(
            Buyer(
                user_id=retail_user.id,
                buyer_type="RETAIL",
                default_shipping_address=addr,
                default_billing_address=addr,
            )
        )
        stats["buyers_added"] += 1

    wholesale_email = "wholesale@craftlens.org"
    wholesale_user = db.query(User).filter(User.email == wholesale_email).first()
    if not wholesale_user:
        wholesale_user = User(
            email=wholesale_email,
            full_name="Vikram Birla",
            phone="+919876500002",
            hashed_password=get_password_hash("Wholesale@2026"),
            preferred_language="en",
            is_active=True,
            is_verified=True,
        )
        wholesale_user.roles.append(roles["WHOLESALE_BUYER"])
        db.add(wholesale_user)
        db.flush()
        b_addr = {
            "street": "88, Nariman Point Commercial Complex",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400021",
            "country": "India",
        }
        b = Buyer(
            user_id=wholesale_user.id,
            buyer_type="WHOLESALE",
            default_shipping_address=b_addr,
            default_billing_address=b_addr,
        )
        db.add(b)
        db.flush()
        db.add(
            BuyerBusinessProfile(
                buyer_id=b.id,
                company_name="Craft Traditions B2B Exports Pvt Ltd",
                gst_number="27AAACR1234F1Z5",
                pan_number="AAACR1234F",
                verified_status="VERIFIED",
                website="https://crafttraditions.example.com",
            )
        )
        stats["buyers_added"] += 1

    # 3. Rich Products Across All 6 Categories
    meenakshi = artisan_profiles.get("meenakshi")
    ravi = artisan_profiles.get("artisan.ravi@craftlens.org")
    nagaraj = artisan_profiles.get("artisan.nagaraj@craftlens.org")
    sita = artisan_profiles.get("artisan.sita@craftlens.org")
    sukhram = artisan_profiles.get("artisan.sukhram@craftlens.org")
    kripal = artisan_profiles.get("artisan.kripal@craftlens.org")

    product_catalog = [
        {
            "slug": "kanchipuram-pure-silk-temple-saree",
            "title": "Kanchipuram Temple Border Pure Mulberry Silk Saree",
            "desc": "Handwoven 3-ply pure mulberry silk saree featuring genuine gold and silver zari border in classic Korvai interlock technique.",
            "category": "handloom-textiles",
            "origin": "GI-001",
            "artisan": meenakshi,
            "price": 14500.0,
            "sku": "KNC-SLK-001",
            "materials": "100% Mulberry Silk, Pure Gold & Silver Zari",
            "dimensions": "6.2m length x 1.2m width (includes blouse piece)",
            "hours": 52.0,
            "tags": ["saree", "silk", "handloom", "kanchipuram", "wedding"],
        },
        {
            "slug": "varanasi-katan-silk-floral-jaal-dupatta",
            "title": "Varanasi Katan Silk Handwoven Floral Jaal Dupatta",
            "desc": "Masterpiece Banarasi brocade stole woven on traditional drawloom with intricate floral lattice (jaal) motifs in antique gold zari.",
            "category": "handloom-textiles",
            "origin": "GI-002",
            "artisan": ravi,
            "price": 6800.0,
            "sku": "BAN-KAT-002",
            "materials": "Pure Katan Silk, Metallic Zari Weft",
            "dimensions": "2.5m length x 0.9m width",
            "hours": 36.0,
            "tags": ["dupatta", "banarasi", "katan silk", "heritage"],
        },
        {
            "slug": "channapatna-natural-lacquered-rocking-horse",
            "title": "Channapatna Natural Lacquered Wooden Rocking Horse",
            "desc": "Child-safe non-toxic artisan rocking horse hand-turned on lathe from seasoned Wrightia tinctoria (ivory-wood) and tinted with turmeric and indigo vegetable lacquer.",
            "category": "woodcraft-toys",
            "origin": "GI-003",
            "artisan": nagaraj,
            "price": 1450.0,
            "sku": "CHN-TOY-003",
            "materials": "Wrightia Tinctoria Wood, Natural Shellac, Turmeric & Indigo Pigments",
            "dimensions": "32cm x 12cm x 24cm",
            "hours": 14.0,
            "tags": ["toys", "wooden", "channapatna", "eco-friendly", "kids"],
        },
        {
            "slug": "jaipur-floral-glazed-blue-pottery-vase",
            "title": "Jaipur Cobalt & Turquoise Floral Glazed Blue Pottery Vase",
            "desc": "Heirloom glazed pottery vase crafted without clay using traditional Egyptian paste, quartz powder, glass, and Fuller's earth, hand-painted with Persian floral motifs.",
            "category": "terracotta-pottery",
            "origin": "GI-006",
            "artisan": kripal,
            "price": 2200.0,
            "sku": "JPR-POT-004",
            "materials": "Quartz Stone Powder, Cullet Glass, Sajji Glaze, Cobalt Oxide",
            "dimensions": "28cm height x 14cm diameter",
            "hours": 18.0,
            "tags": ["pottery", "blue pottery", "jaipur", "home decor", "vase"],
        },
        {
            "slug": "bastar-tribal-musician-dhokra-figurine",
            "title": "Bastar Tribal Musician Dhokra Lost-Wax Bell Metal Figurine",
            "desc": "Unique 4,000-year-old lost-wax technique casting depicting a traditional Bastar dholak player. Every figurine is unique as the clay mold is broken during casting.",
            "category": "metal-brassware",
            "origin": "GI-005",
            "artisan": sukhram,
            "price": 3850.0,
            "sku": "BST-DHK-005",
            "materials": "Bell Metal Bronze (Copper-Tin Alloy), Natural Beeswax Pattern",
            "dimensions": "22cm x 10cm x 8cm",
            "hours": 24.0,
            "tags": ["dhokra", "lost-wax", "tribal art", "metalcraft", "bastar"],
        },
        {
            "slug": "madhubani-kohbar-traditional-mithila-canvas",
            "title": "Madhubani Kohbar Traditional Mithila Painting on Handmade Canvas",
            "desc": "Sacred bridal chamber Kohbar folk painting hand-drawn with bamboo sticks and natural river-silt and plant pigments on sun-dried cow-dung treated handmade paper.",
            "category": "traditional-painting",
            "origin": "GI-004",
            "artisan": sita,
            "price": 4500.0,
            "sku": "MDB-PNT-006",
            "materials": "Handmade Cotton Rag Paper, Lampblack, Haritaki & Turmeric Dyes",
            "dimensions": "45cm x 60cm framed",
            "hours": 30.0,
            "tags": ["madhubani", "mithila", "painting", "folk art", "handmade"],
        },
        {
            "slug": "assam-river-cane-handwoven-fruit-basket",
            "title": "Assam River Cane Handwoven Geometric Fruit & Bread Basket",
            "desc": "Sustainable, zero-carbon multipurpose shallow basket handcrafted from split river cane and golden bamboo by Northeast indigenous artisans.",
            "category": "cane-bamboo",
            "origin": None,
            "artisan": nagaraj,
            "price": 850.0,
            "sku": "ASM-BMB-007",
            "materials": "Natural Split Cane, Assam Golden Bamboo",
            "dimensions": "30cm diameter x 8cm depth",
            "hours": 8.0,
            "tags": ["bamboo", "cane", "sustainable", "basket", "organic"],
        },
    ]

    persisted_products = []
    for item in product_catalog:
        artisan_obj = item["artisan"]
        if not artisan_obj:
            continue

        cat_obj = categories.get(item["category"])
        orig_obj = origins.get(item["origin"]) if item["origin"] else None

        prod = db.query(Product).filter(Product.slug == item["slug"]).first()
        if not prod:
            prod = Product(
                artisan_id=artisan_obj.id,
                category_id=cat_obj.id if cat_obj else None,
                craft_origin_id=orig_obj.id if orig_obj else None,
                title=item["title"],
                slug=item["slug"],
                summary=item["desc"],
                primary_material=item["materials"],
                technique="Traditional Handcrafted Masterpiece",
                dimensions=item["dimensions"],
                weight_grams=item.get("weight", 650),
                status="ACTIVE",
                gi_claim_code=orig_obj.geographical_indication_code if orig_obj else None,
                gi_verification_status="APPROVED" if orig_obj else "NONE",
            )
            db.add(prod)
            db.flush()

            variant = ProductVariant(
                product_id=prod.id,
                sku=item["sku"],
                title="Masterpiece Edition",
                price_retail=item["price"],
                price_wholesale=round(item["price"] * 0.8, 2),
                min_wholesale_qty=5,
                stock_quantity=15,
            )
            db.add(variant)
            db.flush()

            inv = Inventory(
                product_variant_id=variant.id,
                quantity_on_hand=15,
                reserved_quantity=0,
                low_stock_threshold=3,
            )
            db.add(inv)

            # Digital Provenance Signature (Ed25519)
            prov = create_signed_provenance(
                artisan_id=str(artisan_obj.id),
                product_id=str(prod.id),
                batch_code=f"BATCH-{prod.slug[:8].upper()}-01",
                raw_material_source=item["materials"],
            )

            qr = ProductQR(
                product_id=prod.id,
                qr_code_hash=prov["maker_signature_hash"],
                public_url=f"/heritage/verify/{prov['maker_signature_hash']}",
                scan_count=14,
            )
            db.add(qr)
            db.flush()

            record = ProvenanceRecord(
                product_id=prod.id,
                batch_code=f"BATCH-{prod.slug[:8].upper()}-01",
                raw_materials_source=item["materials"],
                craft_technique_details=f"Authenticity verified at artisan workshop in {artisan_obj.city}, {artisan_obj.state}.",
                maker_signature_hash=prov["maker_signature_hash"],
                signed_payload=prov["signed_payload"],
                signature_ed25519=prov["signature_ed25519"],
                public_key_fingerprint=prov["public_key_fingerprint"],
            )
            db.add(record)

            stats["products_added"] += 1
            persisted_products.append(prod)
        else:
            persisted_products.append(prod)

    # 4. Realistic Demonstration Orders
    if persisted_products and retail_user and retail_user.buyer_profile:
        buyer_p = retail_user.buyer_profile
        existing_orders = db.query(Order).filter(Order.buyer_id == buyer_p.id).count()

        if existing_orders == 0:
            addr = {
                "street": "42, Indiranagar 100ft Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "pincode": "560038",
                "country": "India",
            }
            # Order 1: Delivered Handloom Saree
            saree_prod = persisted_products[0]
            saree_var = saree_prod.variants[0] if saree_prod.variants else None
            if saree_var:
                price = float(saree_var.price_retail)
                ord1 = Order(
                    order_number=f"ORD-DEL-{int(datetime.now(UTC).timestamp())}",
                    buyer_id=buyer_p.id,
                    order_type="RETAIL",
                    status="DELIVERED",
                    subtotal=price,
                    discount=0.0,
                    tax=0.0,
                    shipping_fee=0.0,
                    total_amount=price,
                    delivery_address=addr,
                    created_at=datetime.now(UTC) - timedelta(days=7),
                )
                db.add(ord1)
                db.flush()

                db.add(
                    OrderItem(
                        order_id=ord1.id,
                        product_variant_id=saree_var.id,
                        artisan_id=saree_prod.artisan_id,
                        quantity=1,
                        unit_price=price,
                        total_price=price,
                    )
                )

                db.add(
                    Payment(
                        order_id=ord1.id,
                        amount=price,
                        currency="INR",
                        payment_gateway="RAZORPAY_UPI",
                        transaction_ref=f"txn_{ord1.order_number}",
                        gateway_payment_id="pay_demo_test_001",
                        status="SUCCESS",
                        paid_at=datetime.now(UTC) - timedelta(days=7),
                    )
                )

                db.add(
                    Shipment(
                        order_id=ord1.id,
                        shipping_provider="SHIPROCKET_SANDBOX",
                        carrier="Delhivery Express",
                        tracking_number="SR-EXP-7729104",
                        status="DELIVERED",
                        shipped_at=datetime.now(UTC) - timedelta(days=5),
                        delivered_at=datetime.now(UTC) - timedelta(days=1),
                    )
                )
                stats["orders_added"] += 1

            # Order 2: In-Transit Channapatna Toy
            toy_prod = persisted_products[2] if len(persisted_products) > 2 else persisted_products[0]
            toy_var = toy_prod.variants[0] if toy_prod.variants else None
            if toy_var:
                toy_price = float(toy_var.price_retail)
                toy_total = toy_price * 2
                ord2 = Order(
                    order_number=f"ORD-SHP-{int(datetime.now(UTC).timestamp()) + 1}",
                    buyer_id=buyer_p.id,
                    order_type="RETAIL",
                    status="SHIPPED",
                    subtotal=toy_total,
                    discount=0.0,
                    tax=0.0,
                    shipping_fee=0.0,
                    total_amount=toy_total,
                    delivery_address=addr,
                    created_at=datetime.now(UTC) - timedelta(days=2),
                )
                db.add(ord2)
                db.flush()

                db.add(
                    OrderItem(
                        order_id=ord2.id,
                        product_variant_id=toy_var.id,
                        artisan_id=toy_prod.artisan_id,
                        quantity=2,
                        unit_price=toy_price,
                        total_price=toy_total,
                    )
                )

                db.add(
                    Payment(
                        order_id=ord2.id,
                        amount=toy_total,
                        currency="INR",
                        payment_gateway="RAZORPAY_UPI",
                        transaction_ref=f"txn_{ord2.order_number}",
                        gateway_payment_id="pay_demo_test_002",
                        status="SUCCESS",
                        paid_at=datetime.now(UTC) - timedelta(days=2),
                    )
                )

                db.add(
                    Shipment(
                        order_id=ord2.id,
                        shipping_provider="SHIPROCKET_SANDBOX",
                        carrier="India Post Speed Post",
                        tracking_number="SR-EXP-8841923",
                        status="IN_TRANSIT",
                        shipped_at=datetime.now(UTC) - timedelta(days=1),
                    )
                )
                stats["orders_added"] += 1

    # 5. B2B Wholesale Purchase Request (RFQ)
    if wholesale_user and wholesale_user.buyer_profile and len(persisted_products) > 2:
        toy_prod = persisted_products[2]
        existing_rfq = (
            db.query(PurchaseRequest).filter(PurchaseRequest.buyer_id == wholesale_user.buyer_profile.id).first()
        )
        if not existing_rfq:
            rfq = PurchaseRequest(
                buyer_id=wholesale_user.buyer_profile.id,
                product_id=toy_prod.id,
                target_quantity=50,
                target_unit_price=1100.0,
                specifications="Bulk export order for retail showcase across 4 boutique handicraft stores in Mumbai and Delhi. Requires custom packaging with GI authenticity certificates.",
                status="OPEN",
            )
            db.add(rfq)
            stats["rfqs_added"] += 1

    db.commit()
    return stats


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("[SEED] Starting CraftLens 2.0 demonstration dataset seeder...")
        res = seed_demo_data(db)
        print(f"[SEED] Success! Summary of seeded records: {res}")
    finally:
        db.close()
