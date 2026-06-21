from datetime import datetime, timezone
from appwrite.query import Query
from appwrite.id import ID
from database.client import db
from utils.config import APPWRITE_DATABASE_ID, APPWRITE_REFERRALS_COLLECTION

COL = APPWRITE_REFERRALS_COLLECTION
DB = APPWRITE_DATABASE_ID


def record_referral(referrer_id: int, referred_id: int) -> dict | None:
    # Prevent duplicate referrals
    existing = db.list_documents(DB, COL, queries=[
        Query.equal("referred", referred_id)
    ])
    if existing.get("documents"):
        return None
    return db.create_document(DB, COL, ID.unique(), {
        "referrer": referrer_id,
        "referred": referred_id,
        "created_at": datetime.now(timezone.utc).date().isoformat(),
    })


def get_referral_count(telegram_id: int) -> int:
    try:
        res = db.list_documents(DB, COL, queries=[
            Query.equal("referrer", telegram_id),
            Query.limit(100),
        ])
        return res.get("total", 0)
    except Exception:
        return 0
