from database.supabase_client import supabase


def get_admin_by_telegram_id(telegram_id: int):
    res = (
        supabase.table("admins")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return res.data


def create_admin(telegram_id: int, first_name: str, last_name: str):
    res = (
        supabase.table("admins")
        .insert({
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name
        })
        .execute()
    )
    return res.data