"""Reports router — dashboard stats and detailed reporting for ops."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models import Activity, Channel, Product, User, Platform, CostRecord
from ..schemas import DashboardStats, CostRecordCreate, CostRecordResponse
from ..dependencies import require_ops

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), current_user=Depends(require_ops)):
    """Aggregate stats for the operations dashboard."""
    total = db.query(Activity).count()
    draft = db.query(Activity).filter(Activity.status == "draft").count()
    submitted = db.query(Activity).filter(Activity.status == "submitted").count()
    approved = db.query(Activity).filter(Activity.status == "approved").count()
    rejected = db.query(Activity).filter(Activity.status == "rejected").count()
    total_channels = db.query(Channel).filter(Channel.status == "active").count()
    total_products = db.query(Product).filter(Product.status == "active").count()
    total_users = db.query(User).count()
    pending_users = db.query(User).filter(User.status == "pending").count()
    total_budget = db.query(func.coalesce(func.sum(Activity.budget), 0)).scalar() or 0
    approved_budget = db.query(func.coalesce(func.sum(Activity.budget), 0)).filter(
        Activity.status == "approved"
    ).scalar() or 0

    return DashboardStats(
        total_activities=total,
        draft_activities=draft,
        submitted_activities=submitted,
        approved_activities=approved,
        rejected_activities=rejected,
        total_channels=total_channels,
        total_products=total_products,
        total_users=total_users,
        pending_users=pending_users,
        total_budget=float(total_budget),
        approved_budget=float(approved_budget),
    )


@router.get("/activities")
def activity_report(
    region: Optional[str] = None,
    platform_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Detailed activity report with channel/product breakdown."""
    q = db.query(Activity)
    if region:
        q = q.filter(Activity.region.contains(region))
    if platform_id:
        q = q.filter(Activity.platform_id == platform_id)
    if status:
        q = q.filter(Activity.status == status)
    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            q = q.filter(Activity.created_at >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            q = q.filter(Activity.created_at <= ed)
        except ValueError:
            pass

    acts = q.order_by(Activity.created_at.desc()).all()
    results = []
    for act in acts:
        results.append({
            "id": act.id,
            "title": act.title,
            "region": act.region,
            "activity_time": act.activity_time,
            "mechanism": act.mechanism,
            "channel_type": act.channel_type,
            "platform_name": act.platform.name if act.platform else None,
            "voucher_quantity": act.voucher_quantity,
            "budget": act.budget,
            "brand": act.brand,
            "status": act.status,
            "creator_name": act.creator.real_name or act.creator.username if act.creator else None,
            "created_at": act.created_at.isoformat() if act.created_at else None,
            "submitted_at": act.submitted_at.isoformat() if act.submitted_at else None,
            "reviewed_at": act.reviewed_at.isoformat() if act.reviewed_at else None,
            "reviewer_name": act.reviewer.real_name or act.reviewer.username if act.reviewer else None,
            "review_comment": act.review_comment,
            "channel_count": len(act.channels),
            "product_count": len(act.products),
            "channels": [
                {"id": ch.id, "name": ch.name, "channel_type": ch.channel_type,
                 "platform_store_id": ch.platform_store_id}
                for ch in act.channels
            ],
            "products": [
                {"id": p.id, "upc": p.upc, "name": p.name, "brand_series": p.brand_series}
                for p in act.products
            ],
        })
    return {"total": len(results), "items": results}


@router.get("/activities/{activity_id}/detail")
def activity_detail_report(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Full detail report for a single activity — channels, products, cost breakdown."""
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="活动不存在")

    return {
        "id": act.id,
        "title": act.title,
        "region": act.region,
        "activity_time": act.activity_time,
        "mechanism": act.mechanism,
        "channel_type": act.channel_type,
        "platform_name": act.platform.name if act.platform else None,
        "voucher_quantity": act.voucher_quantity,
        "budget": act.budget,
        "brand": act.brand,
        "prefix": act.prefix,
        "remarks": act.remarks,
        "status": act.status,
        "creator_name": act.creator.real_name or act.creator.username if act.creator else None,
        "created_at": act.created_at.isoformat() if act.created_at else None,
        "submitted_at": act.submitted_at.isoformat() if act.submitted_at else None,
        "reviewed_at": act.reviewed_at.isoformat() if act.reviewed_at else None,
        "reviewer_name": act.reviewer.real_name or act.reviewer.username if act.reviewer else None,
        "review_comment": act.review_comment,
        "channels": [
            {
                "id": ch.id, "name": ch.name, "channel_type": ch.channel_type,
                "platform_store_id": ch.platform_store_id, "region": ch.region,
                "address": ch.address, "contact": ch.contact,
                "platform_name": ch.platform.name if ch.platform else None,
            }
            for ch in act.channels
        ],
        "products": [
            {
                "id": p.id, "upc": p.upc, "name": p.name,
                "brand_series": p.brand_series, "center_series": p.center_series,
                "detail_series": p.detail_series, "spec": p.spec, "pack_quantity": p.pack_quantity,
            }
            for p in act.products
        ],
    }


@router.get("/costs", response_model=list[CostRecordResponse])
def list_costs(
    sales_unit: Optional[str] = None,
    platform_id: Optional[str] = None,
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    q = db.query(CostRecord)
    if sales_unit:
        q = q.filter(CostRecord.sales_unit.contains(sales_unit))
    if platform_id:
        q = q.filter(CostRecord.platform_id == platform_id)
    if month:
        q = q.filter(CostRecord.month == month)
    records = q.order_by(CostRecord.created_at.desc()).all()
    results = []
    for r in records:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        d["platform_name"] = r.platform.name if r.platform else None
        results.append(d)
    return results


@router.post("/costs", response_model=CostRecordResponse, status_code=201)
def create_cost(
    req: CostRecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    r = CostRecord(
        sales_unit=req.sales_unit,
        platform_id=req.platform_id,
        plan_amount=req.plan_amount,
        accumulated_cost=req.accumulated_cost,
        cost_ratio=req.cost_ratio,
        transaction_amount=req.transaction_amount,
        month_cost=req.month_cost,
        month_cost_ratio=req.month_cost_ratio,
        month_expected_transaction=req.month_expected_transaction,
        month=req.month,
        year=req.year,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
    d["platform_name"] = r.platform.name if r.platform else None
    return d


@router.get("/export/summary")
def export_summary(
    region: Optional[str] = None,
    platform_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_ops),
):
    """Export activity summary as JSON (can be converted to Excel on frontend)."""
    q = db.query(Activity)
    if region:
        q = q.filter(Activity.region.contains(region))
    if platform_id:
        q = q.filter(Activity.platform_id == platform_id)
    if status:
        q = q.filter(Activity.status == status)
    acts = q.order_by(Activity.created_at.desc()).all()

    rows = []
    for act in acts:
        rows.append({
            "区域": act.region,
            "活动时间": act.activity_time,
            "活动机制": act.mechanism,
            "活动产品": " / ".join([p.name for p in act.products]),
            "渠道类型": act.channel_type,
            "渠道名称": " / ".join([ch.name for ch in act.channels]),
            "平台": act.platform.name if act.platform else "",
            "券数量": act.voucher_quantity or "",
            "备注": act.remarks or "",
            "前缀": act.prefix or "",
            "品牌": act.brand or "",
            "状态": act.status,
            "提报人": act.creator.real_name or act.creator.username if act.creator else "",
            "创建时间": act.created_at.strftime("%Y-%m-%d %H:%M") if act.created_at else "",
        })
    return {"columns": list(rows[0].keys()) if rows else [], "rows": rows}
