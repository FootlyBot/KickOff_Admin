from database.supabase_client import supabase


def get_team_table(game_id: str):

    # Get teams
    teams_res = (
        supabase.table("teams")
        .select("team_id, team_name")
        .eq("game_id", game_id)
        .execute()
    )

    text = "📊 <b>Таблица</b>\n\n<pre>"
    text += "Команда        | В | Н | П\n"
    text += "-----------------------------\n"

    for team in teams_res.data or []:
        # Get results for this team
        try:
            results_res = (
                supabase.table("team_results")
                .select("wins, draws, losses")
                .eq("team_id", team["team_id"])
                .maybe_single()
                .execute()
            )
            stats = results_res.data if results_res and results_res.data else {}
        except Exception:
            stats = {}

        wins = stats.get("wins", 0)
        draws = stats.get("draws", 0)
        losses = stats.get("losses", 0)

        text += f"{team['team_name']:<15} | {wins} | {draws} | {losses}\n"

    text += "</pre>"
    return text