from __future__ import annotations

import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.dependencies import get_engine


def main():
    engine = get_engine()
    cases = []
    # 1) early retrieval
    r1 = engine.process_chunk("bench-1", 0.8, "I need a venue for 30 people in Pune", is_final=False)
    cases.append({"name":"early_retrieval","pass":r1["decision"]["decision"] == "RETRIEVE","decision":r1["decision"]})

    # 2) multi-intent
    r2 = engine.process_chunk("bench-2", 1.0, "I need venue capacity, cancellation policy and catering options in Pune", is_final=True)
    cases.append({"name":"multi_intent","pass":len(r2["sub_queries"]) >= 2,"subquery_count":len(r2["sub_queries"])})

    # 3) session refinement
    engine.process_chunk("bench-3", 0.0, "Summarize the travel reimbursement rule for an employee trip", is_final=True)
    r3 = engine.process_chunk("bench-3", 0.7, "Actually, the trip was international and the booking was made after travel", is_final=True)
    cases.append({"name":"late_refinement","pass":r3["decision"]["trigger"] == "late_refinement" and r3["answer_version"] >= 2,"trigger":r3["decision"]["trigger"]})

    # 4) suppression
    r4 = engine.process_chunk("bench-3", 1.2, "Please repeat your last answer in bullet points", is_final=True)
    cases.append({"name":"query_suppression","pass":r4["decision"]["decision"] == "NO_RETRIEVAL","decision":r4["decision"]})

    # 5) grounding
    citations = r2.get("citations", [])
    cases.append({"name":"citation_presence","pass":len(citations) > 0,"citation_count":len(citations)})

    passed = sum(1 for c in cases if c["pass"])
    result = {
        "benchmark_type": "local_engineering_demo",
        "passed": passed,
        "total": len(cases),
        "pass_rate": round(passed / len(cases), 3),
        "cases": cases,
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/benchmark_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
