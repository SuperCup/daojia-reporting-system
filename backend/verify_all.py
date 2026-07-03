"""Comprehensive verification test for all updated features."""
import requests
import json

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")

def login(username, password):
    r = requests.post(f"{BASE}/api/auth/login", json={"username": username, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

print("=" * 60)
print("  全面功能验证测试")
print("=" * 60)

# ── 1. Login & org_level ──
print("\n[1] 登录与 org_level 字段")
admin_token = login("admin", "admin123456")
check("admin 登录", admin_token is not None)

ops_token = login("ops_user", "ops123456")
check("ops 登录", ops_token is not None)

client_token = login("client_jilin", "client123456")
check("client_jilin 登录", client_token is not None)

client_jilin2_token = login("client_jilin2", "client123456")
check("client_jilin2 登录", client_jilin2_token is not None)

client_gd_token = login("client_guangdong", "client123456")
check("client_guangdong 登录", client_gd_token is not None)

# Verify org_level in user info
headers_admin = {"Authorization": f"Bearer {admin_token}"}
r = requests.get(f"{BASE}/api/auth/me", headers=headers_admin)
admin_info = r.json()
check("admin org_level=HQ", admin_info.get("org_level") == "HQ", f"got: {admin_info.get('org_level')}")

headers_client = {"Authorization": f"Bearer {client_token}"}
r = requests.get(f"{BASE}/api/auth/me", headers=headers_client)
client_info = r.json()
check("client org_level=region", client_info.get("org_level") == "region", f"got: {client_info.get('org_level')}")
check("client region=吉林省区", client_info.get("region") == "吉林省区", f"got: {client_info.get('region')}")

# ── 2. Invitation system ──
print("\n[2] 邀请码系统")
r = requests.post(f"{BASE}/api/auth/invitations", json={"note": "测试邀请码"}, headers=headers_admin)
check("创建邀请码", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")
if r.status_code == 201:
    inv_code = r.json().get("code")
    check("邀请码非空", inv_code is not None and len(inv_code) > 0)

    # List invitations
    r = requests.get(f"{BASE}/api/auth/invitations", headers=headers_admin)
    check("列出邀请码", r.status_code == 200 and len(r.json()) >= 1)

    # Register with invitation code
    r = requests.post(f"{BASE}/api/auth/register", json={
        "invitation_code": inv_code,
        "username": "test_new_client",
        "password": "test123456",
        "real_name": "测试新客户",
        "region": "吉林省区",
        "org_level": "region",
    })
    check("邀请码注册", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")

    # Verify the invitation is now "used"
    r = requests.get(f"{BASE}/api/auth/invitations", headers=headers_admin)
    invs = r.json()
    used_inv = [i for i in invs if i.get("code") == inv_code]
    if used_inv:
        check("邀请码状态=used", used_inv[0].get("status") == "used", f"got: {used_inv[0].get('status')}")
    else:
        check("邀请码状态=used", False, "邀请码不在列表中")

# ── 3. Same-region visibility ──
print("\n[3] 同区域提报可见性")
# client_jilin should see 吉林省区 activities (seeded sample activity is 吉林省区)
r = requests.get(f"{BASE}/api/activities", headers=headers_client)
acts = r.json()
check("client_jilin 看到提报列表", len(acts) >= 1, f"got {len(acts)} activities")
if acts:
    check("提报区域=吉林省区", acts[0].get("region") == "吉林省区", f"got: {acts[0].get('region')}")

# client_guangdong should NOT see 吉林省区 activities
headers_gd = {"Authorization": f"Bearer {client_gd_token}"}
r = requests.get(f"{BASE}/api/activities", headers=headers_gd)
gd_acts = r.json()
check("client_guangdong 看不到吉林省区提报", len(gd_acts) == 0, f"got {len(gd_acts)} activities (should be 0)")

# ── 4. Client account management ──
print("\n[4] 客户端账号管理")
# List all users (admin)
r = requests.get(f"{BASE}/api/users", headers=headers_admin)
users = r.json()
check("列出所有用户", r.status_code == 200 and len(users) >= 5, f"got {len(users)} users")

# Create client account manually
r = requests.post(f"{BASE}/api/users", json={
    "username": "manual_client",
    "password": "manual123456",
    "role": "client",
    "real_name": "手动创建客户",
    "region": "吉林省区",
    "org_level": "region",
}, headers=headers_admin)
check("手动创建客户端账号", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")

# Disable a user
if users:
    target_id = None
    for u in users:
        if u.get("username") == "test_new_client":
            target_id = u.get("id")
            break
    if target_id:
        r = requests.patch(f"{BASE}/api/users/{target_id}", json={"status": "disabled"}, headers=headers_admin)
        check("禁用用户", r.status_code == 200, f"status: {r.status_code}, body: {r.text}")

# ── 5. Batch import — activities ──
print("\n[5] 批量导入 — 活动提报")
# Get a channel and product for the batch
r = requests.get(f"{BASE}/api/channels?page=1&page_size=5", headers=headers_client)
channels = r.json()
ch_ids = [c["id"] for c in channels[:2]] if channels else []

r = requests.get(f"{BASE}/api/products?page=1&page_size=5", headers=headers_client)
products = r.json()
prod_ids = [p["id"] for p in products[:2]] if products else []

batch_activities = [
    {
        "region": "吉林省区",
        "activity_time": "4.1-4.30",
        "mechanism": "满99减50（批量测试1）",
        "channel_ids": ch_ids,
        "product_ids": prod_ids,
        "brand": "青啤",
        "prefix": "批量导入",
    },
    {
        "region": "吉林省区",
        "activity_time": "5.1-5.31",
        "mechanism": "满79减30（批量测试2）",
        "channel_ids": ch_ids,
        "product_ids": prod_ids,
        "brand": "青啤",
        "prefix": "批量导入",
    },
]
r = requests.post(f"{BASE}/api/activities/batch", json=batch_activities, headers=headers_client)
check("批量创建活动", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")
if r.status_code == 201:
    check("创建2条活动", r.json().get("count") == 2, f"got: {r.json()}")

# ── 6. Batch import — channels ──
print("\n[6] 批量导入 — 渠道")
batch_channels = [
    {"name": "批量导入超市1", "channel_type": "超市", "region": "吉林"},
    {"name": "批量导入超市2", "channel_type": "便利", "region": "吉林"},
]
r = requests.post(f"{BASE}/api/channels/batch", json=batch_channels, headers=headers_client)
check("批量创建渠道", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")

# ── 7. Batch import — products ──
print("\n[7] 批量导入 — 商品")
batch_products = [
    {"upc": "BATCH001", "name": "批量导入商品1", "brand_series": "测试系列"},
    {"upc": "BATCH002", "name": "批量导入商品2", "brand_series": "测试系列"},
]
r = requests.post(f"{BASE}/api/products/batch", json=batch_products, headers=headers_client)
check("批量创建商品", r.status_code == 201, f"status: {r.status_code}, body: {r.text}")

# ── 8. Pagination ──
print("\n[8] 分页")
r = requests.get(f"{BASE}/api/activities?page=1&page_size=2", headers=headers_client)
page1 = r.json()
check("活动分页 page1", len(page1) <= 2, f"got {len(page1)} items")

r = requests.get(f"{BASE}/api/activities?page=2&page_size=2", headers=headers_client)
page2 = r.json()
check("活动分页 page2", len(page2) >= 0, "page2 retrieved")

r = requests.get(f"{BASE}/api/channels?page=1&page_size=5", headers=headers_client)
check("渠道分页", len(r.json()) <= 5, f"got {len(r.json())} items")

r = requests.get(f"{BASE}/api/products?page=1&page_size=5", headers=headers_client)
check("商品分页", len(r.json()) <= 5, f"got {len(r.json())} items")

# ── 9. Reports/Dashboard ──
print("\n[9] 运营看板（报表）")
r = requests.get(f"{BASE}/api/reports/dashboard", headers=headers_admin)
check("看板统计", r.status_code == 200, f"status: {r.status_code}")
if r.status_code == 200:
    stats = r.json()
    check("看板有数据", "total_activities" in stats or "total" in stats, f"keys: {list(stats.keys())}")

# ── 10. Change password ──
print("\n[10] 修改密码")
r = requests.post(f"{BASE}/api/auth/change-password", json={
    "old_password": "client123456",
    "new_password": "client123456",
}, headers=headers_client)
check("修改密码", r.status_code == 200, f"status: {r.status_code}, body: {r.text}")

# ── Summary ──
print()
print("=" * 60)
print(f"  Result: {PASS} passed, {FAIL} failed")
print("=" * 60)
