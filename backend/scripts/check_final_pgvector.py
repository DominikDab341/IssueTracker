"""Read-only parity check: replay frozen vectors through PostgreSQL's cosine.

No ticket/reference tables are queried. PostgreSQL receives only sealed snapshot
vectors as query parameters; the check never tunes or changes final predictions.
"""
import asyncio
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))
from scripts.prepare_final_evaluation import DEFAULT, digest, json_bytes, verify_freeze

QUERY = """
SELECT item.id, item.category,
       CAST(item.embedding AS vector) <=> CAST(:query_vector AS vector) AS distance
FROM jsonb_to_recordset(CAST(:references AS jsonb))
     AS item(id integer, category text, embedding text)
ORDER BY distance, item.id
LIMIT :k
"""


async def main():
    import numpy as np
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.settings import settings
    root = DEFAULT
    destination = root / "checks/pgvector-parity.json"
    if destination.exists():
        raise ValueError("Parity result exists; it will not be overwritten.")
    for name in ("frozen", "sealed", "results"):
        verify_freeze(root / name)
    report = json.loads((root / "results/report.json").read_bytes())
    refs = json.loads((root / "frozen/references.json").read_bytes())
    vectors = np.load(root / "results/query-vectors.npy", allow_pickle=False)
    if vectors.shape != (len(report["predictions"]), 384):
        raise ValueError("Query vector shape differs from the result set.")
    payload = json.dumps([{"id": row["id"], "category": row["category"],
                           "embedding": json.dumps(row["embedding_vector"])} for row in refs])
    config = report["configuration"]
    checks = []
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(text("SET TRANSACTION READ ONLY"))
            server = (await connection.execute(text("SELECT current_setting('server_version')"))).scalar_one()
            extension = (await connection.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))).scalar_one()
            for vector, prediction in zip(vectors, report["predictions"], strict=True):
                rows = (await connection.execute(text(QUERY), {"references": payload,
                        "query_vector": json.dumps(vector.tolist()), "k": config["K_NEIGHBORS"]})).mappings().all()
                raw = Counter(row["category"] for row in rows).most_common(1)[0][0]
                support = [row for row in rows if row["category"] == raw]
                score = max(-1.0, min(1.0, max(1 - float(row["distance"]) for row in support)))
                reason = ("low_category_similarity" if score < config["CATEGORY_MIN_SIMILARITY"] else
                          "split_category_vote" if len(support) / len(rows) < config["CATEGORY_MIN_VOTE_SHARE"] else None)
                accepted = None if reason else raw
                checks.append({"id": prediction["id"], "same_neighbor_ids": [row["id"] for row in rows] == [row["id"] for row in prediction["neighbors"]],
                               "same_raw_category": raw == prediction["raw_category"],
                               "same_operational_category": accepted == prediction["accepted_category"],
                               "same_review_reason": reason == prediction["category_review_reason"],
                               "absolute_score_difference": abs(score - prediction["category_score"])})
    finally:
        await engine.dispose()
    differences = [row for row in checks if not all(row[key] for key in
                   ("same_neighbor_ids", "same_raw_category", "same_operational_category", "same_review_reason"))]
    result = {"checked_at": datetime.now(timezone.utc).isoformat(), "postgresql": server, "pgvector": extension,
              "sql": QUERY, "script_sha256": digest(Path(__file__).read_bytes()),
              "report_sha256": digest((root / "results/report.json").read_bytes()),
              "query_vectors_sha256": digest((root / "results/query-vectors.npy").read_bytes()),
              "reference_snapshot_sha256": digest((root / "frozen/references.json").read_bytes()),
              "read_only": True, "application_ticket_or_reference_tables_read": False,
              "count": len(checks), "different_decisions_or_neighbors": differences,
              "max_absolute_score_difference": max(row["absolute_score_difference"] for row in checks), "checks": checks}
    destination.parent.mkdir(exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(json_bytes(result))
    print(f"pgvector parity: {len(checks)} cases; differences: {len(differences)}; max score delta: {result['max_absolute_score_difference']:.3g}")
    if differences:
        raise ValueError("Replay differs from pgvector; review the saved diagnostic without retuning the model.")


if __name__ == "__main__":
    asyncio.run(main())
