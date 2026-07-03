"""Auth router — login, current user info, change password."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserResponse
from ..auth import hash_password, verify_password, create_access_token
from ..dependencies import get_current_user
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Schemas ──
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ── Login ──
@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if user.status == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    if user.status == "pending":
        raise HTTPException(status_code=403, detail="账号待审核，请联系管理员")
    token = create_access_token(
        data={"sub": user.id, "role": user.role, "username": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(
        access_token=token, role=user.role, username=user.username,
        user_id=user.id, real_name=user.real_name, region=user.region,
    )


# ── Current user ──
@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Change password ──
@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6个字符")
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"detail": "密码修改成功"}
