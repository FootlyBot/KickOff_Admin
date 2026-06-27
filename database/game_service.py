from database.supabase_client import supabase


def finish_game(game_id: str):

    # =========================
    # 1. проверяем что игра существует и активна
    # =========================
    game = (
        supabase.table("games")
        .select("id, status")
        .eq("id", game_id)
        .single()
        .execute()
    ).data

    if not game:
        return {"error": "GAME_NOT_FOUND"}

    if game.get("status") == "finished":
        return {"ok": True, "message": "Already finished"}

    # =========================
    # 2. выключаем игру
    # =========================
    supabase.table("games").update({
        "is_running": False,
        "status": "finished"
    }).eq("id", game_id).execute()

    # =========================
    # 3. закрываем все активные матчи
    # =========================
    supabase.table("matches").update({
        "status": "finished"
    }).eq("game_id", game_id)\
      .eq("status", "playing")\
      .execute()

    # =========================
    # 4. (опционально) логика финализации
    # =========================
    # сюда потом можно добавить:
    # - итоговую таблицу
    # - MVP игрока
    # - статистику голов

    return {"ok": True}