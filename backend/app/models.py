"""Database models for the reporting system."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey,
    Table, UniqueConstraint, JSON
)
from sqlalchemy.orm import relationship
from .database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ── Association tables ──
activity_channels = Table(
    "activity_channels",
    Base.metadata,
    Column("activity_id", String(36), ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
    Column("channel_id", String(36), ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True),
)

activity_products = Table(
    "activity_products",
    Base.metadata,
    Column("activity_id", String(36), ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", String(36), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """System user — can be operations staff or client (区域提报人)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="client")  # admin | ops | client
    org_level = Column(String(20), default="region")  # HQ (总部) | region (区域)
    real_name = Column(String(100))
    region = Column(String(100))  # e.g. 吉林省区
    phone = Column(String(20))
    email = Column(String(200))
    status = Column(String(20), nullable=False, default="active")  # active | pending | disabled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activities = relationship("Activity", foreign_keys="Activity.created_by", back_populates="creator")


class Platform(Base):
    """Delivery platform — 美团, 饿了么, 淘宝, etc."""
    __tablename__ = "platforms"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(100), unique=True, nullable=False)  # 美团 / 饿了么 / 淘宝
    code = Column(String(50), unique=True, nullable=False)   # meituan / eleme / taobao
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    channels = relationship("Channel", back_populates="platform")


class Region(Base):
    """Sales region — managed by ops staff."""
    __tablename__ = "regions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(100), unique=True, nullable=False)  # e.g. 吉林省区
    code = Column(String(50), unique=True, nullable=True)    # e.g. jilin
    status = Column(String(20), default="active")  # active | inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Channel(Base):
    """Distribution channel — a store or chain on a platform."""
    __tablename__ = "channels"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(200), nullable=False)           # 渠道名称 e.g. 优客超市
    channel_type = Column(String(50), nullable=False)     # 渠道类型: 便利/超市/酒专营/散店/全渠道/KA超市/闪电仓
    platform_id = Column(String(36), ForeignKey("platforms.id"), nullable=True)
    platform_store_id = Column(String(100))               # 平台店铺ID (美团ID/饿了么ID)
    region = Column(String(100))                          # 区域
    address = Column(Text)
    contact = Column(String(100))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    platform = relationship("Platform", back_populates="channels")
    activities = relationship("Activity", secondary=activity_channels, back_populates="channels")


class Product(Base):
    """Product that can be included in activities."""
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    upc = Column(String(50), unique=True, nullable=False, index=True)  # UPC条码
    name = Column(String(300), nullable=False)           # 产品名称
    brand_series = Column(String(200))                   # 品牌系列
    center_series = Column(String(200))                  # 中心系列
    detail_series = Column(String(200))                  # 中心明细系列
    spec = Column(String(100))                           # 单瓶规格(ml)
    pack_quantity = Column(Integer)                      # 数量(箱规格)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activities = relationship("Activity", secondary=activity_products, back_populates="products")


class Activity(Base):
    """An activity / campaign report submitted by a client."""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    title = Column(String(300))                          # 活动标题 (auto-generated or manual)
    region = Column(String(100), nullable=False)         # 区域 e.g. 吉林省区
    activity_time = Column(String(200), nullable=False)  # 活动时间 e.g. "4.1-4.30" or "周六日"
    mechanism = Column(String(500), nullable=False)      # 活动机制 e.g. "满79减30（品18）"
    channel_type = Column(String(50))                    # 渠道类型 (derived, for quick filter)
    platform_id = Column(String(36), ForeignKey("platforms.id"), nullable=True)
    voucher_quantity = Column(Integer)                   # 券数量/预算
    budget = Column(Float)                               # 预算金额
    remarks = Column(Text)                               # 备注
    prefix = Column(String(100))                         # 前缀
    brand = Column(String(100))                          # 品牌
    status = Column(String(20), default="draft")         # draft | submitted | approved | rejected
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text)

    creator = relationship("User", foreign_keys=[created_by], back_populates="activities")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    platform = relationship("Platform")
    channels = relationship("Channel", secondary=activity_channels, back_populates="activities")
    products = relationship("Product", secondary=activity_products, back_populates="activities")


class CostRecord(Base):
    """Cost / budget tracking per region and platform."""
    __tablename__ = "cost_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    sales_unit = Column(String(100), nullable=False)     # 销售单位 e.g. 吉林省区
    platform_id = Column(String(36), ForeignKey("platforms.id"), nullable=True)
    plan_amount = Column(Float)                           # 方案金额
    accumulated_cost = Column(Float)                      # 累计费用
    cost_ratio = Column(Float)                            # 累计费比
    transaction_amount = Column(Float)                    # 累计交易额
    month_cost = Column(Float)                            # 当月费用
    month_cost_ratio = Column(Float)                      # 当月费比
    month_expected_transaction = Column(Float)            # 当月预计交易额
    month = Column(String(10))                           # e.g. "2026-04"
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    platform = relationship("Platform")


class Invitation(Base):
    """Invitation code for client registration — created by ops/admin."""
    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(32), unique=True, nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    used_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="active")  # active | used | expired
    note = Column(String(200))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime)

    creator = relationship("User", foreign_keys=[created_by])
    registered_user = relationship("User", foreign_keys=[used_by])
