"""Local development runner — uses SQLite instead of PostgreSQL."""
import os
import sys

# Use SQLite for local testing
os.environ["DATABASE_URL"] = "sqlite:///./local_daojia.db"
os.environ["CORS_ORIGINS"] = "*"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Step 1: Initialize database
from app.database import Base, engine, SessionLocal
from app.models import User, Platform, Region, Channel, Product, Activity, CostRecord
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
print("[1/2] Database tables created (SQLite)")

db = SessionLocal()
try:
    # Admin
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(
            username="admin",
            password_hash=hash_password("admin123456"),
            role="admin",
            org_level="HQ",
            real_name="系统管理员",
            status="active",
        ))

    # Ops user
    if not db.query(User).filter(User.username == "ops_user").first():
        db.add(User(
            username="ops_user",
            password_hash=hash_password("ops123456"),
            role="ops",
            org_level="HQ",
            real_name="运营专员",
            status="active",
        ))

    # Client - 吉林省区
    if not db.query(User).filter(User.username == "client_jilin").first():
        db.add(User(
            username="client_jilin",
            password_hash=hash_password("client123456"),
            role="client",
            org_level="region",
            real_name="吉林提报员",
            region="吉林省区",
            status="active",
        ))

    # Client - 吉林省区 (second user, same region — should see each other's reports)
    if not db.query(User).filter(User.username == "client_jilin2").first():
        db.add(User(
            username="client_jilin2",
            password_hash=hash_password("client123456"),
            role="client",
            org_level="region",
            real_name="吉林提报员2",
            region="吉林省区",
            status="active",
        ))

    # Client — different region (should NOT see 吉林省区 reports)
    if not db.query(User).filter(User.username == "client_guangdong").first():
        db.add(User(
            username="client_guangdong",
            password_hash=hash_password("client123456"),
            role="client",
            org_level="region",
            real_name="广东提报员",
            region="广东省区",
            status="active",
        ))
    db.commit()

    # Platforms
    platforms_data = [
        {"name": "美团", "code": "meituan"},
        {"name": "饿了么", "code": "eleme"},
        {"name": "淘宝", "code": "taobao"},
        {"name": "京东", "code": "jd"},
        {"name": "抖音", "code": "douyin"},
    ]
    for p in platforms_data:
        if not db.query(Platform).filter(Platform.code == p["code"]).first():
            db.add(Platform(**p))
    db.commit()
    platforms = {p.code: p for p in db.query(Platform).all()}

    # Regions
    regions_data = [
        {"name": "吉林省区", "code": "jilin"},
        {"name": "广东省区", "code": "guangdong"},
        {"name": "北京区域", "code": "beijing"},
        {"name": "上海区域", "code": "shanghai"},
        {"name": "浙江省区", "code": "zhejiang"},
    ]
    for r in regions_data:
        if not db.query(Region).filter(Region.name == r["name"]).first():
            db.add(Region(**r))
    db.commit()

    # Channels (from Excel reference)
    channels_data = [
        {"name": "远方超市（超达大路店）", "channel_type": "KA超市", "platform_id": platforms["meituan"].id, "platform_store_id": "21614410", "region": "吉林"},
        {"name": "远方超市（临河街店）", "channel_type": "KA超市", "platform_id": platforms["meituan"].id, "platform_store_id": "21614415", "region": "吉林"},
        {"name": "远方超市(越达店)", "channel_type": "KA超市", "platform_id": platforms["meituan"].id, "platform_store_id": "20850264", "region": "吉林"},
        {"name": "优客超市", "channel_type": "便利", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "金文汇", "channel_type": "便利", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "每日隆", "channel_type": "便利", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "新天地", "channel_type": "便利", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "大润发", "channel_type": "超市", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "小酒喔", "channel_type": "酒专营", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "欧亚超市", "channel_type": "KA超市", "platform_id": platforms["meituan"].id, "region": "吉林"},
        {"name": "远方超市(崇智路店)", "channel_type": "KA超市", "platform_id": platforms["eleme"].id, "platform_store_id": "1259126285", "region": "吉林"},
        {"name": "远方超市(富豪店)", "channel_type": "KA超市", "platform_id": platforms["eleme"].id, "platform_store_id": "524531863", "region": "吉林"},
        {"name": "远方超市(光谷大街店)", "channel_type": "KA超市", "platform_id": platforms["eleme"].id, "platform_store_id": "524471848", "region": "吉林"},
    ]
    for ch in channels_data:
        if not db.query(Channel).filter(Channel.name == ch["name"]).first():
            db.add(Channel(**ch))
    db.commit()
    channels = db.query(Channel).all()

    # Products (from Excel reference)
    products_data = [
        {"upc": "6901035981903", "name": "传奇10.5度青岛啤酒一世1.5l/瓶", "brand_series": "青岛百年之旅", "center_series": "百年之旅大瓶", "detail_series": "百年之旅纸箱", "spec": "1500", "pack_quantity": 1},
        {"upc": "6901035614221", "name": "青岛啤酒 11°P白啤 500ml*12听/箱", "brand_series": "青岛白啤", "center_series": "青岛听装", "detail_series": "白啤听装", "spec": "500", "pack_quantity": 12},
        {"upc": "6901035622752", "name": "青岛啤酒（1903） 10度5L/桶", "brand_series": "青岛经典1903", "center_series": "青岛桶鲜", "detail_series": "经典1903桶啤", "spec": "5000", "pack_quantity": 1},
        {"upc": "6901035613675", "name": "青岛啤酒（1903）500ml/瓶", "brand_series": "青岛经典1903", "center_series": "经典1903大瓶", "detail_series": "经典1903纸箱", "spec": "500", "pack_quantity": 1},
        {"upc": "6901035614467", "name": "青岛啤酒（1903）500听", "brand_series": "青岛经典1903", "center_series": "青岛听装", "detail_series": "经典1903听装", "spec": "500", "pack_quantity": 1},
        {"upc": "6901035613682", "name": "青岛啤酒（1903）瓶500ml*12/箱", "brand_series": "青岛经典1903", "center_series": "经典1903大瓶", "detail_series": "经典1903纸箱", "spec": "500", "pack_quantity": 12},
        {"upc": "6901035615167", "name": "青岛啤酒11度白啤瓶330ml*24/箱", "brand_series": "青岛白啤", "center_series": "青岛小瓶", "detail_series": "白啤小瓶", "spec": "330", "pack_quantity": 24},
        {"upc": "6901035623063", "name": "青岛啤酒11度经典296ml*24瓶/箱", "brand_series": "青岛经典", "center_series": "青岛小瓶", "detail_series": "经典小瓶", "spec": "296", "pack_quantity": 24},
        {"upc": "6901035618786", "name": "青岛啤酒11度经典纯生258ml*24/箱", "brand_series": "青岛经典", "center_series": "青岛小瓶", "detail_series": "纯生小瓶", "spec": "258", "pack_quantity": 24},
        {"upc": "6901035617109", "name": "青岛啤酒12度经典纯生大听500ml*4/箱", "brand_series": "青岛经典", "center_series": "青岛听装", "detail_series": "纯生大听", "spec": "500", "pack_quantity": 4},
        {"upc": "6901035622103", "name": "青岛啤酒12度纯生桂花330ml*12瓶/箱", "brand_series": "青岛经典", "center_series": "青岛小瓶", "detail_series": "纯生小瓶", "spec": "330", "pack_quantity": 12},
        {"upc": "6901035614986", "name": "青岛啤酒1903礼罐500ml*3/箱", "brand_series": "青岛经典1903", "center_series": "青岛听装", "detail_series": "1903礼罐", "spec": "500", "pack_quantity": 3},
        {"upc": "6901035627771", "name": "青岛啤酒1L经典", "brand_series": "青岛经典", "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035626729", "name": "青岛啤酒1L茉莉花", "brand_series": "青岛经典", "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035625906", "name": "青岛啤酒1L原酿", "brand_series": "青岛经典", "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035297776", "name": "青岛啤酒A3系列10.7度500ml*12听/箱", "brand_series": "青岛奥古特", "center_series": "青岛听装", "detail_series": "奥古特听装", "spec": "500", "pack_quantity": 12},
        {"upc": "6901035267779", "name": "青岛啤酒A3系列10.7度500ml*3听/箱", "brand_series": "青岛奥古特", "center_series": "青岛听装", "detail_series": "奥古特听装", "spec": "500", "pack_quantity": 3},
    ]
    for p in products_data:
        if not db.query(Product).filter(Product.upc == p["upc"]).first():
            db.add(Product(**p))
    db.commit()
    products = db.query(Product).all()

    # Sample activity
    client = db.query(User).filter(User.username == "client_jilin").first()
    if not db.query(Activity).filter(Activity.mechanism == "满79减30（品18）").first():
        act = Activity(
            region="吉林省区",
            activity_time="周六日",
            mechanism="满79减30（品18）",
            channel_type="便利",
            platform_id=platforms["meituan"].id,
            voucher_quantity=80000,
            budget=80000,
            brand="青啤",
            remarks="每个用户ID每天限一个",
            prefix="区域下沉",
            status="submitted",
            created_by=client.id,
        )
        act.channels = [ch for ch in channels if ch.channel_type == "便利"][:4]
        act.products = products[:8]
        db.add(act)

    # Cost record
    if not db.query(CostRecord).filter(CostRecord.sales_unit == "吉林省区").first():
        db.add(CostRecord(
            sales_unit="吉林省区",
            platform_id=platforms["meituan"].id,
            plan_amount=8000000,
            accumulated_cost=794499.65,
            cost_ratio=0.0947,
            transaction_amount=8393818,
            month_cost=794499.65,
            month_cost_ratio=0.0947,
            month_expected_transaction=8393818,
            month="2026-04",
            year=2026,
        ))

    db.commit()
    print(f"[2/2] Seed data inserted:")
    print(f"  Users: {db.query(User).count()}")
    print(f"  Platforms: {db.query(Platform).count()}")
    print(f"  Regions: {db.query(Region).count()}")
    print(f"  Channels: {db.query(Channel).count()}")
    print(f"  Products: {db.query(Product).count()}")
    print(f"  Activities: {db.query(Activity).count()}")
    print(f"  Cost Records: {db.query(CostRecord).count()}")
finally:
    db.close()

print()
print("=" * 50)
print("  启动后端服务器: http://localhost:8000")
print("  API 文档: http://localhost:8000/docs")
print("  管理员: admin / admin123456")
print("  运营端: ops_user / ops123456")
print("  客户端: client_jilin / client123456")
print("=" * 50)
print()

# Step 2: Start server
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", reload=False)
