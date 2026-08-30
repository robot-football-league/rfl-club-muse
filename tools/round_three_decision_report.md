# Manus FC — Private Round-Two Decision Reliability

## Team-level result

| Total decisions | Applied | Missed deadline | Hung call | Invalid reply | Dropped rate |
|---:|---:|---:|---:|---:|---:|
| 570 | 413 | 150 | 7 | 0 | 27.5% |

## By player

| Robot | Decisions | Applied | Missed deadline | Hung call | Dropped rate | Median applied latency |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 281 | 207 | 70 | 4 | 26.3% | 2.73 s |
| 3 | 289 | 206 | 80 | 3 | 28.7% | 2.78 s |

## Context of the discarded calls

There were **157 discarded decisions**. Of those, **16** occurred while the visible ball was beyond x=+2.0 in Manus FC's defensive half; **18** occurred while Manus FC was level or behind. The first two decisions of the match were both late (3.607 s and 3.975 s), so the team began from holds rather than a live kickoff action.

## Public positional check: the prior loss

Against Real Machina, Manus FC lost 11–0 and the public ball telemetry spent **339 sampled seconds** beyond x=+2.0 in the Manus defensive half. At each of the 11 goal snapshots, the nearest Manus robot averaged **3.84 m** from the ball (minimum 1.40 m; maximum 7.38 m). That failure was tactical separation, whereas the Gemini result shows an additional reliability failure after the LLM rewrite.

## Conclusion

The structural issue is **decision reliability**, not malformed replies: invalid replies were zero, but more than one in four decisions were discarded past the three-second shot clock. A hybrid that waits for an LLM before applying its local fallback cannot address that failure, because the fallback is never reached on a late call. The next implementation must make the live decision path local and deterministic, using the published field coordinates, ball velocity, and legal SDK skills to assign a single chaser and a covering player without a network round trip.
