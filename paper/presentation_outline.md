# Live Presentation Outline (15 min + Q&A)

| Slide | Time | Owner | Talking points |
|---|---|---|---|
| 1. Title | 0:30 | Shahmir | Project title, team, course |
| 2. Motivation | 1:30 | Shahmir | Concept drift -> silent degradation; cite Sculley'15, Paleyes'22 |
| 3. Problem statement | 1:00 | Shahmir | Detectors specialise on perf vs distribution; neither alone is great |
| 4. Architecture (live diagram) | 2:00 | AbuBakr | Walk planes: inference, tracking, monitoring, CI/CD; explain feedback edge |
| 5. HybridDD intuition | 1:30 | Zaid | Consensus + confidence override; show Eq. (1) on slide |
| 6. HybridDD algorithm | 1:00 | Zaid | Pseudocode, complexity, hyperparameters |
| 7. Live demo: docker compose up | 2:00 | AbuBakr | Hit /predict, watch Grafana drift dashboard fire, /reload triggered |
| 8. Experimental setup | 1:00 | Shahmir | 36 configs, 3 seeds, prequential, Friedman-Nemenyi |
| 9. Results: accuracy | 1:00 | Shahmir | Table + bar chart; HybridDD wins on ELEC2 + SEA |
| 10. Results: detection delay & FP | 1:00 | Shahmir | HybridDD halves PH delay; FP rate quartered vs KSWIN |
| 11. Critical-difference diagram | 0:30 | Zaid | Demsar's CD; gap > CD vs every comparator on rank |
| 12. CI/CD demo (screen) | 1:00 | AbuBakr | GH Actions panel: lint, tests, build, paper artifact |
| 13. Limitations & future work | 0:30 | Zaid | Multivariate KS, adaptive cooldown, heavier streams |
| 14. Conclusion | 0:30 | Shahmir | Open repo + paper + dashboards; one-command reproducibility |
| 15. Q&A | 0:00 | All | -- |

## Demo backup checklist
- [ ] `docker compose up -d` ran 5 minutes before talk -> all healthy
- [ ] `scripts/smoke_check.sh` returns 200 on everything
- [ ] Grafana dashboards open in 3 tabs (model, drift, infra)
- [ ] Prometheus alert rule loaded; manually trigger by feeding `label!=prediction` repeatedly
- [ ] MLflow UI on `localhost:5000` showing experiment runs
- [ ] Local copy of `paper/main.pdf` for fallback

## Q&A prep
- "Why not just retrain periodically?" -> wasteful + worse accuracy under abrupt drift; HybridDD only triggers on consensus or confident drop.
- "Why not use Evidently / WhyLogs?" -> we want first-class Prometheus signals integrated with the inference plane; their drift JSON exports are an alternative path.
- "Tradeoff of cooldown C?" -> too small => retraining storm; too large => prolonged degradation between detections.
- "Statistical assumptions?" -> Friedman is non-parametric on ranks; safe under non-normal accuracy distributions.
