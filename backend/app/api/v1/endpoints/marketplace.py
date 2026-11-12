from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.cache import cache
from app.db.session import get_db
from app.models import ArtisanProfile, Category, Product, Review
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.marketplace import CategoryOut, ProductPublicOut, ReviewOut

router = APIRouter()


@router.get("/categories", response_model=APIResponse[list[CategoryOut]])
def list_categories(db: Session = Depends(get_db)):
    """Lists all active craft categories with descriptions and icon metadata."""
    categories = db.query(Category).filter(Category.is_active.is_(True)).order_by(Category.sort_order).all()
    return APIResponse(
        success=True,
        message="Categories retrieved",
        data=[CategoryOut.model_validate(c) for c in categories],
    )


@router.get("/products", response_model=APIResponse[PaginatedResponse[ProductPublicOut]])
def discover_products(
    category_slug: str | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "newest",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """Public marketplace product discovery endpoint with pagination, eager loading (no N+1),
    keyword search, category filters, and Redis/TTL caching.
    """
    p = max(1, int(getattr(page, "default", page)))
    ps = min(100, max(1, int(getattr(page_size, "default", page_size))))

    cache_key = (
        f"marketplace:products:{category_slug or ''}:{search or ''}:{min_price or ''}:{max_price or ''}:{sort}:{p}:{ps}"
    )
    cached = cache.get_json(cache_key)
    if cached is not None:
        return APIResponse(
            success=True,
            message="Products retrieved successfully",
            data=PaginatedResponse(**cached),
        )

    query = (
        db.query(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.variants),
            selectinload(Product.images),
            joinedload(Product.artisan).joinedload(ArtisanProfile.user),
        )
        .filter(Product.status == "ACTIVE")
    )

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
    paginated_data = PaginatedResponse(
        items=output_items,
        total=total,
        page=p,
        page_size=ps,
        pages=pages,
    )
    cache.set_json(cache_key, paginated_data.model_dump(mode="json"), ttl_seconds=45)

    return APIResponse(
        success=True,
        message="Products retrieved successfully",
        data=paginated_data,
    )


@router.get("/products/{slug_or_id}", response_model=APIResponse[ProductPublicOut])
def get_product_detail(
    slug_or_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves full details of a single product including variants, images, and artisan story."""
    product = db.query(Product).filter(or_(Product.slug == slug_or_id, Product.id == slug_or_id)).first()
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


@router.get("/products/{product_id}/reviews", response_model=APIResponse[list[ReviewOut]])
def list_product_reviews(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Returns verified buyer reviews for a product."""
    reviews = db.query(Review).filter(Review.product_id == product_id).order_by(desc(Review.created_at)).all()
    return APIResponse(
        success=True,
        message="Product reviews fetched",
        data=[ReviewOut.model_validate(r) for r in reviews],
    )
