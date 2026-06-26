from datetime import datetime, timedelta, timezone

from database.supabase_client import supabase


# -------------------------
# CREATE GAME
# -------------------------

def create_game(admin_id: str, field_name: str, address: str, game_date: str, max_players: int):
    res = (
        supabase.table("games")
        .insert({
            "admin_id": admin_id,
            "field_name": field_name,
            "address": address,
            "game_date": game_date,
            "max_players": max_players,
            "current_players": 0,
            "status": "active"
        })
        .execute()
    )
    return res.data


# -------------------------
# GET GAMES (ONLY FUTURE ACTIVE)
# -------------------------

def get_games_by_admin(admin_id: str):
    now = datetime.now(timezone.utc).isoformat()

    res = (
        supabase.table("games")
        .select("*")
        .eq("admin_id", admin_id)
        .eq("status", "active")        # только активные
        .gte("game_date", now)         # только будущие
        .order("game_date", desc=False)
        .execute()
    )

    return res.data


# -------------------------
# CANCEL GAME
# -------------------------

def cancel_game(game_id: str):
    res = (
        supabase.table("games")
        .update({
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", game_id)
        .execute()
    )
    return res.data


# -------------------------
# DELETE OLD CANCELLED GAMES (1+ day old)
# -------------------------

def delete_old_cancelled_games():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    res = (
        supabase.table("games")
        .delete()
        .eq("status", "cancelled")
        .lt("cancelled_at", cutoff)
        .execute()
    )

    return res.data

# -------------------------
# Получение актулаьного количества игроков
# -------------------------


def get_current_players_count(game_id: str) -> int:
    res = (
        supabase.table("game_players")
        .select("id", count="exact")
        .eq("game_id", game_id)
        .execute()
    )
    return res.count or 0

