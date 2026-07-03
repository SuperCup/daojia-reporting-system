"""User management router — admin batch create, approve registrations, CRUD."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserUpdate, UserResponse
from ..auth import hash_password
from ..dependencies import get_current_user, require_ops

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    region: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ops),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if status:
        q = q.filter(User.status == status)
    if region:
        q = q.filter(User.region.contains(region))
    if keyword:
        q = q.filter(User.username.contains(keyword) | User.real_name.contains(keyword))
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return users


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    req: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ops),
):
    """Admin batch-creates a user account (ops or client)."""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if req.role not in ("admin", "ops", "client"):
        raise HTTPException(status_code=400, detail="角色无效，可选: admin/ops/client")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=req.role,
        real_name=req.real_name,
        region=req.region,
        org_level=req.org_level,
        phone=req.phone,
        email=req.email,
        status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    req: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ops),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if req.real_name is not None:
        user.real_name = req.real_name
    if req.region is not None:
        user.region = req.region
    if req.org_level is not None:
        user.org_level = req.org_level
    if req.phone is not None:
        user.phone = req.phone
    if req.email is not None:
        user.email = req.email
    if req.status is not None:
        user.status = req.status
    if req.role is not None:
        user.role = req.role
    if req.password:
        user.password_hash = hash_password(req.password)

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ops),
):
    """Approve a pending registration."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.status != "pending":
        raise HTTPException(status_code=400, detail="该账号不在待审核状态")
    user.status = "active"
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ops),
):
    """Soft-delete: disable the user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user.status = "disabled"
    db.commit()
    return {"detail": "已禁用"}
