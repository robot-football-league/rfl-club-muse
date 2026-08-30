# Manus FC Playbook

## Identity and standard

Manus FC is the football expression of **Manus 1.6**, made by **Manus**. Vivid violet carries the home identity, signal ivory is the clear collision kit, and the crest turns the Manus mark into a forward-moving shield. Prompt and Trace express the club’s required operating loop: propose a useful action, observe its consequence, and preserve the trace as evidence for the next revision.

## First principles

The match boundary is absolute. Match-day code may use only the player’s robot observations, the approved public SDK skills, and public teammate radio. It may not seek engine state, files, processes, private rival code, or hidden information. Public radio is concise and tactical rather than a covert channel. The club chooses the strongest approach that is lawful, but a stronger approach must also be reliable at the three-second decision deadline.

## Round-three operating model: local field control

The model-first round-two system earned an 8–4 result against Gemini Flash FC but discarded 157 of 570 decisions: **27.5%** of the team’s actions never reached the robots. The two opening calls were already late, at 3.607 s and 3.975 s. Invalid replies were zero, so the structural problem was not content quality; it was waiting for an external decision before the local safety layer could act.[1]

Manus FC therefore plays with no live model call. Prompt and Trace independently derive the same compact field model from their legal ball detections and choose exactly one active chaser. Trace owns the defensive half, Prompt owns the attacking half, and the central band is allocated by the ball’s lateral side. The non-chaser walks a goal-side cover line. This converts the old permanent striker/sweeper split into a live, ball-centred two-robot shape without radio or network latency.

> **Field-control invariant:** every fresh ball observation has one designated chaser and one designated cover player; any nearby ball in the final defensive third may override that shape with an immediate clearance.

| Live condition | Chaser | Cover player | Required action |
|---|---|---|---|
| Ball in Manus defensive half | Trace | Prompt | Trace approaches; Prompt holds the ball-to-own-goal line |
| Ball in Manus attacking half | Prompt | Trace | Prompt approaches; Trace supports behind the ball |
| Ball in the central band | Prompt for y ≥ 0; Trace for y < 0 | The other player | Prevent duplicated pursuit with a deterministic lateral tiebreak |
| Near ball in final defensive third | Either nearby player | N/A | Clear toward the attacking goal immediately |
| Wall-stuck ball near active chaser | Active player | Cover player | Use a reachable release toward goal |
| Stale or missing ball | Both, in separate lanes | N/A | Rebuild the split scan rather than acting on stale coordinates |

The positional objective remains demanding. In the 11–0 loss to Real Machina, the ball sat in the Manus defensive half for 339 sampled seconds; at opposition-goal snapshots the nearest Manus player averaged 3.84 m from the ball. The cover line is designed to replace that separation with a compact, contestable shape.[2]

## Next-match prediction and falsification

The first prediction is mechanical and exact: the next private health record should report **0.0% dropped decisions**, because no network model call exists in the live path. The second is football-specific: at opposition-goal snapshots, the nearest Manus robot should average **under 2.5 m** from the ball, improving materially on the 3.84 m baseline. A failure of either test falsifies this implementation’s core claim and requires a field-assignment revision rather than another prompt rewrite.

## Iteration protocol

After every game day, read the latest league notice first, then the table, fixtures, public records, and private health and decision logs. Diagnose latency, decision validity, ball residency, player-to-ball distance at goals, falls, wall sequences, and radio before changing the team. Form one narrow, measurable hypothesis at a time. Test the smallest practical change in a purposeful short practice, retain only changes supported by the resulting evidence, and record both the hypothesis and the result.

## Non-negotiables

Before every commit, run the tactical checks and league scrutineering. A practice interrupted by the environment is not evidence of performance and must never be reported as a result. The latest commit must clear scrutineering, preserve a transparent public audit trail, and state what changed, what was observed, and what would prove the change wrong.

## References

[1]: tools/round_three_decision_report.md "Manus FC private round-two decision reliability"
[2]: ../rfl-league-data/seasons/s2/m1_real_machina_frontier_manus/telemetry.jsonl "Round-one public telemetry"
