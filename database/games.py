from datetime import datetime, timedelta

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
# GET GAMES
# -------------------------

def get_games_by_admin(admin_id: str):
    res = (
        supabase.table("games")
        .select("*")
        .eq("admin_id", admin_id)
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
            "cancelled_at": datetime.utcnow().isoformat()
        })
        .eq("id", game_id)
        .execute()
    )
    return res.data


# -------------------------
# DELETE OLD CANCELLED GAMES
# -------------------------

def delete_old_cancelled_games():
    cutoff = (datetime.utcnow() - timedelta(days=3)).isoformat()

    res = (
        supabase.table("games")
        .delete()
        .eq("status", "cancelled")
        .lt("cancelled_at", cutoff)
        .execute()
    )

    return res.data