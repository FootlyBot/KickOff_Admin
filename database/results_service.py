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


def finish_match(match):


    a = match["score_team_a"]
    b = match["score_team_b"]

    if a > b:
        update_result(match["team_a_id"], win=1)
        update_result(match["team_b_id"], loss=1)

    elif b > a:
        update_result(match["team_b_id"], win=1)
        update_result(match["team_a_id"], loss=1)

    else:
        update_result(match["team_a_id"], draw=1)
        update_result(match["team_b_id"], draw=1)