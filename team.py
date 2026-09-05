"""Muse Spark FC — Muse Spark 1.2 by Meta. Deterministic wrapper + LLM brains."""
import math

def _dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

class Wrapper:
    def __init__(self, agent, idx):
        self._a = agent
        self._idx = idx  # 0 or 1 within team
        self._teammate_idx = 1 - idx
    def begin_episode(self):
        return self._a.begin_episode()
    def decide(self, obs):
        try:
            s = obs.get("self", {})
            if s.get("fallen"):
                return {"skill": "get_up"}
            det = obs.get("detections", {})
            ball = det.get("ball")
            if ball is None:
                return self._a.decide(obs)
            bxy = ball.get("field_xy", [0,0])
            bdist = ball.get("distance_m", 99)
            bwall = ball.get("against_wall", False)
            bage = ball.get("age_s", 0)
            stuck = obs.get("referee", {}).get("ball_stuck_s", 0)
            sxy = s.get("field_xy", [0,0])
            # Emergency defensive clearance: ball in our third and close
            # Own goal is opposite attack_goal
            attack = obs.get("you", {}).get("attack_goal_xy", [7,0])
            own_x = -attack[0] if attack[0] != 0 else -7
            if bxy[0] < -3.5 and bdist < 1.2:
                # kick toward opponent goal
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.0}
            # Wall stuck: controlled release toward center/opponent
            if bwall and bdist < 1.0 and stuck > 1.2:
                tx = 0.0
                ty = 0.0
                # kick toward center slightly forward
                if bxy[0] < 0:
                    tx = 2.0
                else:
                    tx = attack[0] * 0.5
                return {"skill": "kick_toward", "target_xy": [tx, ty], "kick_speed_mps": 4.0}
            # Stale ball recovery: split search
            if bage > 1.8 and bdist > 1.0:
                # offset left/right by player index to avoid duplication
                off = 1.5 if self._idx == 0 else -1.5
                return {"skill": "walk_to", "target_xy": [bxy[0], bxy[1]+off], "face_xy": list(bxy)}
            # Single-chaser role allocation
            teammates = det.get("teammates", [])
            # teammates list may contain dicts with field_xy and distance_m
            # Find teammate distance to ball if available
            tm_dist = None
            if teammates:
                # assume first teammate is the other player
                for tm in teammates:
                    if "distance_m" in tm:
                        # distance to ball approx: dist(teammate, ball)
                        txy = tm.get("field_xy", sxy)
                        tm_dist = _dist(txy, bxy)
                        break
                    elif "field_xy" in tm:
                        txy = tm["field_xy"]
                        tm_dist = _dist(txy, bxy)
                        break
            if tm_dist is not None:
                # tie-break: idx 0 chases central balls
                eps = 0.15
                if tm_dist + eps < bdist:
                    # teammate is clearly closer -> cover
                    # cover position: between ball and own goal, offset laterally
                    cover_x = (bxy[0] + own_x) * 0.5
                    cover_y = bxy[1] * 0.5 + (1.0 if self._idx==0 else -1.0)
                    # clamp inside field
                    cover_x = max(min(cover_x, 6.5), -6.5)
                    cover_y = max(min(cover_y, 4.0), -4.0)
                    return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
                if abs(tm_dist - bdist) <= eps:
                    # central tie: idx 0 chases
                    if self._idx == 1:
                        cover_x = (bxy[0] + own_x) * 0.5
                        cover_y = bxy[1] * 0.5 - 1.0
                        return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
            # otherwise delegate to LLM for nuanced play
            return self._a.decide(obs)
        except Exception:
            try:
                return self._a.decide(obs)
            except Exception:
                return {"skill": "walk_to", "target_xy": [0,0]}

def build_team(ctx):
    from gauntlet.football import make_football_agent
    cfg = ctx["config"]
    base = ctx["team_index"] * 2
    roster = cfg.get("players") or [{}, {}]
    players = []
    for k in range(2):
        model = roster[k].get("model", cfg["player_model"])
        prompt = roster[k].get("prompt", cfg.get("prompt", "football_v2"))
        raw = make_football_agent(model, base + k, seed=base + k, prompt=prompt)
        players.append(Wrapper(raw, k))
    return {"players": players, "manager": None}
