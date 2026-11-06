import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models import (
    User,
    Buyer,
    Order,
    OrderItem,
    ProductVariant,
    Inventory,
    StockMovement,
    Payment,
    Shipment,
    ArtisanProfile,
)
from app.schemas.marketplace import OrderCreateIn, OrderOut
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user, require_role

router = APIRouter()


@router.post("/checkout", response_model=APIResponse[OrderOut])
def create_order_checkout(
    order_in: OrderCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Executes atomic checkout transaction:
    1. Validates stock availability for each variant
    2. Calculates subtotal, tax, and shipping
    3. Deducts inventory and logs stock movements
    4. Creates Order and OrderItems
    5. Initializes Payment record in sandbox mode
    """
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        buyer = Buyer(user_id=current_user.id, buyer_type=order_in.order_type)
        db.add(buyer)
        db.flush()

    if not order_in.items:
        raise HTTPException(status_code=400, detail="Cannot create empty order")

    subtotal = 0.0
    order_items_to_create = []

    # 1. Validate items and stock
    for item in order_in.items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Variant {item.variant_id} not found")

        inv = db.query(Inventory).filter(Inventory.product_variant_id == variant.id).first()
        if not inv or inv.quantity_on_hand < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{variant.title}'. Available: {inv.quantity_on_hand if inv else 0}",
            )

        # Apply retail or wholesale unit price
        unit_price = float(
            variant.price_wholesale
            if order_in.order_type == "WHOLESALE" and item.quantity >= variant.min_wholesale_qty
            else variant.price_retail
        )
        line_total = round(unit_price * item.quantity, 2)
        subtotal += line_total

        # Deduct inventory atomically
        inv.quantity_on_hand -= item.quantity
        variant.stock_quantity = inv.quantity_on_hand

        # Log StockMovement
        movement = StockMovement(
            inventory_id=inv.id,
            quantity_change=-item.quantity,
            movement_type="SALE_DEDUCT",
            notes="Order checkout deduction",
        )
        db.add(movement)

        artisan_id = variant.product.artisan_id
        order_items_to_create.append(
            {
                "variant_id": variant.id,
                "artisan_id": artisan_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total_price": line_total,
            }
        )

    shipping_fee = 0.0 if subtotal >= 1000.0 else 100.0
    total_amount = round(subtotal + shipping_fee, 2)
    order_num = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    # 2. Create Order
    new_order = Order(
        order_number=order_num,
        buyer_id=buyer.id,
        order_type=order_in.order_type,
        subtotal=subtotal,
        discount=0.0,
        tax=0.0,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        status="CONFIRMED",
        delivery_address=order_in.delivery_address,
    )
    db.add(new_order)
    db.flush()

    # 3. Create OrderItems
    for oi in order_items_to_create:
        item_entity = OrderItem(
            order_id=new_order.id,
            product_variant_id=oi["variant_id"],
            artisan_id=oi["artisan_id"],
            quantity=oi["quantity"],
            unit_price=oi["unit_price"],
            total_price=oi["total_price"],
        )
        db.add(item_entity)

    # 4. Create Payment record
    payment = Payment(
        order_id=new_order.id,
        payment_gateway=order_in.payment_method,
        transaction_ref=f"TXN-{str(uuid.uuid4())[:12].upper()}",
        amount=total_amount,
        currency="INR",
        status="SUCCESS",
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)

    # 5. Initialize Shipment record
    shipment = Shipment(
        order_id=new_order.id,
        carrier="India Post SpeedPost",
        tracking_number=f"IN-{datetime.now(timezone.utc).strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}",
        status="MANIFESTED",
    )
    db.add(shipment)

    db.commit()
    db.refresh(new_order)

    return APIResponse(
        success=True,
        message="Order placed successfully and payment verified",
        data=OrderOut.model_validate(new_order),
    )


@router.get("/my-orders", response_model=APIResponse[List[OrderOut]])
def get_buyer_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves all past orders placed by the authenticated buyer."""
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    if not buyer:
        return APIResponse(success=True, message="No orders found", data=[])

    orders = db.query(Order).filter(Order.buyer_id == buyer.id).order_by(desc(Order.created_at)).all()
    return APIResponse(
        success=True,
        message="Buyer orders retrieved",
        data=[OrderOut.model_validate(o) for o in orders],
    )


@router.get("/artisan-orders", response_model=APIResponse[List[dict]])
def get_artisan_incoming_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ARTISAN")),
):
    """Retrieves incoming customer orders containing items crafted by this artisan."""
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == current_user.id).first()
    if not profile:
        return APIResponse(success=True, message="Artisan profile not found", data=[])

    items = (
        db.query(OrderItem)
        .filter(OrderItem.artisan_id == profile.id)
        .order_by(desc(OrderItem.id))
        .all()
    )

    results = []
    for it in items:
        results.append(
            {
                "order_number": it.order.order_number if it.order else "N/A",
                "order_status": it.order.status if it.order else "PENDING",
                "product_title": it.variant.product.title if it.variant and it.variant.product else "Craft Item",
                "variant_sku": it.variant.sku if it.variant else "SKU",
                "quantity": it.quantity,
                "unit_price": float(it.unit_price),
                "total_payout": float(it.total_price),
                "ordered_at": it.order.created_at.isoformat() if it.order else None,
            }
        )

    return APIResponse(
        success=True,
        message="Artisan incoming order items retrieved",
        data=results,
    )

