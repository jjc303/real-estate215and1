"""种子数据生成脚本。

生成 4000+ 用户、1000+ 房源、500+ 合同、1500+ 账单等数据。

用法：
  docker exec rent_backend python scripts/seed_data.py

前置条件：
  - backend/seed_assets/images/ 下有 house_01.jpg ~ house_21.jpg
  - backend/seed_assets/videos/ 下有 tour_01.mp4 ~ tour_03.mp4
"""

from __future__ import annotations

import random
import shutil
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from faker import Faker
from werkzeug.security import generate_password_hash

from app.factory import create_app
from app.core.database import SessionLocal
from app.common.enums import (
    HouseStatus, ContractStatus, BillStatus, BillType,
    RepairStatus, ComplaintStatus, NewsStatus,
)
from app.modules.user.model import User
from app.modules.house.model import House
from app.modules.house_image.model import HouseImage
from app.modules.house_video.model import HouseVideo
from app.modules.contract.model import Contract
from app.modules.bill.model import Bill
from app.modules.repair.model import Repair
from app.modules.complaint.model import Complaint
from app.modules.news.model import News
from app.modules.favorite.model import Favorite
from app.modules.conversation.model import Conversation, Message
from app.modules.appointment.model import Appointment

PASSWORD_HASH = generate_password_hash("123456")
fake = Faker("zh_CN")

SEED_IMAGES_DIR = BACKEND_DIR / "seed_assets" / "images"
SEED_VIDEOS_DIR = BACKEND_DIR / "seed_assets" / "videos"
UPLOAD_ROOT = BACKEND_DIR / "uploads"

HOUSE_TYPES = ["1室1厅", "1室0厅", "2室1厅", "2室2厅", "3室1厅", "3室2厅", "4室2厅"]
DECORATIONS = ["毛坯", "简装", "精装", "豪装"]
ORIENTATIONS = ["东", "南", "西", "北", "南北", "东南"]
REGIONS = ["芙蓉区", "天心区", "岳麓区", "开福区", "雨花区", "望城区", "长沙县"]
COMMUNITIES = [
    "阳光城", "恒大华府", "万科城", "保利麓谷", "中海国际",
    "湘江世纪城", "北辰三角洲", "梅溪湖一号", "月亮岛",
    "八方小区", "钰龙天下", "江山帝景", "麓山名园",
]
BILL_REMARKS = ["本月租金", "上期租金", "水电费代收", "物业费", None]
NEWS_TITLES = [
    "关于规范租赁合同签署流程的通知",
    "夏季用电安全温馨提示",
    "平台新增视频看房功能",
    "房东收入看板功能上线",
    "关于防范租房诈骗的公告",
    "国庆假期服务安排通知",
    "平台系统升级维护通知",
    "长沙市房屋租赁登记备案指南",
    "冬季房屋设施保养建议",
    "打击违规转租行为的公告",
]
BATCH_SIZE = 200


def log(msg: str) -> None:
    t = datetime.now().strftime("%H:%M:%S")
    print(f"[{t}] {msg}")


def get_image_list() -> list[Path]:
    """获取 seed_assets/images/ 下的所有图片文件。"""
    files = sorted(SEED_IMAGES_DIR.glob("house_*.jpg"))
    if not files:
        log("⚠ 没有找到图片文件，跳过图片创建")
    return files


def get_video_list() -> list[Path]:
    """获取 seed_assets/videos/ 下的所有视频文件。"""
    files = sorted(SEED_VIDEOS_DIR.glob("tour_*.mp4"))
    if not files:
        log("⚠ 没有找到视频文件，跳过视频创建")
    return files


def create_users(db, count: int, role: str) -> list[int]:
    """批量创建用户，返回 id 列表。"""
    ids = []
    for i in range(count):
        username = f"{role}_{i:05d}"
        user = User(
            username=username,
            password=PASSWORD_HASH,
            role=role,
            phone=fake.phone_number(),
            email=f"{username}@mail.com",
            status="active",
        )
        db.add(user)
        db.flush()
        ids.append(user.id)
        if (i + 1) % BATCH_SIZE == 0:
            db.commit()
            log(f"  created {i + 1}/{count} {role}s")
    db.commit()
    log(f"  total {role}s: {len(ids)}")
    return ids


