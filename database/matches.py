from database.supabase_client import supabase
import random


TEAM_COLORS = [
    {"name": "🟡 YELLOW TEAM", "short": "yellow"},
    {"name": "🔴 RED TEAM", "short": "red"},
    {"name": "🟢 GREEN TEAM", "short": "green"},
    {"name": "🔵 BLUE TEAM", "short": "blue"},
]


def get_game_players(game_id: str):
    res = (
        supabase.table("game_players")
        .select("user_id")
        .eq("game_id", game_id)
        .is_("team_id", "null")
        .execute()
    )
    return res.data or []


def create_team(game_id: str, team_name: str):
    res = (
        supabase.table("teams")
        .insert({
            "game_id": game_id,
            "team_name": team_name
        })
        .execute()
    )
    return res.data[0]


def assign_player_to_team(game_id: str, user_id: int, team_id: str):
    supabase.table("game_players").update({
        "team_id": team_id
    }).eq("game_id", game_id).eq("user_id", user_id).execute()


def init_team_result(team_id: str):
    supabase.table("team_results").insert({
        "team_id": team_id,
        "wins": 0,
        "draws": 0,
        "losses": 0
    }).execute()


def create_teams_for_game(game_id: str):
    players = get_game_players(game_id)

    if not players:
        return None, "Нет игроков"

    random.shuffle(players)

    teams_data = []
    team_index = 0

    for i in range(0, len(players), 5):

        if team_index >= 4:
            break

        chunk = players[i:i + 5]
        team_color = TEAM_COLORS[team_index]

        team = create_team(game_id, team_color["name"])
        init_team_result(team["team_id"])

        for p in chunk:
            assign_player_to_team(game_id, p["user_id"], team["team_id"])

        teams_data.append({
            "team": team,
            "players": chunk,
            "name": team_color["name"]
        })

        team_index += 1

    return teams_data, None