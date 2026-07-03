"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    real_name: str
    region: str
    phone: Optional[str] = None
    email: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: str
    real_name: Optional[str] = None
    region: Optional[str] = None


# ── User ──
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "client"  # admin | ops | client
    real_name: Optional[str] = None
    region: Optional[str] = None
    org_level: str = "region"
    phone: Optional[str] = None
    email: Optional[str] = None


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    region: Optional[str] = None
    org_level: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    real_name: Optional[str]
    region: Optional[str]
    org_level: Optional[str] = None
    phone: Optional[str]
    email: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Platform ──
class PlatformCreate(BaseModel):
    name: str
    code: str


class PlatformUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[str] = None


class PlatformResponse(BaseModel):
    id: str
    name: str
    code: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Region ──
class RegionCreate(BaseModel):
    name: str
    code: Optional[str] = None
    status: Optional[str] = "active"


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[str] = None


class RegionResponse(BaseModel):
    id: str
    name: str
    code: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Channel ──
class ChannelCreate(BaseModel):
    name: str
    channel_type: str
    platform_id: Optional[str] = None
    platform_store_id: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    channel_type: Optional[str] = None
    platform_id: Optional[str] = None
    platform_store_id: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None


class ChannelResponse(BaseModel):
    id: str
    name: str
    channel_type: str
    platform_id: Optional[str]
    platform_store_id: Optional[str]
    region: Optional[str]
    address: Optional[str]
    contact: Optional[str]
    status: str
    created_at: datetime
    platform_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── Product ──
class ProductCreate(BaseModel):
    upc: str
    name: str
    brand_series: Optional[str] = None
    center_series: Optional[str] = None
    detail_series: Optional[str] = None
    spec: Optional[str] = None
    pack_quantity: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand_series: Optional[str] = None
    center_series: Optional[str] = None
    detail_series: Optional[str] = None
    spec: Optional[str] = None
    pack_quantity: Optional[int] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    upc: str
    name: str
    brand_series: Optional[str]
    center_series: Optional[str]
    detail_series: Optional[str]
    spec: Optional[str]
    pack_quantity: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Activity ──
class ActivityCreate(BaseModel):
    title: Optional[str] = None
    region: str
    activity_time: str
    mechanism: str
    platform_id: Optional[str] = None
    voucher_quantity: Optional[int] = None
    budget: Optional[float] = None
    remarks: Optional[str] = None
    prefix: Optional[str] = None
    brand: Optional[str] = None
    channel_ids: List[str] = []
    product_ids: List[str] = []


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    region: Optional[str] = None
    activity_time: Optional[str] = None
    mechanism: Optional[str] = None
    platform_id: Optional[str] = None
    voucher_quantity: Optional[int] = None
    budget: Optional[float] = None
    remarks: Optional[str] = None
    prefix: Optional[str] = None
    brand: Optional[str] = None
    channel_ids: Optional[List[str]] = None
    product_ids: Optional[List[str]] = None
    status: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    title: Optional[str]
    region: str
    activity_time: str
    mechanism: str
    channel_type: Optional[str]
    platform_id: Optional[str]
    platform_name: Optional[str] = None
    voucher_quantity: Optional[int]
    budget: Optional[float]
    remarks: Optional[str]
    prefix: Optional[str]
    brand: Optional[str]
    status: str
    created_by: str
    creator_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    reviewer_name: Optional[str] = None
    review_comment: Optional[str]
    channels: List[ChannelResponse] = []
    products: List[ProductResponse] = []

    class Config:
        from_attributes = True


class ActivityReview(BaseModel):
    status: str  # approved | rejected
    review_comment: Optional[str] = None


# ── Cost ──
class CostRecordCreate(BaseModel):
    sales_unit: str
    platform_id: Optional[str] = None
    plan_amount: Optional[float] = None
    accumulated_cost: Optional[float] = None
    cost_ratio: Optional[float] = None
    transaction_amount: Optional[float] = None
    month_cost: Optional[float] = None
    month_cost_ratio: Optional[float] = None
    month_expected_transaction: Optional[float] = None
    month: Optional[str] = None
    year: Optional[int] = None


class CostRecordResponse(BaseModel):
    id: str
    sales_unit: str
    platform_id: Optional[str]
    platform_name: Optional[str] = None
    plan_amount: Optional[float]
    accumulated_cost: Optional[float]
    cost_ratio: Optional[float]
    transaction_amount: Optional[float]
    month_cost: Optional[float]
    month_cost_ratio: Optional[float]
    month_expected_transaction: Optional[float]
    month: Optional[str]
    year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard / Stats ──
class DashboardStats(BaseModel):
    total_activities: int
    draft_activities: int
    submitted_activities: int
    approved_activities: int
    rejected_activities: int
    total_channels: int
    total_products: int
    total_users: int
    pending_users: int
    total_budget: float
    approved_budget: float
