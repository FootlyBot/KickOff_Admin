from database.supabase_client import supabase
import random


TEAM_COLORS = [
    "🟡 YELLOW TEAM",
    "🔴 RED TEAM",
    "🟢 GREEN TEAM",
    "🔵 BLUE TEAM",
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


def create_team(game_id: str, name: str):
    return (
        supabase.table("teams")
        .insert({"game_id": game_id, "team_name": name})
        .execute()
    ).data[0]


def assign_player(game_id: str, user_id: int, team_id: str):
    supabase.table("game_players")\
        .update({"team_id": team_id})\
        .eq("game_id", game_id)\
        .eq("user_id", user_id)\
        .execute()


def create_teams_for_game(game_id: str):

    players = get_game_players(game_id)

    if not players:
        return None, "Нет игроков"

    random.shuffle(players)

    teams = []
    team_index = 0

    for i in range(0, len(players), 5):

        if team_index >= 4:
            break

        chunk = players[i:i + 5]
        team_name = TEAM_COLORS[team_index]

        team = create_team(game_id, team_name)

        for p in chunk:
            assign_player(game_id, p["user_id"], team["team_id"])

        teams.append({
            "team_id": team["team_id"],
            "name": team_name,
            "players": chunk
        })

        team_index += 1

    return teams, None