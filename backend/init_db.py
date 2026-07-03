"""
Database initialization and seed script.
Run: python init_db.py
Creates all tables and seeds sample data based on the reference Excel.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models import User, Platform, Channel, Product, Activity, CostRecord
from app.auth import hash_password


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("[1/5] Tables created.")


def seed_platforms(db):
    """Seed delivery platforms."""
    platforms = [
        {"name": "美团", "code": "meituan"},
        {"name": "饿了么", "code": "eleme"},
        {"name": "淘宝", "code": "taobao"},
        {"name": "京东", "code": "jd"},
        {"name": "抖音", "code": "douyin"},
    ]
    for p in platforms:
        existing = db.query(Platform).filter(Platform.code == p["code"]).first()
        if not existing:
            db.add(Platform(**p))
    db.commit()
    print("[2/5] Platforms seeded.")
    return {p.code: p for p in db.query(Platform).all()}


def seed_channels(db, platforms):
    """Seed sample channels from the Excel reference (远方超市 etc.)."""
    meituan = platforms.get("meituan")
    eleme = platforms.get("eleme")

    channels_data = [
        # 美团 channels
        {"name": "远方超市（超达大路店）", "channel_type": "KA超市", "platform_id": meituan.id if meituan else None, "platform_store_id": "21614410", "region": "吉林"},
        {"name": "远方超市（临河街店）", "channel_type": "KA超市", "platform_id": meituan.id if meituan else None, "platform_store_id": "21614415", "region": "吉林"},
        {"name": "远方超市(越达店)", "channel_type": "KA超市", "platform_id": meituan.id if meituan else None, "platform_store_id": "20850264", "region": "吉林"},
        {"name": "优客超市", "channel_type": "便利", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "金文汇", "channel_type": "便利", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "每日隆", "channel_type": "便利", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "新天地", "channel_type": "便利", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "大润发", "channel_type": "超市", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "小酒喔", "channel_type": "酒专营", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        {"name": "欧亚超市", "channel_type": "KA超市", "platform_id": meituan.id if meituan else None, "region": "吉林"},
        # 饿了么 channels
        {"name": "远方超市(崇智路店)", "channel_type": "KA超市", "platform_id": eleme.id if eleme else None, "platform_store_id": "1259126285", "region": "吉林"},
        {"name": "远方超市(富豪店)", "channel_type": "KA超市", "platform_id": eleme.id if eleme else None, "platform_store_id": "524531863", "region": "吉林"},
        {"name": "远方超市(光谷大街店)", "channel_type": "KA超市", "platform_id": eleme.id if eleme else None, "platform_store_id": "524471848", "region": "吉林"},
    ]

    for ch in channels_data:
        existing = db.query(Channel).filter(
            Channel.name == ch["name"], Channel.platform_id == ch["platform_id"]
        ).first()
        if not existing:
            db.add(Channel(**ch))
    db.commit()
    print("[3/5] Channels seeded.")
    return db.query(Channel).all()


def seed_products(db):
    """Seed sample products from the Excel reference."""
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
        {"upc": "6901035627771", "name": "青岛啤酒1L经典", "brand_series": "青岛经典", "center_series": None, "detail_series": None, "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035626729", "name": "青岛啤酒1L茉莉花", "brand_series": "青岛经典", "center_series": None, "detail_series": None, "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035625906", "name": "青岛啤酒1L原酿", "brand_series": "青岛经典", "center_series": None, "detail_series": None, "spec": "1000", "pack_quantity": 1},
        {"upc": "6901035297776", "name": "青岛啤酒A3系列10.7度500ml*12听/箱", "brand_series": "青岛奥古特", "center_series": "青岛听装", "detail_series": "奥古特听装", "spec": "500", "pack_quantity": 12},
        {"upc": "6901035267779", "name": "青岛啤酒A3系列10.7度500ml*3听/箱", "brand_series": "青岛奥古特", "center_series": "青岛听装", "detail_series": "奥古特听装", "spec": "500", "pack_quantity": 3},
    ]

    for p in products_data:
        existing = db.query(Product).filter(Product.upc == p["upc"]).first()
        if not existing:
            db.add(Product(**p))
    db.commit()
    print("[4/5] Products seeded.")
    return db.query(Product).all()


def seed_sample_activity(db, channels, products, platforms):
    """Create a sample activity to demonstrate the workflow."""
    existing = db.query(Activity).filter(Activity.mechanism == "满79减30（品18）").first()
    if existing:
        print("[5/5] Sample activity already exists, skipping.")
        return

    # Get a client user or create one
    client = db.query(User).filter(User.username == "client_jilin").first()
    if not client:
        client = User(
            username="client_jilin",
            password_hash=hash_password("client123456"),
            role="client",
            real_name="吉林提报员",
            region="吉林省区",
            status="active",
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    meituan = platforms.get("meituan")
    # Pick some channels and products
    ch_ids = [ch for ch in channels if ch.region == "吉林" and ch.channel_type == "便利"][:4]
    prod_sample = products[:8]

    act = Activity(
        title="吉林省区4月满减活动",
        region="吉林省区",
        activity_time="周六日",
        mechanism="满79减30（品18）",
        channel_type="便利",
        platform_id=meituan.id if meituan else None,
        voucher_quantity=80000,
        budget=80000,
        remarks="每个用户ID每天限一个",
        prefix="区域下沉",
        brand="青啤",
        status="submitted",
        created_by=client.id,
    )
    act.channels = ch_ids
    act.products = prod_sample
    db.add(act)

    # Also seed a cost record
    cost = CostRecord(
        sales_unit="吉林省区",
        platform_id=meituan.id if meituan else None,
        plan_amount=8000000,
        accumulated_cost=794499.65,
        cost_ratio=0.0947,
        transaction_amount=8393818,
        month_cost=794499.65,
        month_cost_ratio=0.0947,
        month_expected_transaction=8393818,
        month="2026-04",
        year=2026,
    )
    db.add(cost)
    db.commit()
    print("[5/5] Sample activity and cost record seeded.")


def main():
    print("=" * 50)
    print("  到家平台提报管理系统 - 数据库初始化")
    print("=" * 50)

    init_db()

    db = SessionLocal()
    try:
        # Ensure admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123456"),
                role="admin",
                real_name="系统管理员",
                status="active",
            )
            db.add(admin)
            db.commit()
            print("[0/5] Admin user created (admin / admin123456)")

        platforms = seed_platforms(db)
        channels = seed_channels(db, platforms)
        products = seed_products(db)
        seed_sample_activity(db, channels, products, platforms)
    finally:
        db.close()

    print()
    print("Initialization complete!")
    print("  Admin login:  admin / admin123456")
    print("  Client login: client_jilin / client123456")
    print()
    print("API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
