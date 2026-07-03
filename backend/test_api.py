"""
Comprehensive API test script for the reporting system.
Tests all business flows: auth, users, platforms, channels, products, activities, reports.

Usage:
    python test_api.py

Prerequisites:
    - Backend running at http://localhost:8000
    - Database initialized (python init_db.py)
"""
import requests
import sys
import json

BASE_URL = "http://localhost:8000"
PASS = 0
FAIL = 0
RESULTS = []


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        RESULTS.append(f"  [PASS] {name}")
    else:
        FAIL += 1
        RESULTS.append(f"  [FAIL] {name} — {detail}")


def section(title):
    RESULTS.append(f"\n{'='*50}")
    RESULTS.append(f"  {title}")
    RESULTS.append(f"{'='*50}")


# ── 1. Health Check ──
section("1. Health Check")
try:
    r = requests.get(f"{BASE_URL}/api/health", timeout=5)
    test("Health endpoint", r.status_code == 200 and r.json().get("status") == "ok")
except Exception as e:
    test("Health endpoint", False, str(e))
    print("\nBackend not running. Start it first: uvicorn app.main:app --reload")
    sys.exit(1)

# ── 2. Authentication ──
section("2. Authentication")
# Login as admin
r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123456"})
test("Admin login", r.status_code == 200, r.text)
admin_token = r.json().get("access_token") if r.status_code == 200 else None
admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

# Login as client
r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "client_jilin", "password": "client123456"})
test("Client login", r.status_code == 200, r.text)
client_token = r.json().get("access_token") if r.status_code == 200 else None
client_headers = {"Authorization": f"Bearer {client_token}"} if client_token else {}

# Wrong password
r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "wrong"})
test("Wrong password rejected", r.status_code == 401)

# Get current user
r = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers)
test("Get current user", r.status_code == 200 and r.json().get("username") == "admin")

# ── 3. Registration & User Management ──
section("3. Registration & User Management")
# Register a new client
r = requests.post(f"{BASE_URL}/api/auth/register", json={
    "username": "test_client_001",
    "password": "test123456",
    "real_name": "测试用户",
    "region": "测试区域",
    "phone": "13800000000",
})
test("Client registration", r.status_code == 201, r.text)
test("Registration creates pending status", r.json().get("status") == "pending")

# Admin lists pending users
r = requests.get(f"{BASE_URL}/api/users?status=pending", headers=admin_headers)
test("List pending users", r.status_code == 200)
pending_user_id = None
for u in r.json():
    if u.get("username") == "test_client_001":
        pending_user_id = u["id"]
        break
test("Found pending user", pending_user_id is not None)

# Approve the pending user
if pending_user_id:
    r = requests.post(f"{BASE_URL}/api/users/{pending_user_id}/approve", headers=admin_headers)
    test("Approve user", r.status_code == 200 and r.json().get("status") == "active")

# Approved user can now login
r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "test_client_001", "password": "test123456"})
test("Approved user can login", r.status_code == 200)

# Admin creates a user
r = requests.post(f"{BASE_URL}/api/users", headers=admin_headers, json={
    "username": "ops_user_001",
    "password": "ops123456",
    "role": "ops",
    "real_name": "运营人员",
    "region": "吉林",
})
test("Admin creates ops user", r.status_code == 201, r.text)

# Client cannot create users (forbidden)
r = requests.post(f"{BASE_URL}/api/users", headers=client_headers, json={
    "username": "hack_user",
    "password": "hack123456",
    "role": "admin",
})
test("Client cannot create users", r.status_code == 403)

# ── 4. Platforms ──
section("4. Platforms")
r = requests.get(f"{BASE_URL}/api/platforms", headers=client_headers)
test("List platforms", r.status_code == 200 and len(r.json()) > 0)
platforms = r.json()
meituan_id = next((p["id"] for p in platforms if p["code"] == "meituan"), None)
test("Meituan platform exists", meituan_id is not None)

# ── 5. Channels ──
section("5. Channels")
r = requests.get(f"{BASE_URL}/api/channels", headers=client_headers, params={"page_size": 200})
test("List channels", r.status_code == 200 and len(r.json()) > 0)
channels = r.json()
test("Has channel types", any(c.get("channel_type") for c in channels))

# Create a channel
r = requests.post(f"{BASE_URL}/api/channels", headers=client_headers, json={
    "name": "测试渠道001",
    "channel_type": "便利",
    "platform_id": meituan_id,
    "platform_store_id": "99999999",
    "region": "吉林",
})
test("Create channel", r.status_code == 201, r.text)
test_channel_id = r.json().get("id") if r.status_code == 201 else None

# Update channel
if test_channel_id:
    r = requests.patch(f"{BASE_URL}/api/channels/{test_channel_id}", headers=client_headers, json={
        "name": "测试渠道_已修改",
        "address": "测试地址",
    })
    test("Update channel", r.status_code == 200 and r.json().get("name") == "测试渠道_已修改")

# ── 6. Products ──
section("6. Products")
r = requests.get(f"{BASE_URL}/api/products", headers=client_headers, params={"page_size": 200})
test("List products", r.status_code == 200 and len(r.json()) > 0)
products = r.json()
test("Products have UPC", all(p.get("upc") for p in products))

# Create a product
r = requests.post(f"{BASE_URL}/api/products", headers=client_headers, json={
    "upc": "6999999999999",
    "name": "测试产品001",
    "brand_series": "测试品牌",
    "spec": "500",
    "pack_quantity": 12,
})
test("Create product", r.status_code == 201, r.text)
test_product_id = r.json().get("id") if r.status_code == 201 else None

