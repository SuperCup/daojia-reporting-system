"""Activity router — CRUD and workflow for activity reports."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from ..database import get_db
from ..models import Activity, Channel, Product, User, Platform, activity_channels, activity_products
from ..schemas import (
    ActivityCreate, ActivityUpdate, ActivityResponse, ActivityReview,
    ChannelResponse, ProductResponse,
)
from ..dependencies import get_current_user, require_ops

router = APIRouter(prefix="/api/activities", tags=["activities"])


def _enrich(act: Activity) -> dict:
    """Build full response dict with nested channels, products, and names."""
    d = {c.name: getattr(act, c.name) for c in act.__table__.columns}
    d["platform_name"] = act.platform.name if act.platform else None
    d["creator_name"] = act.creator.real_name or act.creator.username if act.creator else None
    d["reviewer_name"] = act.reviewer.real_name or act.reviewer.username if act.reviewer else None
    d["channels"] = []
    for ch in act.channels:
        chd = {c.name: getattr(ch, c.name) for c in ch.__table__.columns}
        chd["platform_name"] = ch.platform.name if ch.platform else None
        d["channels"].append(chd)
    d["products"] = [
        {c.name: getattr(p, c.name) for c in p.__table__.columns}
        for p in act.products
    ]
    return d


@router.get("", response_model=List[ActivityResponse])
def list_activities(
    status: Optional[str] = None,
    region: Optional[str] = None,
    platform_id: Optional[str] = None,
    keyword: Optional[str] = None,
    created_by: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List activities. Client users see activities from same region; ops/admin see all."""
    q = db.query(Activity)
    if current_user.role == "client":
        q = q.filter(Activity.region == current_user.region)
    if status:
        q = q.filter(Activity.status == status)
    if region:
        q = q.filter(Activity.region.contains(region))
    if platform_id:
        q = q.filter(Activity.platform_id == platform_id)
    if created_by:
        q = q.filter(Activity.created_by == created_by)
    if keyword:
        q = q.filter(
            Activity.mechanism.contains(keyword) | Activity.title.contains(keyword) | Activity.brand.contains(keyword)
        )
    acts = q.order_by(Activity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return [_enrich(a) for a in acts]


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")
    # Client can view activities from same region
    if current_user.role == "client" and act.region != current_user.region:
        raise HTTPException(status_code=403, detail="无权查看此活动")
    return _enrich(act)


@router.post("", response_model=ActivityResponse, status_code=201)
def create_activity(
    req: ActivityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new activity report (client or ops)."""
    # Derive channel_type from first channel if available
    channel_type = None
    if req.channel_ids:
        first_ch = db.query(Channel).filter(Channel.id == req.channel_ids[0]).first()
        if first_ch:
            channel_type = first_ch.channel_type

    act = Activity(
        title=req.title,
        region=req.region,
        activity_time=req.activity_time,
        mechanism=req.mechanism,
        channel_type=channel_type,
        platform_id=req.platform_id,
        voucher_quantity=req.voucher_quantity,
        budget=req.budget,
        remarks=req.remarks,
        prefix=req.prefix,
        brand=req.brand,
        status="draft",
        created_by=current_user.id,
    )

    # Attach channels
    if req.channel_ids:
        channels = db.query(Channel).filter(Channel.id.in_(req.channel_ids)).all()
        act.channels = channels

    # Attach products
    if req.product_ids:
        products = db.query(Product).filter(Product.id.in_(req.product_ids)).all()
        act.products = products

    db.add(act)
    db.commit()
    db.refresh(act)
    return _enrich(act)


@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    req: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")
    # Client can only edit their own drafts
    if current_user.role == "client":
        if act.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权修改此活动")
        if act.status not in ("draft", "rejected"):
            raise HTTPException(status_code=400, detail="只能修改草稿或被驳回的活动")

    simple_fields = ["title", "region", "activity_time", "mechanism", "platform_id",
                     "voucher_quantity", "budget", "remarks", "prefix", "brand"]
    for field in simple_fields:
        val = getattr(req, field, None)
        if val is not None:
            setattr(act, field, val)

    # Update channel associations
    if req.channel_ids is not None:
        channels = db.query(Channel).filter(Channel.id.in_(req.channel_ids)).all()
        act.channels = channels
        if channels:
            act.channel_type = channels[0].channel_type

    # Update product associations
    if req.product_ids is not None:
        products = db.query(Product).filter(Product.id.in_(req.product_ids)).all()
        act.products = products

    db.commit()
    db.refresh(act)
    return _enrich(act)


@router.post("/{activity_id}/submit", response_model=ActivityResponse)
def submit_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Submit a draft activity for ops review."""
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")
    if current_user.role == "client" and act.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权提交此活动")
    if act.status not in ("draft", "rejected"):
        raise HTTPException(status_code=400, detail="只能提交草稿或被驳回的活动")
    if not act.channels:
        raise HTTPException(status_code=400, detail="请至少选择一个投放渠道")
    if not act.products:
        raise HTTPException(status_code=400, detail="请至少选择一个投放商品")

    act.status = "submitted"
    act.submitted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(act)
    return _enrich(act)


@router.post("/{activity_id}/review", response_model=ActivityResponse)
def review_activity(
    activity_id: str,
    req: ActivityReview,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Ops reviews a submitted activity — approve or reject."""
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")
    if act.status != "submitted":
        raise HTTPException(status_code=400, detail="只能审核已提交的活动")
    if req.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="审核状态无效")

    act.status = req.status
    act.reviewed_by = current_user.id
    act.reviewed_at = datetime.now(timezone.utc)
    act.review_comment = req.review_comment
    db.commit()
    db.refresh(act)
    return _enrich(act)


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")
    if current_user.role == "client":
        if act.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此活动")
        if act.status not in ("draft", "rejected"):
            raise HTTPException(status_code=400, detail="只能删除草稿或被驳回的活动")
    db.delete(act)
    db.commit()
    return {"detail": "已删除"}


@router.post("/batch", status_code=201)
def batch_create_activities(
    items: list[ActivityCreate],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Batch create activities. Returns count of created items."""
    created = []
    for item in items:
        channel_type = None
        if item.channel_ids:
            first_ch = db.query(Channel).filter(Channel.id == item.channel_ids[0]).first()
            if first_ch:
                channel_type = first_ch.channel_type

        act = Activity(
            title=item.title,
            region=item.region,
            activity_time=item.activity_time,
            mechanism=item.mechanism,
            channel_type=channel_type,
            platform_id=item.platform_id,
            voucher_quantity=item.voucher_quantity,
            budget=item.budget,
            remarks=item.remarks,
            prefix=item.prefix,
            brand=item.brand,
            status="draft",
            created_by=current_user.id,
        )
        if item.channel_ids:
            channels = db.query(Channel).filter(Channel.id.in_(item.channel_ids)).all()
            act.channels = channels
        if item.product_ids:
            products = db.query(Product).filter(Product.id.in_(item.product_ids)).all()
            act.products = products
        db.add(act)
        created.append(act)
    db.commit()
    return {"detail": f"已创建 {len(created)} 条活动", "count": len(created)}
