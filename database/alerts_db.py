import logging
from datetime import datetime, timezone
from appwrite.query import Query
from appwrite.id import ID
from database.client import db
from utils.config import APPWRITE_DATABASE_ID, APPWRITE_ALERTS_COLLECTION

logger = logging.getLogger(__name__)

COL = APPWRITE_ALERTS_COLLECTION
DB = APPWRITE_DATABASE_ID

FREE_ALERT_LIMIT = 3
FREE_ASSETS = {"USDNGN"}


def get_user_alerts(telegram_id: int) -> list[dict]:
    try:
        res = db.list_documents(DB, COL, queries=[
            Query.equal("telegram_id", telegram_id),
            Query.equal("active", True),
            Query.limit(50),
        ])
        return res.get("documents", [])
    except Exception as e:
        # Log the real reason instead of silently returning an empty list —
        # an empty list here is indistinguishable from "no alerts" to the user,
        # which previously hid real Appwrite errors (e.g. missing index,
        # type mismatch on telegram_id) as a false "no alerts" screen.
        logger.error(f"get_user_alerts failed for {telegram_id}: {e}")
        return []


def get_all_active_alerts() -> list[dict]:
    try:
        res = db.list_documents(DB, COL, queries=[
            Query.equal("active", True),
            Query.limit(500),
        ])
        return res.get("documents", [])
    except Exception as e:
        logger.error(f"get_all_active_alerts failed: {e}")
        return []


def create_alert(telegram_id: int, asset: str, condition: str, target: float) -> dict:
    return db.create_document(DB, COL, ID.unique(), {
        "telegram_id": telegram_id,
        "asset": asset,
        "condition": condition,
        "target": target,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


def delete_alert(document_id: str) -> None:
    db.delete_document(DB, COL, document_id)


def deactivate_alert(document_id: str) -> None:
    db.update_document(DB, COL, document_id, {"active": False})


def count_user_alerts(telegram_id: int) -> int:
    return len(get_user_alerts(telegram_id))
        
