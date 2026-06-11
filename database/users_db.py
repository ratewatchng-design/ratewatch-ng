from datetime import datetime, timezone
from appwrite.query import Query
from appwrite.id import ID
from database.client import db
from utils.config import APPWRITE_DATABASE_ID, APPWRITE_USERS_COLLECTION

COL = APPWRITE_USERS_COLLECTION
DB = APPWRITE_DATABASE_ID


def get_user(telegram_id: int) -> dict | None:
    try:
        res = db.list_documents(DB, COL, queries=[Query.equal("telegram_id", telegram_id)])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception:
        return None


def create_user(telegram_id: int, username: str, first_name: str) -> dict:
    return db.create_document(DB, COL, ID.unique(), {
        "telegram_id": telegram_id,
        "username": username or "",
        "first_name": first_name or "",
        "plan": "free",
        "referrals": 0,
        "notification_style": "instant",
        "quiet_hours": "off",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


def get_or_create_user(telegram_id: int, username: str, first_name: str) -> dict:
    user = get_user(telegram_id)
    if not user:
        user = create_user(telegram_id, username, first_name)
    return user


def update_user(document_id: str, data: dict) -> dict:
    return db.update_document(DB, COL, document_id, data)


def increment_referrals(telegram_id: int) -> None:
    user = get_user(telegram_id)
    if user:
        db.update_document(DB, COL, user["$id"], {
            "referrals": user.get("referrals", 0) + 1
        })


def get_all_users() -> list[dict]:
    try:
        res = db.list_documents(DB, COL, queries=[Query.limit(500)])
        return res.get("documents", [])
    except Exception:
        return []


def get_premium_users() -> list[dict]:
    try:
        res = db.list_documents(DB, COL, queries=[
            Query.equal("plan", "premium"),
            Query.limit(500)
        ])
        return res.get("documents", [])
    except Exception:
        return []


def is_premium(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    return (user or {}).get("plan") == "premium"
