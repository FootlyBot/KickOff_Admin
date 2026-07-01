from database.supabase_client import supabase


def get_admin_by_telegram_id(telegram_id: int):
    res = (
        supabase.table("admins")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    return res.data


def get_active_admin_by_telegram_id(telegram_id: int):
    res = (
        supabase.table("admins")
        .select("*")
        .eq("telegram_id", telegram_id)
        .eq("is_active", True)
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]


def get_super_admins():
    res = (
        supabase.table("admins")
        .select("*")
        .eq("role", "super_admin")
        .eq("is_active", True)
        .execute()
    )

    return res.data


def create_admin(
    telegram_id: int,
    first_name: str | None,
    last_name: str | None = None,
    username: str | None = None,
    role: str = "admin"
):
    existing_admin = get_admin_by_telegram_id(telegram_id)

    admin_data = {
        "telegram_id": telegram_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "role": role,
        "is_active": True
    }

    if existing_admin:
        res = (
            supabase.table("admins")
            .update(admin_data)
            .eq("telegram_id", telegram_id)
            .execute()
        )
    else:
        res = (
            supabase.table("admins")
            .insert(admin_data)
            .execute()
        )

    return res.data