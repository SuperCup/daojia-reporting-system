"""Product router — CRUD for products."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Product
from ..schemas import ProductCreate, ProductUpdate, ProductResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    keyword: Optional[str] = None,
    brand_series: Optional[str] = None,
    status: Optional[str] = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Product)
    if keyword:
        q = q.filter(
            Product.name.contains(keyword) | Product.upc.contains(keyword) | Product.brand_series.contains(keyword)
        )
    if brand_series:
        q = q.filter(Product.brand_series == brand_series)
    if status:
        q = q.filter(Product.status == status)
    products = q.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return products


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    req: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = db.query(Product).filter(Product.upc == req.upc).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"UPC {req.upc} 已存在")
    p = Product(
        upc=req.upc,
        name=req.name,
        brand_series=req.brand_series,
        center_series=req.center_series,
        detail_series=req.detail_series,
        spec=req.spec,
        pack_quantity=req.pack_quantity,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post("/batch", response_model=List[ProductResponse], status_code=201)
def batch_create_products(
    items: List[ProductCreate],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Batch create products."""
    created = []
    for item in items:
        existing = db.query(Product).filter(Product.upc == item.upc).first()
        if existing:
            continue
        p = Product(
            upc=item.upc,
            name=item.name,
            brand_series=item.brand_series,
            center_series=item.center_series,
            detail_series=item.detail_series,
            spec=item.spec,
            pack_quantity=item.pack_quantity,
        )
        db.add(p)
        created.append(p)
    db.commit()
    for p in created:
        db.refresh(p)
    return created


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    req: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="产品不存在")
    for field in ["name", "brand_series", "center_series", "detail_series", "spec", "pack_quantity", "status"]:
        val = getattr(req, field, None)
        if val is not None:
            setattr(p, field, val)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="产品不存在")
    p.status = "inactive"
    db.commit()
    return {"detail": "已停用"}


@router.get("/brands")
def list_brands(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get distinct brand series."""
    brands = db.query(Product.brand_series).filter(Product.brand_series.isnot(None)).distinct().all()
    return [b[0] for b in brands if b[0]]
