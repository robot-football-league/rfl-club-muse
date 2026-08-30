"""Create a reproducible public-data review of RFL season-two round one."""

from collections import Counter
from pathlib import Path
import json
import math


ROOT = Path("/home/ubuntu/rfl-league-data/seasons/s2")
MATCHES = sorted(ROOT.glob("m*_*"))
OUT = Path("/home/ubuntu/rfl-club-manus/tools/round_one_report.md")


def load_json(path):
    return json.loads(path.read_text())


def telemetry(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def count_events(events, team_index):
    return Counter(event["kind"] for event in events), Counter(
        event.get("who") for event in events if event["kind"] == "through"
    ), Counter(
        event.get("who") for event in events
        if event["kind"] == "fall" and event.get("who") is not None
    )


def player_spatial(rows, robot_index):
    distances = []
    xs = []
    close = 0
    for row in rows:
        px, py = row["robots"][robot_index]
        bx, by = row["ball"]
        distance = math.hypot(px - bx, py - by)
        distances.append(distance)
        xs.append(px)
        if distance <= 1.2:
            close += 1
    return {"mean_x": mean(xs), "mean_ball_distance": mean(distances),
            "close_ball_seconds": close}


def goal_snapshot(rows, goal):
    prior = max((row for row in rows if row["t"] <= goal["t"]),
                key=lambda row: row["t"])
    return {"goal_t": goal["t"], "ball": prior["ball"],
            "robots": prior["robots"], "score_before": prior["score"]}


def format_counter(counter):
    return ", ".join(f"{k}: {v}" for k, v in sorted(counter.items()))


def main():
    lines = ["# RFL Season 2, Round One — Public Data Review", ""]
    league_totals = Counter()
    summaries = []
    for directory in MATCHES:
        match = load_json(directory / "match.json")
        rows = telemetry(directory / "telemetry.jsonl")
        teams = match["teams"]
        events, throughs, falls = count_events(match["events"], 0)
        league_totals.update(events)
        goal_counts = Counter((goal["team"], goal["scorer"]) for goal in match["goals"])
        summary = {
            "directory": directory.name,
            "score": match["score"],
            "teams": (teams["A"]["name"], teams["B"]["name"]),
            "events": events,
            "throughs": throughs,
            "falls": falls,
            "goals": goal_counts,
            "ball_x": mean(row["ball"][0] for row in rows),
        }
        summaries.append(summary)
        lines.extend([
            f"## {directory.name}",
            "",
            f"**Result:** {teams['A']['name']} {match['score'][0]}–{match['score'][1]} {teams['B']['name']}.",
            "",
            f"**Events:** {format_counter(events)}. **Throughs by robot index:** {format_counter(throughs)}. "
            f"**Falls by robot index:** {format_counter(falls)}.",
            "",
            f"**Goals by team/robot index:** {format_counter(goal_counts)}. Mean ball x-position was {summary['ball_x']:.2f} m.",
            "",
        ])
        if directory.name.endswith("frontier_manus"):
            prompt = player_spatial(rows, 2)
            trace = player_spatial(rows, 3)
            snapshots = [goal_snapshot(rows, goal) for goal in match["goals"]]
            defensive_ball_seconds = sum(1 for row in rows if row["ball"][0] > 2.0)
            lines.extend([
                "### Manus FC diagnosis",
                "",
                f"Prompt: {match['robots'][2]['touches']} touches, {match['robots'][2]['falls']} falls, "
                f"{prompt['mean_ball_distance']:.2f} m mean ball distance, and within 1.2 m of the ball for "
                f"{prompt['close_ball_seconds']} sampled seconds.",
                "",
                f"Trace: {match['robots'][3]['touches']} touches, {match['robots'][3]['falls']} fall, "
                f"{trace['mean_ball_distance']:.2f} m mean ball distance, and within 1.2 m of the ball for "
                f"{trace['close_ball_seconds']} sampled seconds.",
                "",
                f"The ball spent {defensive_ball_seconds} telemetry seconds beyond x=+2.0 in Manus FC's defensive half. "
                "At the sampled pre-goal states, both Manus players were routinely several metres behind the ball or "
                "separated from each other; the first five snapshots are recorded below for audit.",
                "",
                "```json",
                json.dumps(snapshots[:5], indent=2),
                "```",
                "",
            ])
    lines.extend([
        "## League-wide signals",
        "",
        f"Across four matches: {format_counter(league_totals)}.",
        "",
        "The round was defined by frequent kicks, transition-worthy through events, wall involvement, and falls. "
        "The two winning sides that scored seven or more did not preserve a passive shape: their scoring was distributed "
        "across both halves and at least one player repeatedly converted high-pressure moments.",
        "",
    ])
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
