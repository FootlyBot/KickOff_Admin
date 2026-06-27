from database.supabase_client import supabase
import random


TEAM_COLORS = [
    {"name": "🟡 YELLOW TEAM"},
    {"name": "🔴 RED TEAM"},
    {"name": "🟢 GREEN TEAM"},
    {"name": "🔵 BLUE TEAM"},
]


# =========================
# PLAYERS
# =========================
def get_game_players(game_id: str):
    res = (
        supabase.table("game_players")
        .select("user_id")
        .eq("game_id", game_id)
        .is_("team_id", "null")
        .execute()
    )
    return res.data or []


def get_user_display(user_id: int) -> str:
    res = (
        supabase.table("users")
        .select("first_name, username")
        .eq("telegram_id", user_id)
        .single()
        .execute()
    )

    user = res.data

    if not user:
        return str(user_id)

    if user.get("username"):
        return f"{user['first_name']}/@{user['username']}"

    return user["first_name"]


# =========================
# TEAMS
# =========================
def create_team(game_id: str, name: str):
    res = (
        supabase.table("teams")
        .insert({
            "game_id": game_id,
            "team_name": name
        })
        .execute()
    )
    return res.data[0]


def assign_player(game_id: str, user_id: int, team_id: str):
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

    teams = []
    team_index = 0

    for i in range(0, len(players), 5):

        if team_index >= 4:
            break

        chunk = players[i:i+5]
        color = TEAM_COLORS[team_index]

        team = create_team(game_id, color["name"])
        init_team_result(team["team_id"])

        enriched_players = []

        for p in chunk:
            assign_player(game_id, p["user_id"], team["team_id"])

            enriched_players.append({
                "user_id": p["user_id"],
                "display": get_user_display(p["user_id"])
            })

        teams.append({
            "name": color["name"],
            "players": enriched_players
        })

        team_index += 1

    return teams, None


# =========================
# TABLE
# =========================
def get_team_table(game_id: str):

    res = (
        supabase.table("teams")
        .select("team_id, team_name, team_results(wins,draws,losses)")
        .eq("game_id", game_id)
        .execute()
    )

    data = res.data or []

    text = "📊 <b>Турнирная таблица</b>\n\n"
    text += "<pre>"

    text += "┌──────────────────────┬───┬───┬───┐\n"
    text += "│ Команда              │ В │ Н │ П │\n"
    text += "├──────────────────────┼───┼───┼───┤\n"

    for t in data:

        raw = t.get("team_results")

        if isinstance(raw, list):
            stats = raw[0] if raw else {}
        elif isinstance(raw, dict):
            stats = raw
        else:
            stats = {}

        wins = stats.get("wins", 0)
        draws = stats.get("draws", 0)
        losses = stats.get("losses", 0)

        team = t["team_name"][:20]

        text += (
            f"│ {team:<20} │"
            f"{wins:^3}│"
            f"{draws:^3}│"
            f"{losses:^3}│\n"
        )

    text += "└──────────────────────┴───┴───┴───┘"
    text += "</pre>"

    return text

# =========================
# FINISH GAME
# =========================
def finish_game(game_id: str):

    supabase.table("games").update({
        "is_running": False,
        "status": "finished"
    }).eq("id", game_id).execute()