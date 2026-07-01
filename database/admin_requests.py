from datetime import datetime, timezone

from database.supabase_client import supabase


def get_pending_request_by_telegram_id(telegram_id: int):
    res = (
        supabase.table("admin_requests")
        .select("*")
        .eq("telegram_id", telegram_id)
        .eq("status", "pending")
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]


def create_admin_request(
    telegram_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None
):
    res = (
        supabase.table("admin_requests")
        .insert({
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "status": "pending"
        })
        .execute()
    )

    return res.data[0]


def get_admin_request_by_id(request_id: str):
    res = (
        supabase.table("admin_requests")
        .select("*")
        .eq("id", request_id)
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]


def approve_admin_request(request_id: str, reviewed_by: int):
    res = (
        supabase.table("admin_requests")
        .update({
            "status": "approved",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", request_id)
        .execute()
    )

    return res.data


def reject_admin_request(request_id: str, reviewed_by: int):
    res = (
        supabase.table("admin_requests")
        .update({
            "status": "rejected",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", request_id)
        .execute()
    )

    return res.data