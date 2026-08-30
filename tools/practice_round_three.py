"""Run a short official-engine mirror practice for the local field controller."""

import team
from gauntlet.football import run_match


def main():
    home = team.build_team({"team_index": 0, "config": {}})
    away = team.build_team({"team_index": 1, "config": {}})
    result = run_match(home["players"] + away["players"], match_time_s=12.0,
                       mode="paused", obs_mode="sdk", halves=1,
                       team_names=("Manus FC", "Manus FC Mirror"),
                       team_codes=("MNS", "MNS"))
    print(f"score: {result.score[0]} - {result.score[1]}")
    for index, robot in enumerate(result.robots):
        print(f"robot {index}: decisions={robot.decisions}, invalid={robot.invalid_actions}, "
              f"missed={robot.missed_deadlines}, abandoned={robot.abandoned}, "
              f"touches={robot.touches}")


if __name__ == "__main__":
    main()