def create_houses(
    db, landlord_ids: list[int], image_files: list[Path], video_files: list[Path]
) -> list[int]:
    """批量创建房源，返回 (house_id, landlord_id) 列表。"""
    total_landlords = len(landlord_ids)
    counts = []
    # 60% → 1套, 30% → 2套, 10% → 3套
    for i in range(total_landlords):
        r = random.random()
        if r < 0.6:
            counts.append(1)
        elif r < 0.9:
            counts.append(2)
        else:
            counts.append(3)

    img_count = len(image_files)
    video_count = len(video_files)
    house_ids = []
    house_counter = 0

    for idx, landlord_id in enumerate(landlord_ids):
        for _ in range(counts[idx]):
            house_counter += 1
            region = random.choice(REGIONS)
            community = random.choice(COMMUNITIES)
            house_type = random.choice(HOUSE_TYPES)
            area = round(random.uniform(25, 160), 2)
            rent = random.randint(800, 8000)
            deposit = rent * random.choice([1, 1, 1, 2])

            house = House(
                landlord_id=landlord_id,
                title=f"{community} {house_type} {area}㎡ {'精装出租' if random.random() > 0.3 else '首次出租'}",
                address=f"{region} {community} {random.randint(1, 30)}栋{random.randint(1, 34)}层",
                region=region,
                community=community,
                house_type=house_type,
                area=Decimal(str(area)),
                rent=Decimal(str(rent)),
                deposit=Decimal(str(deposit)),
                decoration=random.choice(DECORATIONS),
                floor=f"{random.randint(1, 33)}/{random.randint(6, 34)}",
                orientation=random.choice(ORIENTATIONS),
                description=f"{community}优质{'房源' if random.random() > 0.3 else '好房'}，{'交通便利' if random.random() > 0.5 else '环境优美'}，{'拎包入住' if random.random() > 0.4 else '随时看房'}。",
                status=random.choices(
                    [HouseStatus.LISTED, HouseStatus.DRAFT, HouseStatus.RENTED, HouseStatus.OFFLINE],
                    weights=[70, 5, 20, 5],
                )[0],
            )
            db.add(house)
            db.flush()

            # 创建图片记录（每套 3 张）
            for pi in range(3):
                src_idx = ((house_counter - 1) * 3 + pi) % img_count if img_count else 0
                src_img = image_files[src_idx]
                ext = src_img.suffix
                obj_key = f"houses/{house.id}/img_{pi}{ext}"
                dest = UPLOAD_ROOT / obj_key
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_img, dest)
                except Exception as e:
                    log(f"  ⚠ copy image failed: {e}")

                img = HouseImage(
                    house_id=house.id,
                    url=f"/uploads/{obj_key}",
                    object_key=obj_key,
                    mime_type=f"image/{ext[1:]}",
                    size_bytes=dest.stat().st_size if dest.exists() else 0,
                    sort_order=pi,
                    is_cover=(pi == 0),
                    status="active",
                )
                db.add(img)

            # 给前 100 套房配上视频
            if house_counter <= 100 and video_count > 0:
                src_video = video_files[(house_counter - 1) % video_count]
                v_ext = src_video.suffix
                v_obj_key = f"houses/{house.id}/videos/tour{v_ext}"
                v_dest = UPLOAD_ROOT / v_obj_key
                v_dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_video, v_dest)
                except Exception as e:
                    log(f"  ⚠ copy video failed: {e}")

                video = HouseVideo(
                    house_id=house.id,
                    url=f"/uploads/{v_obj_key}",
                    object_key=v_obj_key,
                    mime_type=f"video/{v_ext[1:]}",
                    size_bytes=v_dest.stat().st_size if v_dest.exists() else 0,
                    duration=random.randint(10, 60),
                    status="active",
                )
                db.add(video)

            house_ids.append((house.id, landlord_id))

            if house_counter % 50 == 0:
                db.commit()
                log(f"  created {house_counter} houses")

    db.commit()
    log(f"  total houses: {len(house_ids)}")
    return house_ids


