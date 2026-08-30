"""Exercise Manus FC's deterministic single-chaser field controller."""

import team


def observation(position, ball, remaining=60.0, stuck=0.0):
    return {
        "time_remaining_s": remaining,
        "self": {"field_xy": position, "fallen": False},
        "you": {"attack_goal_xy": [7.0, 0.0]},
        "detections": {"ball": ball, "teammates": [], "opponents": []},
        "referee": {"ball_stuck_s": stuck},
    }


def ball(x, y, distance, age=0.0, wall=False, speed=0.0):
    return {"field_xy": [x, y], "distance_m": distance, "age_s": age,
            "speed_mps": speed, "against_wall": wall}


def expect(label, player, obs, expected):
    reply = player.decide(obs)
    actual = reply.get("skill")
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")
    print(f"PASS: {label} -> {actual}")


def main():
    prompt, trace = team.build_team({"team_index": 0, "config": {}})["players"]
    prompt.begin_episode()
    trace.begin_episode()

    expect("Prompt owns a ball in the attacking half", prompt,
           observation([0.0, 0.0], ball(2.0, 0.8, 2.2)), "go_to_ball")
    expect("Trace covers rather than duplicating the attacking chase", trace,
           observation([0.0, -1.0], ball(2.0, 0.8, 2.2)), "walk_to")
    expect("Trace owns a ball in the defensive half", trace,
           observation([0.0, -1.0], ball(-2.0, -0.8, 2.2)), "go_to_ball")
    expect("Prompt covers rather than duplicating the defensive chase", prompt,
           observation([0.0, 1.0], ball(-2.0, -0.8, 2.2)), "walk_to")
    expect("Central positive-lane ball selects Prompt as the tiebreak chaser", prompt,
           observation([0.0, 0.0], ball(0.0, 0.3, 2.0)), "go_to_ball")
    expect("A nearby wall case uses a controlled release", prompt,
           observation([2.5, 3.8], ball(2.8, 4.0, 0.5, wall=True), stuck=2.0),
           "kick_toward")
    expect("Any nearby final-third ball receives an emergency clearance", prompt,
           observation([-4.0, 0.1], ball(-4.2, 0.2, 0.4)), "kick_toward")
    expect("A stale ball triggers local split-search recovery", trace,
           observation([0.0, 0.0], ball(0.0, 0.0, 1.0, age=2.0)), "walk_to")


if __name__ == "__main__":
    main()
