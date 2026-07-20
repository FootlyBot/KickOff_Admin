from database.supabase_client import supabase


def get_team_table(game_id: str):

    # Get teams
    teams_res = (
        supabase.table("teams")
        .select("team_id, team_name")
        .eq("game_id", game_id)
        .execute()
    )

    # Collect team data with stats
    teams_data = []
    
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
        
        teams_data.append({
            "name": team["team_name"],
            "wins": wins,
            "draws": draws,
            "losses": losses
        })

    # Sort by wins (descending), then by draws (descending), then by losses (ascending - fewer is better)
    teams_data.sort(key=lambda x: (x["wins"], x["draws"], -x["losses"]), reverse=True)

    text = "📊 <b>Таблица</b>\n\n<pre>"
    text += "👥 Команда        | В | Н | П\n"
    text += "-----------------------------\n"

    for team in teams_data:
        text += f"{team['name']:<15} | {team['wins']} | {team['draws']} | {team['losses']}\n"

    text += "</pre>"
    return text


def get_winner(game_id: str):
    """Get the winning team based on wins (primary) and draws (secondary)"""
    
    # Get teams
    teams_res = (
        supabase.table("teams")
        .select("team_id, team_name")
        .eq("game_id", game_id)
        .execute()
    )

    # Collect team data with stats
    teams_data = []
    
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
        
        teams_data.append({
            "name": team["team_name"],
            "wins": wins,
            "draws": draws,
            "losses": losses
        })

    if not teams_data:
        return None

    # Sort by wins (descending), then by draws (descending), then by losses (ascending - fewer is better)
    teams_data.sort(key=lambda x: (x["wins"], x["draws"], -x["losses"]), reverse=True)

    # Return the top team
    winner = teams_data[0]
    
    # Check if there's a tie (same wins, draws, AND losses)
    tied_teams = [t for t in teams_data if t["wins"] == winner["wins"] and t["draws"] == winner["draws"] and t["losses"] == winner["losses"]]
    
    if len(tied_teams) > 1:
        # Multiple winners
        return {
            "name": " и ".join([t["name"] for t in tied_teams]),
            "wins": winner["wins"],
            "draws": winner["draws"],
            "losses": winner["losses"],
            "is_tie": True
        }
    
    return {
        "name": winner["name"],
        "wins": winner["wins"],
        "draws": winner["draws"],
        "losses": winner["losses"],
        "is_tie": False
    }