"""Muse Spark FC — Muse Spark 1.2 by Meta. Deterministic wrapper + LLM brains + buzzer awareness v3 — latency cut."""
import math

def _dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

class Wrapper:
    def __init__(self, agent, idx):
        self._a = agent
        self._idx = idx
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
            attack = obs.get("you", {}).get("attack_goal_xy", [7,0])
            if not attack or len(attack) < 2:
                attack = [7, 0]
            own_x = -attack[0] if attack[0] != 0 else -7
            ref = obs.get("referee", {})
            t_rem = ref.get("time_remaining_s", None)
            if t_rem is None:
                t_rem = obs.get("time_remaining_s", None)
            if t_rem is None:
                t_rem = obs.get("clock", {}).get("time_remaining_s", None) if isinstance(obs.get("clock"), dict) else None
            buzzer_urgent = False
            buzzer_critical = False
            if t_rem is not None:
                if t_rem > 300:
                    to_buzzer = t_rem - 300
                else:
                    to_buzzer = t_rem
                if to_buzzer < 8.0:
                    buzzer_urgent = True
                if to_buzzer < 3.5:
                    buzzer_critical = True
            if buzzer_critical and bdist < 2.5:
                if bxy[0] > 0:
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 7.0}
                else:
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.5}
            if buzzer_urgent and bdist < 1.8:
                if bxy[0] > -1.0:
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.5}
                else:
                    return {"skill": "kick_toward", "target_xy": [3.0, 0.0], "kick_speed_mps": 6.0}
            if bxy[0] < -3.5 and bdist < 1.2:
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.5}
            if buzzer_urgent and bxy[0] < -2.0 and bdist < 3.0:
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.0}
            if bwall and bdist < 1.0 and stuck > 1.0:
                tx = 2.0 if bxy[0] < 0 else attack[0] * 0.5
                return {"skill": "kick_toward", "target_xy": [tx, 0.0], "kick_speed_mps": 4.5}
            if bage > 1.8 and bdist > 1.2:
                off = 1.5 if self._idx == 0 else -1.5
                return {"skill": "walk_to", "target_xy": [bxy[0], _clamp(bxy[1]+off, -4.0, 4.0)], "face_xy": list(bxy)}
            teammates = det.get("teammates", [])
            tm_dist = None
            txy = None
            if teammates:
                for tm in teammates:
                    if "distance_m" in tm:
                        txy = tm.get("field_xy", sxy)
                        tm_dist = _dist(txy, bxy)
                        break
                    elif "field_xy" in tm:
                        txy = tm["field_xy"]
                        tm_dist = _dist(txy, bxy)
                        break
            if tm_dist is not None:
                eps = 0.25
                if tm_dist + eps < bdist:
                    if bxy[0] > 1.0:
                        cover_x = _clamp(bxy[0] - 2.5, -1.0, 5.0)
                    else:
                        cover_x = (bxy[0] + own_x) * 0.5
                    cover_y = bxy[1] * 0.4 + (0.8 if self._idx==0 else -0.8)
                    if bxy[0] < -2.0 and abs(bxy[1]) < 1.5:
                        cover_x = _clamp(own_x + 1.8, -6.5, -2.0)
                        cover_y = _clamp(bxy[1]*0.3, -1.2, 1.2) + (0.5 if self._idx==0 else -0.5)
                    cover_x = _clamp(cover_x, -6.5, 6.5)
                    cover_y = _clamp(cover_y, -4.0, 4.0)
                    return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
                if abs(tm_dist - bdist) <= eps:
                    if self._idx == 1:
                        if bxy[0] > 1.0:
                            cover_x = _clamp(bxy[0] - 3.0, -1.0, 4.5)
                        else:
                            cover_x = (bxy[0] + own_x) * 0.5
                        cover_y = bxy[1] * 0.4 - 0.9
                        cover_x = _clamp(cover_x, -6.5, 6.5)
                        cover_y = _clamp(cover_y, -4.0, 4.0)
                        return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
            # Chaser: deterministic to cut LLM latency
            if bdist < 1.4 and bxy[0] > 0.5:
                aim_y = 0.7 if self._idx == 0 else -0.7
                if abs(bxy[1]) > 2.2:
                    aim_y = 0.0
                spd = 7.0 if bdist < 0.9 else 6.2
                return {"skill": "kick_toward", "target_xy": [attack[0], aim_y], "kick_speed_mps": spd}
            if bdist < 1.0:
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 5.0}
            if bdist > 0.6:
                return {"skill": "walk_to", "target_xy": list(bxy), "face_xy": list(bxy)}
            # very close but not in shot window: dribble forward
            return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 4.0}
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
