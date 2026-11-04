from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.db.session import get_db
from app.models import Product, ProductVariant, Category, CraftOrigin, ArtisanProfile, User
from app.schemas.marketplace import CategoryOut, ProductPublicOut
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter()


@router.get("/categories", response_model=APIResponse[List[CategoryOut]])
def list_categories(db: Session = Depends(get_db)):
    """Lists all active craft categories with descriptions and icon metadata."""
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order).all()
    return APIResponse(
        success=True,
        message="Categories retrieved",
        data=[CategoryOut.model_validate(c) for c in categories],
    )


@router.get("/products", response_model=APIResponse[PaginatedResponse[ProductPublicOut]])
def discover_products(
    category_slug: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: str = "newest",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """Public marketplace product discovery endpoint with pagination, keyword search,
    category filters, and price ranges.
    """
    # Safe int conversion in case Query wrapper passed
    p = int(getattr(page, "default", page))
    ps = int(getattr(page_size, "default", page_size))

    query = db.query(Product).filter(Product.status == "ACTIVE")

    if category_slug:
        query = query.join(Category).filter(Category.slug == category_slug)

    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                Product.title.ilike(term),
                Product.summary.ilike(term),
                Product.primary_material.ilike(term),
                Product.technique.ilike(term),
            )
        )

    total = query.count()

    if sort == "newest":
        query = query.order_by(desc(Product.created_at))
    else:
        query = query.order_by(desc(Product.created_at))

    offset = (p - 1) * ps
    products = query.offset(offset).limit(ps).all()

    # Enrich with artisan metadata
    output_items = []
    for prod in products:
        item = ProductPublicOut.model_validate(prod)
        if prod.artisan:
            item.artisan_city = prod.artisan.city
            item.artisan_verification_level = prod.artisan.verification_level
            if prod.artisan.user:
                item.artisan_name = prod.artisan.user.full_name
        output_items.append(item)

    pages = (total + ps - 1) // ps if total > 0 else 1

    return APIResponse(
        success=True,
        message="Products retrieved successfully",
        data=PaginatedResponse(
            items=output_items,
            total=total,
            page=p,
            page_size=ps,
            pages=pages,
        ),
    )


@router.get("/products/{slug_or_id}", response_model=APIResponse[ProductPublicOut])
def get_product_detail(
    slug_or_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves full details of a single product including variants, images, and artisan story."""
    product = (
        db.query(Product)
        .filter(or_(Product.slug == slug_or_id, Product.id == slug_or_id))
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.view_count += 1
    db.commit()

    item = ProductPublicOut.model_validate(product)
    if product.artisan:
        item.artisan_city = product.artisan.city
        item.artisan_verification_level = product.artisan.verification_level
        if product.artisan.user:
            item.artisan_name = product.artisan.user.full_name

    return APIResponse(
        success=True,
        message="Product details retrieved",
        data=item,
    )