def create_contracts(db, house_ids: list[tuple], tenant_ids: list[int]) -> list[int]:
    """批量创建合同，返回 contract.id 列表。"""
    active_contracts = []
    all_contracts = []
    target = 500
    total_houses = len(house_ids)

    for i in range(min(target, total_houses)):
        house_id, landlord_id = house_ids[i]
        tenant_id = random.choice(tenant_ids)
        days_offset = random.randint(-60, -1)
        start = date.today() + timedelta(days=days_offset)
        end = start + timedelta(days=random.choice([180, 365, 365, 730]))

        status = random.choices(
            ["active", "terminated", "pending"],
            weights=[60, 30, 10],
        )[0]

        from app.modules.appointment.model import Appointment
        dummy_appt = Appointment(
            house_id=house_id,
            tenant_id=tenant_id,
            landlord_id=landlord_id,
            appointment_time=datetime.now() + timedelta(days=30),
            status="confirmed",
            remark="auto-generated",
        )
        db.add(dummy_appt)
        db.flush()

        contract = Contract(
            house_id=house_id,
            tenant_id=tenant_id,
            landlord_id=landlord_id,
            appointment_id=dummy_appt.id,
            start_date=start,
            end_date=end,
            monthly_rent=Decimal(str(random.randint(1000, 6000))),
            deposit=Decimal(str(random.randint(1000, 6000))),
            status=status,
            remark=None,
        )
        db.add(contract)
        db.flush()

        if status == ContractStatus.ACTIVE:
            active_contracts.append(contract)
        all_contracts.append(contract)

        if (i + 1) % 50 == 0:
            db.commit()
            log(f"  created {i + 1}/{target} contracts")

    db.commit()
    log(f"  contracts: {len(all_contracts)} (active: {len(active_contracts)})")
    return active_contracts


def create_bills(db, active_contracts: list) -> None:
    """批量创建账单。"""
    bill_count = 0
    for contract in active_contracts:
        periods = random.randint(2, 6)
        for p in range(periods):
            due = contract.start_date + timedelta(days=30 * p)
            if due > date.today() + timedelta(days=30):
                continue
            status = random.choices(
                [BillStatus.PAID, BillStatus.UNPAID, BillStatus.OVERDUE],
                weights=[60, 25, 15],
            )[0]
            bill = Bill(
                contract_id=contract.id,
                house_id=contract.house_id,
                tenant_id=contract.tenant_id,
                landlord_id=contract.landlord_id,
                bill_type=random.choice(["rent", "rent", "rent", "deposit"]),
                amount=contract.monthly_rent,
                due_date=due,
                status=status,
                remark=random.choice(BILL_REMARKS),
            )
            db.add(bill)
            bill_count += 1

            if bill_count % 200 == 0:
                db.commit()
                log(f"  created {bill_count} bills")

    db.commit()
    log(f"  total bills: {bill_count}")


def create_repairs(db, active_contracts: list) -> None:
    """批量创建报修。"""
    count = 0
    targets = min(200, len(active_contracts))
    for contract in random.sample(active_contracts, targets):
        repair = Repair(
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            contract_id=contract.id,
            description=random.choice([
                "水龙头漏水", "马桶堵塞", "灯泡坏了", "热水器不热",
                "空调不制冷", "门锁坏了", "下水道堵塞", "墙面开裂",
                "窗户关不上", "插座没电",
            ]),
            status=random.choice([
                "pending", "processing",
                "completed", "closed",
            ]),
        )
        db.add(repair)
        count += 1
        if count % 100 == 0:
            db.commit()
    db.commit()
    log(f"  repairs: {count}")


def create_complaints(db, active_contracts: list) -> None:
    """批量创建投诉。"""
    count = 0
    targets = min(200, len(active_contracts))
    for contract in random.sample(active_contracts, targets):
        complaint = Complaint(
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            contract_id=contract.id,
            description=random.choice([
                "噪音扰民，多次联系房东未处理",
                "房屋维修不及时，已经反映一周了没有任何回应",
                "押金退还纠纷，希望能尽快解决",
                "配套设施不完善，存在安全隐患",
            ]),
            status=random.choice([
                "pending", "processing",
                "resolved", "closed",
            ]),
        )
        db.add(complaint)
        count += 1
        if count % 100 == 0:
            db.commit()
    db.commit()
    log(f"  complaints: {count}")


