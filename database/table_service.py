from database.supabase_client import supabase


def get_team_table(game_id: str):

    res = (
        supabase.table("teams")
        .select("team_name, team_results(wins,draws,losses)")
        .eq("game_id", game_id)
        .execute()
    )

    text = "📊 <b>Таблица</b>\n\n<pre>"
    text += "Команда        | В | Н | П\n"
    text += "-----------------------------\n"

    for t in res.data or []:

        stats = t.get("team_results", [{}])[0] if isinstance(t.get("team_results"), list) else {}

        text += f"{t['team_name']:<15} | {stats.get('wins',0)} | {stats.get('draws',0)} | {stats.get('losses',0)}\n"

    text += "</pre>"
    return text