# Duplicate UPC rejected
r = requests.post(f"{BASE_URL}/api/products", headers=client_headers, json={
    "upc": "6999999999999",
    "name": "重复UPC产品",
})
test("Duplicate UPC rejected", r.status_code == 400)

# ── 7. Activities (Core Business Flow) ──
section("7. Activities — Core Business Flow")
# Create activity (draft)
r = requests.post(f"{BASE_URL}/api/activities", headers=client_headers, json={
    "region": "吉林省区",
    "activity_time": "4.1-4.30",
    "mechanism": "满79减30（品18）",
    "platform_id": meituan_id,
    "voucher_quantity": 50000,
    "budget": 50000,
    "brand": "青啤",
    "remarks": "每个用户ID每天限一个",
    "channel_ids": [c["id"] for c in channels[:3]],
    "product_ids": [p["id"] for p in products[:5]],
})
test("Create activity (draft)", r.status_code == 201, r.text)
activity_id = r.json().get("id") if r.status_code == 201 else None
test("Activity is draft", activity_id and r.json().get("status") == "draft")
test("Activity has channels", activity_id and len(r.json().get("channels", [])) == 3)
test("Activity has products", activity_id and len(r.json().get("products", [])) == 5)

# Get activity detail
if activity_id:
    r = requests.get(f"{BASE_URL}/api/activities/{activity_id}", headers=client_headers)
    test("Get activity detail", r.status_code == 200)

# Submit activity
if activity_id:
    r = requests.post(f"{BASE_URL}/api/activities/{activity_id}/submit", headers=client_headers)
    test("Submit activity", r.status_code == 200 and r.json().get("status") == "submitted", r.text)

# Client cannot delete submitted activity
if activity_id:
    r = requests.delete(f"{BASE_URL}/api/activities/{activity_id}", headers=client_headers)
    test("Cannot delete submitted activity", r.status_code == 400)

# ── 8. Operations Review Flow ──
section("8. Operations Review Flow")
# Ops views all activities
r = requests.get(f"{BASE_URL}/api/activities", headers=admin_headers, params={"page_size": 100})
test("Ops sees all activities", r.status_code == 200 and len(r.json()) > 0)

# Ops reviews the activity
if activity_id:
    r = requests.post(f"{BASE_URL}/api/activities/{activity_id}/review", headers=admin_headers, json={
        "status": "approved",
        "review_comment": "审核通过，符合要求",
    })
    test("Approve activity", r.status_code == 200 and r.json().get("status") == "approved", r.text)

# Ops cannot review already-reviewed activity
if activity_id:
    r = requests.post(f"{BASE_URL}/api/activities/{activity_id}/review", headers=admin_headers, json={
        "status": "rejected",
    })
    test("Cannot re-review", r.status_code == 400)

# ── 9. Reports & Dashboard ──
section("9. Reports & Dashboard")
r = requests.get(f"{BASE_URL}/api/reports/dashboard", headers=admin_headers)
test("Dashboard stats", r.status_code == 200 and "total_activities" in r.json(), r.text)

r = requests.get(f"{BASE_URL}/api/reports/activities", headers=admin_headers)
test("Activity report", r.status_code == 200 and "items" in r.json())

if activity_id:
    r = requests.get(f"{BASE_URL}/api/reports/activities/{activity_id}/detail", headers=admin_headers)
    test("Activity detail report", r.status_code == 200 and "channels" in r.json())

r = requests.get(f"{BASE_URL}/api/reports/export/summary", headers=admin_headers)
test("Export summary", r.status_code == 200 and "rows" in r.json())

# Client cannot access reports
r = requests.get(f"{BASE_URL}/api/reports/dashboard", headers=client_headers)
test("Client cannot access dashboard", r.status_code == 403)

# ── 10. Cost Records ──
section("10. Cost Records")
r = requests.get(f"{BASE_URL}/api/reports/costs", headers=admin_headers)
test("List costs", r.status_code == 200)

r = requests.post(f"{BASE_URL}/api/reports/costs", headers=admin_headers, json={
    "sales_unit": "吉林省区",
    "platform_id": meituan_id,
    "plan_amount": 5000000,
    "accumulated_cost": 300000,
    "cost_ratio": 0.06,
    "transaction_amount": 5000000,
    "month_cost": 300000,
    "month_cost_ratio": 0.06,
    "month_expected_transaction": 5000000,
    "month": "2026-04",
    "year": 2026,
})
test("Create cost record", r.status_code == 201, r.text)

# ── 11. Authorization Checks ──
section("11. Authorization Checks")
# No token = 401
r = requests.get(f"{BASE_URL}/api/activities")
test("No token = 401", r.status_code == 401)

# Client cannot access ops reports
r = requests.get(f"{BASE_URL}/api/reports/activities", headers=client_headers)
test("Client blocked from reports", r.status_code == 403)

# Client cannot review activities
if activity_id:
    r = requests.post(f"{BASE_URL}/api/activities/{activity_id}/review", headers=client_headers, json={
        "status": "rejected",
    })
    test("Client cannot review", r.status_code == 403)

# ── Summary ──
section("TEST SUMMARY")
RESULTS.append(f"  Total: {PASS + FAIL}  |  Passed: {PASS}  |  Failed: {FAIL}")
RESULTS.append(f"  Result: {'ALL PASSED' if FAIL == 0 else 'SOME FAILED'}")

print("\n".join(RESULTS))
print()
sys.exit(0 if FAIL == 0 else 1)
