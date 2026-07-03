"""FastAPI dependencies for authentication and authorization."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .auth import decode_access_token
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Validate JWT token and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if user.status == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    if user.status == "pending":
        raise HTTPException(status_code=403, detail="账号待审核，请联系管理员")
    return user


def require_ops(current_user: User = Depends(get_current_user)) -> User:
    """Require operations or admin role."""
    if current_user.role not in ("ops", "admin"):
        raise HTTPException(status_code=403, detail="无权限：需要运营端账号")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限：需要管理员账号")
    return current_user
