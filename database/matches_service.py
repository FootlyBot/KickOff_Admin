from database.supabase_client import supabase
import itertools


def get_teams(game_id: str):
    return (
        supabase.table("teams")
        .select("team_id, team_name")
        .eq("game_id", game_id)
        .execute()
    ).data or []


def create_match(game_id: str, a, b, round_num: int):
    return (
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
    ).data[0]


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

    if side == "B":
        supabase.table("matches").update({
            "score_team_b": match["score_team_b"] + 1
        }).eq("id", match_id).execute()