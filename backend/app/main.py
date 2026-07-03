"""FastAPI application entry point."""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import settings
from .database import Base, engine, SessionLocal
from .models import User
from .auth import hash_password
from .routers import auth, users, platforms, regions, channels, products, activities, reports

logger = logging.getLogger("daojia")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed initial admin on startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.INITIAL_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.INITIAL_ADMIN_USERNAME,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role="admin",
                real_name="系统管理员",
                status="active",
            )
            db.add(admin)
            db.commit()
            logger.info("Initial admin user created: %s", settings.INITIAL_ADMIN_USERNAME)
    finally:
        db.close()
    yield


app = FastAPI(
    title="到家平台提报管理系统",
    description="运营端与客户端活动提报管理",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(platforms.router)
app.include_router(regions.router)
app.include_router(channels.router)
app.include_router(products.router)
app.include_router(activities.router)
app.include_router(reports.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "daojia-reporting"}


# Path to test.html in project root (../../test.html relative to this file)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@app.get("/")
def root():
    return FileResponse(os.path.join(_PROJECT_ROOT, "test.html"))
