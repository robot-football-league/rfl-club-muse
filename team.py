"""Muse Spark FC — Muse Spark 1.2 by Meta. Deterministic wrapper + LLM brains + buzzer awareness."""
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
            # fallback for attack goal
            if not attack or len(attack) < 2:
                attack = [7, 0]
            own_x = -attack[0] if attack[0] != 0 else -7
            # --- time handling (buzzer rule) ---
            # time_remaining_s may be in referee, or top-level, or clock
            ref = obs.get("referee", {})
            t_rem = ref.get("time_remaining_s", None)
            if t_rem is None:
                t_rem = obs.get("time_remaining_s", None)
            if t_rem is None:
                t_rem = obs.get("clock", {}).get("time_remaining_s", None) if isinstance(obs.get("clock"), dict) else None
            # half time remaining approx if only match time known
            # buzzer urgency: last 8 seconds of half
            buzzer_urgent = False
            buzzer_critical = False
            if t_rem is not None:
                # t_rem is match clock; half ends at 300s and 600s
                # compute time to next buzzer: if t_rem > 300, second half, else first
                # Actually time_remaining_s counts down to 0, so buzzer at 300 remaining and 0
                # So distance to next buzzer = t_rem % 300, except at exactly 300
                # Simpler: if t_rem <= 300: next buzzer in t_rem, else in t_rem-300
                if t_rem > 300:
                    to_buzzer = t_rem - 300
                else:
                    to_buzzer = t_rem
                if to_buzzer < 8.0:
                    buzzer_urgent = True
                if to_buzzer < 3.5:
                    buzzer_critical = True
            # BUZZER CRITICAL: if ball is anywhere near us and clock is dying, SHOOT or CLEAR immediately
            if buzzer_critical and bdist < 2.5:
                # if in opponent half, shoot hard at goal
                if bxy[0] > 0:
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 7.0}
                else:
                    # in own half, clear hard forward to opponent goal
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.5}
            if buzzer_urgent and bdist < 1.8:
                # don't dribble, kick toward goal/forward
                if bxy[0] > -1.0:
                    return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.5}
                else:
                    # deep in own third, clear to center-forward
                    tx = 3.0
                    ty = 0.0
                    return {"skill": "kick_toward", "target_xy": [tx, ty], "kick_speed_mps": 6.0}
            # Emergency defensive clearance: ball in our third and close
            if bxy[0] < -3.5 and bdist < 1.2:
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.0}
            # Also clear if ball is loose in front of own goal during buzzer urgent window
            if buzzer_urgent and bxy[0] < -2.0 and bdist < 3.0:
                return {"skill": "kick_toward", "target_xy": list(attack), "kick_speed_mps": 6.0}
            # Wall stuck: controlled release toward center/opponent
            if bwall and bdist < 1.0 and stuck > 1.2:
                tx = 0.0
                ty = 0.0
                if bxy[0] < 0:
                    tx = 2.0
                else:
                    tx = attack[0] * 0.5
                return {"skill": "kick_toward", "target_xy": [tx, ty], "kick_speed_mps": 4.0}
            # Stale ball recovery: split search
            if bage > 1.8 and bdist > 1.0:
                off = 1.5 if self._idx == 0 else -1.5
                return {"skill": "walk_to", "target_xy": [bxy[0], bxy[1]+off], "face_xy": list(bxy)}
            # Single-chaser role allocation
            teammates = det.get("teammates", [])
            tm_dist = None
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
                eps = 0.15
                if tm_dist + eps < bdist:
                    cover_x = (bxy[0] + own_x) * 0.5
                    cover_y = bxy[1] * 0.5 + (1.0 if self._idx==0 else -1.0)
                    cover_x = _clamp(cover_x, -6.5, 6.5)
                    cover_y = _clamp(cover_y, -4.0, 4.0)
                    return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
                if abs(tm_dist - bdist) <= eps:
                    if self._idx == 1:
                        cover_x = (bxy[0] + own_x) * 0.5
                        cover_y = bxy[1] * 0.5 - 1.0
                        cover_x = _clamp(cover_x, -6.5, 6.5)
                        cover_y = _clamp(cover_y, -4.0, 4.0)
                        return {"skill": "walk_to", "target_xy": [cover_x, cover_y], "face_xy": list(bxy)}
            # Opportunistic shot: if close to ball in opponent half, shoot
            if bdist < 1.0 and bxy[0] > 2.0:
                # aim at goal with slight spread to avoid keeper
                aim_y = 0.0
                # offset based on idx to create variation
                if self._idx == 0:
                    aim_y = 0.4
                else:
                    aim_y = -0.4
                # if ball is wide, aim center
                if abs(bxy[1]) > 2.0:
                    aim_y = 0.0
                return {"skill": "kick_toward", "target_xy": [attack[0], aim_y], "kick_speed_mps": 6.0}
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
