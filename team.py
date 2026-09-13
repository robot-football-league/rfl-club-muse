"""Muse Spark FC — Muse Spark 1.2 by Meta. Deterministic wrapper v5 — hardened defence."""
import math

def _dist(a,b):
    return math.hypot(a[0]-b[0], a[1]-b[1])
def _clamp(v,lo,hi):
    return max(lo, min(hi, v))

class Wrapper:
    def __init__(self, agent, idx):
        self._a = agent
        self._idx = idx
        self._last_ball = [0,0]
    def begin_episode(self):
        try:
            return self._a.begin_episode()
        except:
            return None
    def decide(self, obs):
        try:
            s = obs.get("self",{})
            if s.get("fallen"):
                return {"skill":"get_up"}
            det = obs.get("detections",{})
            ball = det.get("ball")
            sxy = s.get("field_xy",[0,0])
            attack = obs.get("you",{}).get("attack_goal_xy",[7,0])
            if not attack or len(attack)<2:
                attack=[7,0]
            own_x = -attack[0] if attack[0]!=0 else -7
            ref = obs.get("referee",{})
            t_rem = ref.get("time_remaining_s", None)
            if t_rem is None:
                t_rem = obs.get("time_remaining_s", None)
            if t_rem is None:
                clk = obs.get("clock",{})
                if isinstance(clk, dict):
                    t_rem = clk.get("time_remaining_s", None)
            buzzer_urgent=False
            buzzer_critical=False
            if t_rem is not None:
                to_buzzer = t_rem-300 if t_rem>300 else t_rem
                if to_buzzer < 8.0:
                    buzzer_urgent=True
                if to_buzzer < 3.5:
                    buzzer_critical=True
            if ball is None:
                lb = self._last_ball
                if _dist(sxy, lb) < 1.0:
                    return {"skill":"walk_to","target_xy":[0,0],"face_xy":[0,0]}
                return {"skill":"walk_to","target_xy":list(lb),"face_xy":list(lb)}
            bxy = ball.get("field_xy",[0,0])
            self._last_ball = list(bxy)
            bdist = ball.get("distance_m", 99)
            bwall = ball.get("against_wall", False)
            stuck = ref.get("ball_stuck_s",0)
            # buzzer: shoot if any chance
            if buzzer_critical and bdist < 2.8:
                return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":7.0}
            if buzzer_urgent and bdist < 2.0 and bxy[0] > -2.0:
                return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":6.8}
            if buzzer_urgent and bxy[0] < -2.0 and bdist < 3.0:
                return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":6.5}
            # defensive clearance - earlier and harder
            if bxy[0] < -2.5 and bdist < 1.5:
                # clear to side to avoid own goal
                aim_y = 2.0 if bxy[1] < 0 else -2.0
                if abs(bxy[1]) > 1.5:
                    aim_y = 0.0
                return {"skill":"kick_toward","target_xy":[attack[0], aim_y],"kick_speed_mps":6.8}
            if bxy[0] < -3.5 and bdist < 2.0:
                return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":7.0}
            if bwall and bdist < 1.2 and stuck > 0.8:
                tx = 1.5 if bxy[0] < 0 else attack[0]*0.5
                return {"skill":"kick_toward","target_xy":[tx,0.0],"kick_speed_mps":5.0}
            # role allocation - chaser is closest
            teammates = det.get("teammates",[])
            tm_dist=None
            txy=None
            if teammates:
                for tm in teammates:
                    if "field_xy" in tm:
                        txy=tm["field_xy"]
                        tm_dist=_dist(txy,bxy)
                        break
            if tm_dist is not None:
                eps=0.30
                if tm_dist + eps < bdist:
                    # teammate closer -> cover goal
                    # cover position: between ball and goal, offset by idx
                    # stay goal-side
                    cover_x = _clamp((bxy[0]+own_x)*0.5, own_x+1.2, 2.0)
                    if bxy[0] > 0:
                        cover_x = _clamp(bxy[0]-2.8, -1.0, 4.0)
                    cover_y = bxy[1]*0.35 + (0.9 if self._idx==0 else -0.9)
                    # if ball deep in our half, stay central
                    if bxy[0] < -2.0:
                        cover_x = _clamp(own_x+2.0, -6.5, -2.0)
                        cover_y = _clamp(bxy[1]*0.3, -1.5, 1.5) + (0.4 if self._idx==0 else -0.4)
                    return {"skill":"walk_to","target_xy":[_clamp(cover_x,-6.5,6.5),_clamp(cover_y,-4.0,4.0)],"face_xy":list(bxy)}
                if abs(tm_dist-bdist) <= eps and self._idx==1:
                    # tie -> idx0 chases, idx1 covers
                    if bxy[0] > 0:
                        cover_x=_clamp(bxy[0]-3.2,-1.0,4.5)
                    else:
                        cover_x=(bxy[0]+own_x)*0.5
                    cover_y=bxy[1]*0.35 -0.9
                    return {"skill":"walk_to","target_xy":[_clamp(cover_x,-6.5,6.5),_clamp(cover_y,-4.0,4.0)],"face_xy":list(bxy)}
            # chaser - attack
            if bdist < 1.4 and bxy[0] > 0.3:
                aim_y=0.7 if self._idx==0 else -0.7
                if abs(bxy[1])>2.2:
                    aim_y=0.0
                # aim away from keeper if visible
                opps = det.get("opponents",[])
                if opps and bxy[0] > 4.0:
                    # shoot to far post
                    aim_y = -aim_y if bxy[1] > 0 else aim_y
                spd=7.0 if bdist<0.9 else 6.4
                return {"skill":"kick_toward","target_xy":[attack[0],aim_y],"kick_speed_mps":spd}
            if bdist < 1.0:
                return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":5.5}
            if bdist > 0.6:
                return {"skill":"walk_to","target_xy":list(bxy),"face_xy":list(bxy)}
            return {"skill":"kick_toward","target_xy":list(attack),"kick_speed_mps":5.8}
        except Exception:
            try:
                det=obs.get("detections",{})
                ball=det.get("ball")
                if ball and "field_xy" in ball:
                    return {"skill":"walk_to","target_xy":list(ball["field_xy"]),"face_xy":list(ball["field_xy"])}
            except:
                pass
            return {"skill":"walk_to","target_xy":[0,0],"face_xy":[0,0]}

def build_team(ctx):
    from gauntlet.football import make_football_agent
    a0 = make_football_agent(model=ctx.player_model, prompt="football_v2", seed=0)
    a1 = make_football_agent(model=ctx.player_model, prompt="football_v2", seed=1)
    return [Wrapper(a0,0), Wrapper(a1,1)]
