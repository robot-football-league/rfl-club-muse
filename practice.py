"""Run a 60-second Manus FC mirror practice through the public SDK surface.

Additional command-line arguments are intentionally ignored so the standard
``python practice.py --time 90`` invocation remains harmless under the same
scrutineering rules as match-day code.
"""

import team
from gauntlet.football import run_match


def main():
    home = team.build_team({"team_index": 0, "config": {}})
    away = team.build_team({"team_index": 1, "config": {}})
    result = run_match(home["players"] + away["players"], match_time_s=60.0,
                       mode="paused", obs_mode="sdk", halves=1,
                       team_names=("Manus FC", "Manus FC Mirror"),
                       team_codes=("MNS", "MNS"))
    print(f"final score: {result.score[0]} - {result.score[1]}")
    for index, robot in enumerate(result.robots):
        print(f"robot {index}: touches={robot.touches}, falls={robot.falls}, "
              f"invalid={robot.invalid_actions}, decisions={robot.decisions}")


if __name__ == "__main__":
    main()
