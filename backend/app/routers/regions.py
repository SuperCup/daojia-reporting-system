"""Region router — CRUD for sales regions (managed by ops/admin)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Region
from ..schemas import RegionCreate, RegionUpdate, RegionResponse
from ..dependencies import require_ops

router = APIRouter(prefix="/api/regions", tags=["regions"])


@router.get("", response_model=List[RegionResponse])
def list_regions(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """List all regions. Ops/admin can manage regions."""
    q = db.query(Region)
    if status:
        q = q.filter(Region.status == status)
    if keyword:
        q = q.filter(Region.name.contains(keyword) | Region.code.contains(keyword))
    regions = q.order_by(Region.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return regions


@router.post("", response_model=RegionResponse, status_code=201)
def create_region(
    req: RegionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Create a new region."""
    existing = db.query(Region).filter(Region.name == req.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"区域 {req.name} 已存在")
    region = Region(
        name=req.name,
        code=req.code,
        status=req.status or "active",
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


@router.patch("/{region_id}", response_model=RegionResponse)
def update_region(
    region_id: str,
    req: RegionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Update a region."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")
    for field in ["name", "code", "status"]:
        val = getattr(req, field, None)
        if val is not None:
            setattr(region, field, val)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/{region_id}")
def delete_region(
    region_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Soft-delete a region (set status to inactive)."""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="区域不存在")
    region.status = "inactive"
    db.commit()
    return {"detail": "已停用"}
