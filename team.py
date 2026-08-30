"""Manus FC — local, deterministic field control for RFL 0.3.

The model-first experiment created a 27.5% dropped-decision rate in round two.
This controller removes network calls from the live path. Both players build the
same small field model from legal SDK detections, assign a single active chaser
from ball position, and hold a goal-side cover lane behind the ball.
"""


class FieldController:
    """A role-stable player in a shared, deterministic two-robot shape."""

    def __init__(self, role):
        self.role = role
        self.name = "Prompt" if role == "prompt" else "Trace"
        self.last_call_time = None

    def begin_episode(self, log_dir=None):
        self.last_call_time = None

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    def _say(self, reply, obs, text):
        remaining = float(obs.get("time_remaining_s", 0.0))
        if self.last_call_time is None or abs(remaining - self.last_call_time) >= 18.0:
            reply["say"] = text
            self.last_call_time = remaining
        return reply

    @staticmethod
    def _active_role(progress, ball_y):
        """Select exactly one chaser from public field coordinates.

        Progress is positive toward the opponent goal. Trace owns defensive
        territory, Prompt owns attacking territory, and the centre is divided
        by the ball's side of the pitch. Both robots calculate the same answer
        from their own legal ball detection, avoiding a radio-dependent delay.
        """
        if progress < -0.45:
            return "trace"
        if progress > 0.45:
            return "prompt"
        return "prompt" if ball_y >= 0.0 else "trace"

    def _lost_ball(self, goal, attack, obs):
        # Rebuild a compact, goal-side search shape without pretending that a
        # stale detection is current. The two lanes prevent a static overlap.
        scan_y = 2.25 if self.role == "prompt" else -2.25
        anchor = [-attack * 1.35, scan_y]
        return self._say({"skill": "walk_to", "target": anchor}, obs,
                         "Ball lost; restoring the split scan.")

    def decide(self, obs):
        self_state = obs.get("self") or {}
        if self_state.get("fallen"):
            return {"skill": "hold"}

        goal = (obs.get("you") or {}).get("attack_goal_xy") or [7.0, 0.0]
        attack = 1.0 if float(goal[0]) >= 0.0 else -1.0
        ball = (obs.get("detections") or {}).get("ball")
        if not ball or float(ball.get("age_s", 99.0)) > 1.2:
            return self._lost_ball(goal, attack, obs)

        point = ball.get("field_xy") or [0.0, 0.0]
        bx, by = float(point[0]), float(point[1])
        distance = float(ball.get("distance_m", 99.0))
        speed = float(ball.get("speed_mps", 0.0))
        progress = attack * bx
        active = self._active_role(progress, by)
        stuck_for = float((obs.get("referee") or {}).get("ball_stuck_s", 0.0))
        wall_case = bool(ball.get("against_wall"))

        # Every nearby player may clear an immediate final-third emergency;
        # this is a local safety constraint, not a second tactical system.
        if progress < -3.25 and distance < 1.5:
            target = [goal[0], self._clamp(by * 0.30, -1.0, 1.0)]
            return self._say({"skill": "kick_toward", "target": target}, obs,
                             "Emergency clear; rebuild the cover line.")

        if self.role == active:
            if wall_case and stuck_for >= 1.5 and distance < 2.25:
                target = [goal[0], self._clamp(by * 0.58, -1.35, 1.35)]
                return self._say({"skill": "kick_toward", "target": target}, obs,
                                 "Wall release under control.")
            if distance < 1.15:
                target = [goal[0], self._clamp(by * 0.16, -0.85, 0.85)]
                return self._say({"skill": "kick_toward", "target": target}, obs,
                                 "On the ball; hold the cover lane.")
            lead = 0.35 if speed > 0.45 else 0.0
            return {"skill": "go_to_ball", "lead_s": lead}

        # Structural revision: in defence the cover player presses compactly
        # behind the ball instead of holding a deep 2.25 m line. This gives the
        # chaser immediate support and directly targets the failed 3.04 m goal-
        # snapshot proximity prediction, while retaining a one-player outlet
        # shape once the ball crosses midfield.
        cover_distance = 0.95 if progress < -1.0 else 1.45
        lateral_factor = 0.72 if progress < -1.0 else 0.45
        cover = [self._clamp(bx - attack * cover_distance, -5.8, 5.8),
                 self._clamp(by * lateral_factor, -2.6, 2.6)]
        return {"skill": "walk_to", "target": cover}


def build_team(ctx):
    return {"players": [FieldController("prompt"), FieldController("trace")],
            "manager": None}
