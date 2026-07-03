"""Platform router — CRUD for delivery platforms."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Platform
from ..schemas import PlatformCreate, PlatformUpdate, PlatformResponse
from ..dependencies import get_current_user, require_ops

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


@router.get("", response_model=List[PlatformResponse])
def list_platforms(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Platform).order_by(Platform.created_at).all()


@router.post("", response_model=PlatformResponse, status_code=201)
def create_platform(
    req: PlatformCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    existing = db.query(Platform).filter(
        (Platform.name == req.name) | (Platform.code == req.code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="平台名称或代码已存在")
    p = Platform(name=req.name, code=req.code)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.patch("/{platform_id}", response_model=PlatformResponse)
def update_platform(
    platform_id: str,
    req: PlatformUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    p = db.query(Platform).filter(Platform.id == platform_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="平台不存在")
    if req.name is not None:
        p.name = req.name
    if req.code is not None:
        p.code = req.code
    if req.status is not None:
        p.status = req.status
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{platform_id}")
def delete_platform(
    platform_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    p = db.query(Platform).filter(Platform.id == platform_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="平台不存在")
    p.status = "inactive"
    db.commit()
    return {"detail": "已停用"}
