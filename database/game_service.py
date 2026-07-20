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

    return {"ok": True}


def cleanup_game(game_id: str):
    """
    Clean up all game-related data after game finishes
    Deletes: team_results, matches, game_players, teams, and the game itself
    """
    
    # Get all teams for this game first
    teams_res = (
        supabase.table("teams")
        .select("team_id")
        .eq("game_id", game_id)
        .execute()
    )
    
    team_ids = [t["team_id"] for t in (teams_res.data or [])]
    
    # 1. Delete team_results for all teams in this game
    if team_ids:
        for team_id in team_ids:
            supabase.table("team_results").delete().eq("team_id", team_id).execute()
    
    # 2. Delete all matches for this game
    supabase.table("matches").delete().eq("game_id", game_id).execute()
    
    # 3. Delete all game_players for this game
    supabase.table("game_players").delete().eq("game_id", game_id).execute()
    
    # 4. Delete all teams for this game
    supabase.table("teams").delete().eq("game_id", game_id).execute()
    
    # 5. Finally, delete the game itself
    supabase.table("games").delete().eq("id", game_id).execute()
    
    return {"ok": True, "message": "Game data cleaned up"}