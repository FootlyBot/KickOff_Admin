from database.supabase_client import supabase

def finish_game(game_id: str):

    # 1. выключаем игру
    supabase.table("games").update({
        "is_running": False,
        "status": "finished"
    }).eq("id", game_id).execute()

    # 2. сбрасываем активные матчи (на всякий случай)
    supabase.table("matches").update({
        "status": "finished"
    }).eq("game_id", game_id)\
      .eq("status", "playing")\
      .execute()