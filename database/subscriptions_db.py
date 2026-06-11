from datetime import datetime, timezone, timedelta
from appwrite.query import Query
from appwrite.id import ID
from database.client import db
from utils.config import APPWRITE_DATABASE_ID, APPWRITE_SUBSCRIPTIONS_COLLECTION

COL = APPWRITE_SUBSCRIPTIONS_COLLECTION
DB = APPWRITE_DATABASE_ID


def get_subscription(telegram_id: int) -> dict | None:
    try:
        res = db.list_documents(DB, COL, queries=[Query.equal("telegram_id", telegram_id)])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception:
        return None


def create_or_renew_subscription(telegram_id: int, days: int = 30) -> dict:
    existing = get_subscription(telegram_id)
    expires = (datetime.now(timezone.utc) + timedelta(days=days)).date().isoformat()
    if existing:
        return db.update_document(DB, COL, existing["$id"], {
            "plan": "premium",
            "expires_at": expires,
        })
    return db.create_document(DB, COL, ID.unique(), {
        "telegram_id": telegram_id,
        "plan": "premium",
        "expires_at": expires,
    })


def is_subscription_active(telegram_id: int) -> bool:
    sub = get_subscription(telegram_id)
    if not sub:
        return False
    expires_at = sub.get("expires_at", "")
    try:
        return datetime.fromisoformat(expires_at).date() >= datetime.now(timezone.utc).date()
    except Exception:
        return False
