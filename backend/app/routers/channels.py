"""Channel router — CRUD for distribution channels."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Channel, Platform
from ..schemas import ChannelCreate, ChannelUpdate, ChannelResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/channels", tags=["channels"])


def _enrich(ch: Channel) -> dict:
    """Add platform_name to the channel dict."""
    d = {c.name: getattr(ch, c.name) for c in ch.__table__.columns}
    d["platform_name"] = ch.platform.name if ch.platform else None
    return d


@router.get("", response_model=List[ChannelResponse])
def list_channels(
    channel_type: Optional[str] = None,
    platform_id: Optional[str] = None,
    region: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = "active",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Channel)
    if channel_type:
        q = q.filter(Channel.channel_type == channel_type)
    if platform_id:
        q = q.filter(Channel.platform_id == platform_id)
    if region:
        q = q.filter(Channel.region.contains(region))
    if keyword:
        q = q.filter(Channel.name.contains(keyword) | Channel.platform_store_id.contains(keyword))
    if status:
        q = q.filter(Channel.status == status)
    channels = q.order_by(Channel.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return [_enrich(ch) for ch in channels]


@router.post("", response_model=ChannelResponse, status_code=201)
def create_channel(
    req: ChannelCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ch = Channel(
        name=req.name,
        channel_type=req.channel_type,
        platform_id=req.platform_id,
        platform_store_id=req.platform_store_id,
        region=req.region,
        address=req.address,
        contact=req.contact,
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return _enrich(ch)


@router.post("/batch", response_model=List[ChannelResponse], status_code=201)
def batch_create_channels(
    items: List[ChannelCreate],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Batch create channels."""
    created = []
    for item in items:
        ch = Channel(
            name=item.name,
            channel_type=item.channel_type,
            platform_id=item.platform_id,
            platform_store_id=item.platform_store_id,
            region=item.region,
            address=item.address,
            contact=item.contact,
        )
        db.add(ch)
        created.append(ch)
    db.commit()
    for ch in created:
        db.refresh(ch)
    return [_enrich(ch) for ch in created]


@router.patch("/{channel_id}", response_model=ChannelResponse)
def update_channel(
    channel_id: str,
    req: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ch = db.query(Channel).filter(Channel.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="渠道不存在")
    for field in ["name", "channel_type", "platform_id", "platform_store_id", "region", "address", "contact", "status"]:
        val = getattr(req, field, None)
        if val is not None:
            setattr(ch, field, val)
    db.commit()
    db.refresh(ch)
    return _enrich(ch)


@router.delete("/{channel_id}")
def delete_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ch = db.query(Channel).filter(Channel.id == channel_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="渠道不存在")
    ch.status = "inactive"
    db.commit()
    return {"detail": "已停用"}


@router.get("/types")
def list_channel_types(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get distinct channel types."""
    types = db.query(Channel.channel_type).filter(Channel.channel_type.isnot(None)).distinct().all()
    return [t[0] for t in types if t[0]]
