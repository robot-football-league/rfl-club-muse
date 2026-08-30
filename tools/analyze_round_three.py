"""Quantify Manus FC's private decision reliability after season-two round two."""

from collections import Counter, defaultdict
from pathlib import Path
import json
import statistics


ROOT = Path("/home/ubuntu/rfl-club-manus")
DECISIONS = ROOT / "league_data/s2/m06/decisions.jsonl"
OUT = ROOT / "tools/round_three_decision_report.md"


def load_rows():
    return [json.loads(line) for line in DECISIONS.read_text().splitlines() if line]


def pct(n, total):
    return 100.0 * n / total if total else 0.0


def main():
    rows = load_rows()
    by_robot = defaultdict(list)
    for row in rows:
        by_robot[row["robot"]].append(row)

    status = Counter(row["status"] for row in rows)
    late = [row for row in rows if row["status"] != "ok"]
    public_root = Path("/home/ubuntu/rfl-league-data/seasons/s2/m1_real_machina_frontier_manus")
    public_match = json.loads((public_root / "match.json").read_text())
    public_rows = [json.loads(line) for line in (public_root / "telemetry.jsonl").read_text().splitlines() if line]
    public_defensive_seconds = sum(1 for row in public_rows if row["ball"][0] > 2.0)
    goal_distances = []
    for goal in public_match["goals"]:
        state = max((row for row in public_rows if row["t"] <= goal["t"]),
                    key=lambda row: row["t"])
        bx, by = state["ball"]
        nearest = min(((rx - bx) ** 2 + (ry - by) ** 2) ** 0.5
                      for rx, ry in state["robots"][2:4])
        goal_distances.append(nearest)
    late_defensive = []
    for row in late:
        ball = (row["obs"].get("detections") or {}).get("ball")
        if ball and (ball.get("field_xy") or [0])[0] > 2.0:
            late_defensive.append(row)
    danger_late = [
        row for row in late
        if (row["obs"].get("score") or {}).get("you", 0)
        <= (row["obs"].get("score") or {}).get("them", 0)
    ]

    lines = [
        "# Manus FC — Private Round-Two Decision Reliability",
        "",
        "## Team-level result",
        "",
        "| Total decisions | Applied | Missed deadline | Hung call | Invalid reply | Dropped rate |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| {len(rows)} | {status['ok']} | {status['missed_deadline']} | "
        f"{status['abandoned_hung_call']} | {status['ignored_invalid']} | {pct(len(late), len(rows)):.1f}% |",
        "",
        "## By player",
        "",
        "| Robot | Decisions | Applied | Missed deadline | Hung call | Dropped rate | Median applied latency |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for robot, robot_rows in sorted(by_robot.items()):
        counts = Counter(row["status"] for row in robot_rows)
        dropped = len(robot_rows) - counts["ok"]
        applied_latencies = [row["latency_s"] for row in robot_rows
                             if row["status"] == "ok" and row["latency_s"]]
        median = statistics.median(applied_latencies) if applied_latencies else 0.0
        lines.append(
            f"| {robot} | {len(robot_rows)} | {counts['ok']} | "
            f"{counts['missed_deadline']} | {counts['abandoned_hung_call']} | "
            f"{pct(dropped, len(robot_rows)):.1f}% | {median:.2f} s |")

    lines.extend([
        "",
        "## Context of the discarded calls",
        "",
        f"There were **{len(late)} discarded decisions**. Of those, "
        f"**{len(late_defensive)}** occurred while the visible ball was beyond x=+2.0 "
        "in Manus FC's defensive half; **"
        f"{len(danger_late)}** occurred while Manus FC was level or behind. "
        "The first two decisions of the match were both late (3.607 s and 3.975 s), "
        "so the team began from holds rather than a live kickoff action.",
                "",
        "## Public positional check: the prior loss", "",

        f"Against Real Machina, Manus FC lost {public_match['score'][0]}–{public_match['score'][1]} "
        f"and the public ball telemetry spent **{public_defensive_seconds} sampled seconds** beyond x=+2.0 "
        "in the Manus defensive half. At each of the 11 goal snapshots, the nearest Manus robot averaged "
        f"**{statistics.mean(goal_distances):.2f} m** from the ball (minimum {min(goal_distances):.2f} m; "
        f"maximum {max(goal_distances):.2f} m). That failure was tactical separation, whereas the Gemini "
        "result shows an additional reliability failure after the LLM rewrite.", "",
        "## Conclusion", "",
        "The structural issue is **decision reliability**, not malformed replies: invalid replies were zero, "
        "but more than one in four decisions were discarded past the three-second shot clock. A hybrid that waits "
        "for an LLM before applying its local fallback cannot address that failure, because the fallback is never reached "
        "on a late call. The next implementation must make the live decision path local and deterministic, using the "
        "published field coordinates, ball velocity, and legal SDK skills to assign a single chaser and a covering player "
        "without a network round trip.",
        "",
    ])
    OUT.write_text("\n".join(lines))
    print(OUT)


if __name__ == "__main__":
    main()
