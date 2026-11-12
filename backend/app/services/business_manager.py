from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    BusinessExpense,
    OrderItem,
    Product,
)


def get_artisan_dashboard_metrics(artisan_id: str, db: Session) -> dict[str, Any]:
    """Aggregates real-time business performance metrics for an artisan:
    - Today's sales & total monthly revenue
    - Pending vs fulfilled orders
    - Active product count
    - Inventory items below low-stock threshold
    - Recorded business expenses
    """
    now = datetime.now(UTC)
    today_start = datetime(now.year, now.month, now.day, tzinfo=UTC)
    month_start = datetime(now.year, now.month, 1, tzinfo=UTC)

    # All items sold by this artisan
    artisan_items = db.query(OrderItem).filter(OrderItem.artisan_id == artisan_id).all()

    total_revenue = sum((float(i.total_price) for i in artisan_items), 0.0)
    today_revenue = sum(
        (float(i.total_price) for i in artisan_items if i.order and i.order.created_at >= today_start),
        0.0,
    )
    month_revenue = sum(
        (float(i.total_price) for i in artisan_items if i.order and i.order.created_at >= month_start),
        0.0,
    )

    total_orders_count = len(set(i.order_id for i in artisan_items))
    pending_orders_count = len(
        set(i.order_id for i in artisan_items if i.order and i.order.status in ["PENDING", "CONFIRMED"])
    )

    # Active products
    products = db.query(Product).filter(Product.artisan_id == artisan_id).all()
    active_products_count = sum(1 for p in products if p.status == "ACTIVE")

    # Low stock items
    low_stock_items = []
    for p in products:
        for v in p.variants:
            if v.inventory_record and v.inventory_record.quantity_on_hand <= v.inventory_record.low_stock_threshold:
                low_stock_items.append(
                    {
                        "product_title": p.title,
                        "variant_sku": v.sku,
                        "quantity_on_hand": v.inventory_record.quantity_on_hand,
                        "threshold": v.inventory_record.low_stock_threshold,
                    }
                )

    # Expenses
    expenses = db.query(BusinessExpense).filter(BusinessExpense.artisan_id == artisan_id).all()
    total_expenses = sum(float(e.amount) for e in expenses)
    estimated_net_profit = round(max(0.0, total_revenue - total_expenses), 2)

    return {
        "today_revenue": round(today_revenue, 2),
        "month_revenue": round(month_revenue, 2),
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "estimated_net_profit": estimated_net_profit,
        "total_orders_count": total_orders_count,
        "pending_orders_count": pending_orders_count,
        "active_products_count": active_products_count,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
    }


def answer_business_assistant_query(query: str, artisan_id: str, db: Session) -> dict[str, Any]:
    """Answers artisan business questions using actual verified database records."""
    metrics = get_artisan_dashboard_metrics(artisan_id=artisan_id, db=db)
    q = query.lower()

    if any(k in q for k in ["earn", "revenue", "income", "sales", "வருமானம்", "கையிருப்பு", "कमाई"]):
        answer = (
            f"You have earned ₹{metrics['today_revenue']:,.2f} today. "
            f"Your total monthly revenue is ₹{metrics['month_revenue']:,.2f}, with an estimated net profit of ₹{metrics['estimated_net_profit']:,.2f}."
        )
    elif any(k in q for k in ["pending", "order", "ஆர்டர்", "कितने आर्डर"]):
        answer = (
            f"You have {metrics['pending_orders_count']} pending order(s) requiring dispatch. "
            f"Total lifetime completed orders: {metrics['total_orders_count']}."
        )
    elif any(k in q for k in ["stock", "inventory", "low", "இருப்பு", "स्टॉक"]):
        if metrics["low_stock_count"] > 0:
            names = ", ".join(i["product_title"] for i in metrics["low_stock_items"][:3])
            answer = (
                f"Warning: {metrics['low_stock_count']} item(s) have low stock: {names}. Consider creating more units."
            )
        else:
            answer = "All your products have healthy inventory levels above the minimum threshold."
    else:
        answer = (
            f"Studio Overview: Monthly sales ₹{metrics['month_revenue']:,.2f}, "
            f"{metrics['pending_orders_count']} pending orders, and {metrics['active_products_count']} active listings in marketplace."
        )

    return {"query": query, "answer": answer, "metrics_snapshot": metrics}


def create_promotional_copy(
    product_title: str,
    craft_technique: str,
    platform: str = "INSTAGRAM",
    festival: str | None = None,
    language: str = "en",
) -> dict[str, Any]:
    """Generates engaging marketing and social media copy with hashtags."""
    fest_str = f" for {festival}" if festival else ""

    if platform.upper() == "WHATSAPP":
        caption = (
            f"🙏 *Namaste! Direct from Master Artisans*\n\n"
            f"Explore our authentic *{product_title}*, handcrafted using traditional {craft_technique}{fest_str}.\n\n"
            f"✨ 100% Genuine Handmade\n"
            f"🛡️ Cryptographic QR Authenticity Verified\n"
            f"📦 Pan-India & Worldwide Doorstep Shipping\n\n"
            f"Reply to this message or order directly on CraftLens!"
        )
    else:  # Instagram / Facebook
        caption = (
            f"Centuries of living heritage woven into every contour. 🎨✨\n\n"
            f"Presenting the *{product_title}*, individually crafted using timeless {craft_technique}{fest_str}.\n"
            f"When you purchase from CraftLens, 100% of fair value reaches the indigenous artisan family.\n\n"
            f"Tap the link in bio to explore the maker story and verify authenticity.\n\n"
            f"#CraftLens #HandmadeInIndia #VocalForLocal #ArtisanMade #IndianHeritage #SustainableCraft #{craft_technique.replace(' ', '')}"
        )

    return {
        "platform": platform,
        "festival": festival,
        "generated_content": caption,
        "suggested_hashtags": ["#CraftLens", "#HandmadeInIndia", "#VocalForLocal", "#ArtisanMade"],
    }
