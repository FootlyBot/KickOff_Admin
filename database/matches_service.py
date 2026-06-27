from database.supabase_client import supabase
import itertools


# =========================
# TEAMS
# =========================
def get_teams(game_id: str):
    return (
        supabase.table("teams")
        .select("team_id, team_name")
        .eq("game_id", game_id)
        .execute()
    ).data or []


def get_team_name(team_id: str):
    res = (
        supabase.table("teams")
        .select("team_name")
        .eq("team_id", team_id)
        .single()
        .execute()
    )
    return res.data["team_name"] if res.data else "UNKNOWN"


# =========================
# MATCH CORE
# =========================
def create_match(game_id: str, a, b, round_num: int):

    res = (
        supabase.table("matches")
        .insert({
            "game_id": game_id,
            "team_a_id": a,
            "team_b_id": b,
            "score_team_a": 0,
            "score_team_b": 0,
            "status": "playing",
            "round": round_num
        })
        .execute()
    )

    return res.data[0]


def get_active_match(game_id: str):
    res = (
        supabase.table("matches")
        .select("*")
        .eq("game_id", game_id)
        .eq("status", "playing")
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


# =========================
# ROUND ROBIN
# =========================
def generate_round_robin(teams):
    return list(itertools.combinations(teams, 2))


def get_next_match(game_id: str):

    active = get_active_match(game_id)
    if active:
        return active

    teams = get_teams(game_id)
    if len(teams) < 2:
        return None

    pairs = generate_round_robin(teams)

    played_res = (
        supabase.table("matches")
        .select("team_a_id, team_b_id")
        .eq("game_id", game_id)
        .execute()
    )

    played = set()
    for m in played_res.data or []:
        played.add((m["team_a_id"], m["team_b_id"]))
        played.add((m["team_b_id"], m["team_a_id"]))

    round_num = 1

    for a, b in pairs:
        if (a["team_id"], b["team_id"]) not in played:
            return create_match(game_id, a["team_id"], b["team_id"], round_num)

        round_num += 1

    return None


# =========================
# GOALS
# =========================
def add_goal(match_id: str, side: str):

    match = (
        supabase.table("matches")
        .select("*")
        .eq("id", match_id)
        .single()
        .execute()
    ).data

    if not match:
        return

    if side == "A":
        supabase.table("matches").update({
            "score_team_a": match["score_team_a"] + 1
        }).eq("id", match_id).execute()

    elif side == "B":
        supabase.table("matches").update({
            "score_team_b": match["score_team_b"] + 1
        }).eq("id", match_id).execute()


# =========================
# FINISH MATCH
# =========================
def finish_match(match_id: str):

    match = (
        supabase.table("matches")
        .select("*")
        .eq("id", match_id)
        .single()
        .execute()
    ).data

    if not match:
        return

    a = match["score_team_a"]
    b = match["score_team_b"]

    team_a = match["team_a_id"]
    team_b = match["team_b_id"]

    if a > b:
        update_result(team_a, win=1)
        update_result(team_b, loss=1)

    elif b > a:
        update_result(team_b, win=1)
        update_result(team_a, loss=1)

    else:
        update_result(team_a, draw=1)
        update_result(team_b, draw=1)

    supabase.table("matches").update({
        "status": "finished"
    }).eq("id", match_id).execute()


def update_result(team_id: str, win=0, draw=0, loss=0):

    res = (
        supabase.table("team_results")
        .select("*")
        .eq("team_id", team_id)
        .maybe_single()
        .execute()
    )

    existing = res.data

    if not existing:
        supabase.table("team_results").insert({
            "team_id": team_id,
            "wins": win,
            "draws": draw,
            "losses": loss
        }).execute()
        return

    supabase.table("team_results").update({
        "wins": existing["wins"] + win,
        "draws": existing["draws"] + draw,
        "losses": existing["losses"] + loss
    }).eq("team_id", team_id).execute()