# Benchmark & Evaluation Plan

## Official Theme 4 targets from the supplied guide

The project should be evaluated against the guide's six gates:

- **G1 Reproducibility:** container launch / clean-machine replay
- **G2 Early Retrieval:** >= 80% of eligible queries retrieve before utterance completion
- **G3 Multi-Intent Identification:** >= 70% of compound queries identify at least two intents
- **G4 Factual Grounding:** >= 85% citation support
- **G5 Session Refinement:** late constraints update the existing state without restart
- **G6 Telemetry & Observability:** 100% trace coverage

These thresholds come from the supplied Theme 4 guide and must be measured on the official test set before being claimed in the final submission.

## Local demo benchmark

`python scripts/run_benchmark.py` evaluates:

1. Early retrieval on a partial utterance
2. Multi-intent decomposition
3. Late-arriving constraint refinement
4. Query suppression
5. Citation presence

Output: `artifacts/benchmark_results.json`.

## Ablations

### A. Hybrid vs sparse-only

```bash
python scripts/run_ablation.py --mode hybrid_vs_sparse
```

This compares ranking under the configured hybrid scorer with sparse-only retrieval.

### B. Controller vs always-retrieve behavior

```bash
python scripts/run_ablation.py --mode controller_vs_always_retrieve
```

This demonstrates retrieval suppression for presentation-only requests.

## Recommended final measurements

When the official corpus/test set is available, record:

- early-retrieval precision/recall
- multi-intent exact/partial match rate
- citation support rate
- cold retrieval latency
- incremental retrieval latency
- number of retrievals per utterance
- tokens/cost per answer
- answer-version deltas after late constraints
- trace coverage
