"""Muse Spark FC — Muse Spark 1.2 by Meta. Fast LLM brains with spark-blue identity."""

def build_team(ctx):
    from gauntlet.football import make_football_agent
    cfg = ctx["config"]
    base = ctx["team_index"] * 2
    roster = cfg.get("players") or [{}, {}]
    # football_v2 is the league-tuned prompt; keep latency low with flash-lite
    players = []
    for k in range(2):
        model = roster[k].get("model", cfg["player_model"])
        prompt = roster[k].get("prompt", cfg.get("prompt", "football_v2"))
        players.append(make_football_agent(model, base + k, seed=base + k, prompt=prompt))
    return {"players": players, "manager": None}