def create_news(db) -> None:
    """创建新闻公告。"""
    for idx, title in enumerate(NEWS_TITLES):
        news = News(
            title=title,
            content=fake.paragraph(nb_sentences=8),
            status="published",
            author_id=1,
        )
        db.add(news)
    db.commit()
    log(f"  news: {len(NEWS_TITLES)}")


def _has_seed_data(db) -> bool:
    result = db.execute(
        __import__("sqlalchemy").text(
            "SELECT COUNT(*) FROM users WHERE username LIKE 'admin_%'"
        )
    )
    return result.scalar() > 0


def main() -> None:
    app = create_app()
    with app.app_context():
        db = SessionLocal()
        try:
            if _has_seed_data(db):
                log("Seed data already exists, skipping")
                return

            log("=" * 50)
            log("Starting seed data generation...")
            log("=" * 50)

            image_files = get_image_list()
            video_files = get_video_list()

            # 1. Users
            log("[1/6] Creating users...")
            admin_ids = create_users(db, 2, "admin")
            landlord_ids = create_users(db, 1000, "landlord")
            tenant_ids = create_users(db, 3000, "tenant")

            # 2. Houses
            log("[2/6] Creating houses with images/videos...")
            house_ids = create_houses(db, landlord_ids, image_files, video_files)

            # 3. Contracts
            log("[3/6] Creating contracts...")
            active_contracts = create_contracts(db, house_ids, tenant_ids)

            # 4. Bills
            log("[4/6] Creating bills...")
            create_bills(db, active_contracts)

            # 5. Repairs & Complaints
            log("[5/6] Creating repairs & complaints...")
            create_repairs(db, active_contracts)
            create_complaints(db, active_contracts)

            # 6. News
            log("[6/6] Creating news...")
            create_news(db)

            # 7. Ensure admin user exists
            log("[7/7] Finalizing...")
            db.execute(
                __import__("sqlalchemy").text(
                    "INSERT IGNORE INTO users (username, password, role, status) "
                    "VALUES ('admin', :pw, 'admin', 'active')"
                ),
                {"pw": PASSWORD_HASH},
            )
            db.commit()

            # 8. Spread bill timestamps across months for income chart
            log("[8/8] Spreading bill dates for monthly income...")
            rows = db.execute(
                __import__("sqlalchemy").text(
                    "SELECT id FROM bills WHERE status = 'paid'"
                )
            ).fetchall()
            paid_count = 0
            for (bid,) in rows:
                offset_days = random.randint(30, 180)
                new_date = datetime.now() - timedelta(days=offset_days)
                db.execute(
                    __import__("sqlalchemy").text(
                        "UPDATE bills SET created_at = :dt, updated_at = :dt WHERE id = :id"
                    ),
                    {"dt": new_date, "id": bid},
                )
                paid_count += 1
            db.commit()
            log(f"  updated {paid_count} paid bills to past months")

            # 9. Create payment records for paid bills (for admin statistics)
            log("[9/9] Creating payment records...")
            from app.modules.payment.model import Payment
            rows = db.execute(
                __import__("sqlalchemy").text(
                    "SELECT id, amount, updated_at, tenant_id, contract_id, house_id, landlord_id FROM bills WHERE status = 'paid'"
                )
            ).fetchall()
            payment_count = 0
            for bid, amount, paid_at, payer_id, cid, hid, lid in rows:
                payment = Payment(
                    bill_id=bid,
                    contract_id=cid,
                    house_id=hid,
                    tenant_id=payer_id,
                    landlord_id=lid,
                    amount=amount,
                    payment_method="mock",
                    status="success",
                    paid_at=paid_at,
                )
                db.add(payment)
                payment_count += 1
                if payment_count % 200 == 0:
                    db.commit()
            db.commit()
            log(f"  created {payment_count} payment records")

            log("=" * 50)
            log("✅ Seed data complete!")
            log("=" * 50)

        except Exception as e:
            db.rollback()
            log(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            db.close()


if __name__ == "__main__":
    main()
