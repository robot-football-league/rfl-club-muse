# RFL Season 2, Round One — Public Data Review

## m1_real_machina_frontier_manus

**Result:** Real Machina 11–0 Manus FC.

**Events:** fall: 21, kick: 202, near_miss: 5, ram: 3, through: 19, wall: 42. **Throughs by robot index:** 0: 5, 1: 13, 2: 1. **Falls by robot index:** 0: 8, 1: 2, 2: 10, 3: 1.

**Goals by team/robot index:** ('A', 0): 4, ('A', 1): 6, ('A', 2): 1. Mean ball x-position was 2.36 m.

### Manus FC diagnosis

Prompt: 43 touches, 10 falls, 2.74 m mean ball distance, and within 1.2 m of the ball for 166 sampled seconds.

Trace: 18 touches, 1 fall, 2.85 m mean ball distance, and within 1.2 m of the ball for 110 sampled seconds.

The ball spent 339 telemetry seconds beyond x=+2.0 in Manus FC's defensive half. At the sampled pre-goal states, both Manus players were routinely several metres behind the ball or separated from each other; the first five snapshots are recorded below for audit.

```json
[
  {
    "goal_t": 23.8,
    "ball": [
      6.87,
      -0.52
    ],
    "robots": [
      [
        6.49,
        1.38
      ],
      [
        7.05,
        0.44
      ],
      [
        4.6,
        4.17
      ],
      [
        0.81,
        1.26
      ]
    ],
    "score_before": [
      0,
      0
    ]
  },
  {
    "goal_t": 158.1,
    "ball": [
      6.96,
      -0.2
    ],
    "robots": [
      [
        6.46,
        -0.72
      ],
      [
        5.85,
        -1.94
      ],
      [
        -1.25,
        -1.49
      ],
      [
        -0.41,
        -0.49
      ]
    ],
    "score_before": [
      1,
      0
    ]
  },
  {
    "goal_t": 177.5,
    "ball": [
      6.58,
      0.62
    ],
    "robots": [
      [
        5.39,
        1.79
      ],
      [
        5.88,
        1.49
      ],
      [
        1.09,
        0.01
      ],
      [
        2.34,
        1.39
      ]
    ],
    "score_before": [
      2,
      0
    ]
  },
  {
    "goal_t": 195.2,
    "ball": [
      6.91,
      0.23
    ],
    "robots": [
      [
        5.17,
        -0.54
      ],
      [
        6.47,
        -0.13
      ],
      [
        0.28,
        0.42
      ],
      [
        1.94,
        0.33
      ]
    ],
    "score_before": [
      3,
      0
    ]
  },
  {
    "goal_t": 217.1,
    "ball": [
      6.97,
      0.4
    ],
    "robots": [
      [
        6.65,
        1.24
      ],
      [
        6.08,
        1.33
      ],
      [
        1.28,
        2.56
      ],
      [
        3.37,
        0.52
      ]
    ],
    "score_before": [
      4,
      0
    ]
  }
]
```

## m2_frontier_fable_synthetic_athletic

**Result:** AFC Fable 6–7 Synthetic Athletic.

**Events:** fall: 21, kick: 212, near_miss: 8, ram: 3, through: 20, wall: 26. **Throughs by robot index:** 0: 5, 1: 7, 2: 4, 3: 4. **Falls by robot index:** 0: 4, 1: 5, 2: 4, 3: 8.

**Goals by team/robot index:** ('A', 0): 3, ('A', 1): 2, ('A', 2): 1, ('B', 0): 1, ('B', 1): 1, ('B', 3): 5. Mean ball x-position was 0.87 m.

## m3_singularity_united_frontier_gemini

**Result:** Singularity United 2–4 Gemini Flash FC.

**Events:** fall: 27, kick: 242, near_miss: 3, ram: 7, through: 11, wall: 51. **Throughs by robot index:** 0: 2, 1: 3, 2: 2, 3: 4. **Falls by robot index:** 0: 11, 1: 7, 2: 3, 3: 6.

**Goals by team/robot index:** ('A', 1): 2, ('B', 2): 1, ('B', 3): 3. Mean ball x-position was 0.79 m.

## m4_frontier_sol_dynamo_datacenter

**Result:** Codex City 4–4 Dynamo Datacenter.

**Events:** fall: 28, kick: 192, near_miss: 6, ram: 2, through: 19, wall: 38. **Throughs by robot index:** 0: 3, 1: 3, 2: 5, 3: 8. **Falls by robot index:** 0: 11, 1: 4, 2: 7, 3: 6.

**Goals by team/robot index:** ('A', 0): 3, ('A', 1): 1, ('B', 1): 1, ('B', 2): 1, ('B', 3): 2. Mean ball x-position was -1.33 m.

## League-wide signals

Across four matches: fall: 97, kick: 848, near_miss: 22, ram: 15, through: 69, wall: 157.

The round was defined by frequent kicks, transition-worthy through events, wall involvement, and falls. The two winning sides that scored seven or more did not preserve a passive shape: their scoring was distributed across both halves and at least one player repeatedly converted high-pressure moments.
