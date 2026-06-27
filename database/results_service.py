from database.supabase_client import supabase


def update_result(team_id: str, win=0, draw=0, loss=0):

    existing = (
        supabase.table("team_results")
        .select("*")
        .eq("team_id", team_id)
        .single()
        .execute()
    ).data

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