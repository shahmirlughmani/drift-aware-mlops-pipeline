# ADR 0001 — A hybrid performance + distribution drift detector

**Status:** Accepted (2026-04)
**Deciders:** Zaid · Shahmir Asif · AbuBakr Shahid
**Supersedes:** —
**Superseded by:** —

## Context

Concept-drift detectors fall into two families. Performance-based detectors
(DDM, EDDM, Page-Hinkley, ADWIN) react quickly to drifts that hurt accuracy
but are blind to virtual drift — `P(X)` shifts with `P(y|X)` unchanged — and
require labels. Distribution-based detectors (KSWIN, MMD, χ²) catch covariate
shift label-free but generate false positives on harmless feature noise.

Production ML systems see both kinds of drift, often interleaved. Picking
either family alone leaves a known failure mode on the table.

## Decision

Combine **DDM** (performance) and **KSWIN** (distribution) with a hybrid rule:

> Emit a hard drift event when **(a)** DDM and KSWIN both fire within a
> 200-sample consensus window, **OR** **(b)** DDM enters the drift state
> and the posterior error rate exceeds 0.35 (confidence override).
> A 500-sample cooldown suppresses re-firings.

The cooldown protects against retraining storms; the consensus rule
maintains a low false-positive rate; the override gives fast reaction
to high-impact accuracy drops that the consensus alone would delay.

Implemented in `src/drift/detectors.py::HybridDriftDetector`.

## Alternatives considered

| Option | Rejected because |
|---|---|
| DDM only | Misses virtual drift |
| KSWIN only | Noisy; high FPR on synthetic streams |
| DDM **AND** KSWIN (hard consensus) | No fast-path; misses severe label drift |
| ADDM ensemble (Frías-Blanco et al.) | Higher complexity; no measurable accuracy gain on our streams |
| Bayesian online change-point detection | Not yet implemented in `river`; one-off C++ port out of scope |

## Consequences

**Positive**
- Top-tier accuracy on the Friedman-Nemenyi ranking
- 0.00 false-positive rate on consensus-only configurations
- 53% reduction in mean detection delay vs. Page-Hinkley

**Negative**
- Two extra hyperparameters (`consensus_window`, `confidence_threshold`)
- Tested only on tabular, low-dimensional streams

The sensitivity analysis (`experiments/sensitivity.py`) shows a broad plateau
of good configurations around `(200, 0.35)`, mitigating the tuning concern.

## Validation

- Ablation study (`experiments/ablation.py`): each component (cooldown,
  consensus, override) contributes a measurable degradation when removed.
- Friedman + Nemenyi (`experiments/results/stats.json`): HybridDD is in the
  top group on accuracy and FPR with `p < 0.001`.
