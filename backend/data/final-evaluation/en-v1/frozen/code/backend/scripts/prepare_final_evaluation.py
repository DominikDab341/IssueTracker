"""Freeze the running classifier and validate human-reviewed test candidates.

No inference, training, ticket creation or reference import takes place here.
The host command reads the runtime through Docker; verify/validate are offline.
"""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

BACKEND = Path(__file__).resolve().parent.parent
ROOT = BACKEND.parent
DEFAULT = BACKEND / "data/final-evaluation/en-v1"
CATEGORIES = ("accounts_access", "hardware", "network", "software")
PRIORITIES = ("low", "medium", "high", "critical")
CONFIG_KEYS = ("MODEL_NAME", "MODEL_REVISION", "CLASSIFICATION_REFERENCE_SOURCE", "K_NEIGHBORS",
               "CATEGORY_MIN_SIMILARITY", "CATEGORY_MIN_VOTE_SHARE", "PRIORITY_MIN_SCORE",
               "DUPLICATE_MIN_SIMILARITY", "DUPLICATE_SAME_CATEGORY", "MAX_DUPLICATE_SUGGESTIONS",
               "ESCALATION_ENABLED", "ESCALATION_MIN_USERS", "ESCALATION_WINDOW_HOURS",
               "ESCALATION_MIN_SIMILARITY")


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


async def runtime_snapshot():
    # Imports confined to the export command: offline validation needs stdlib only.
    sys.path.insert(0, str(BACKEND))
    from huggingface_hub import snapshot_download
    from sqlalchemy import select, text
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from app.models.models import ClassificationReference
    from app.services.classifier import active_reference_filter
    from app.services.priority_classifier import make_priority_model
    from app.settings import settings

    engine = create_async_engine(settings.DATABASE_URL, isolation_level="REPEATABLE READ")
    try:
        async with AsyncSession(engine) as db, db.begin():
            await db.execute(text("SET TRANSACTION READ ONLY"))
            revision = (await db.execute(text("SELECT version_num FROM alembic_version"))).scalar_one()
            rows = (await db.scalars(select(ClassificationReference).where(active_reference_filter())
                                    .order_by(ClassificationReference.id))).all()
            fields = ("id", "text", "category", "base_priority", "source", "source_key",
                      "source_ticket_id", "source_content_version", "approved_by_id", "approved_at", "created_at")
            references = []
            for row in rows:
                record = {field: getattr(row, field) for field in fields}
                for key, value in record.items():
                    if isinstance(value, datetime):
                        record[key] = value.isoformat()
                record["embedding_vector"] = [float(v) for v in row.embedding_vector]
                references.append(record)
    finally:
        await engine.dispose()
    if not references:
        raise ValueError("Cannot freeze an empty reference set.")
    for row in references:
        vector = row["embedding_vector"]
        if len(vector) != 384 or not all(math.isfinite(v) for v in vector) or not any(vector):
            raise ValueError("Invalid stored reference vector.")

    # Hash cached assets without loading the encoder or querying candidate cases.
    hub_id = settings.MODEL_NAME if "/" in settings.MODEL_NAME else "sentence-transformers/" + settings.MODEL_NAME
    cache = Path(snapshot_download(hub_id, revision=settings.MODEL_REVISION, local_files_only=True))
    model_files = {str(p.relative_to(cache)).replace("\\", "/"): digest(p.read_bytes())
                   for p in sorted(cache.rglob("*")) if p.is_file()}
    model = make_priority_model()
    vectorizer, regression = model.steps[0][1], model.steps[1][1]
    return {"captured_at": datetime.now(timezone.utc).isoformat(), "database_revision": revision,
            "configuration": {key: getattr(settings, key) for key in CONFIG_KEYS},
            "priority_estimator": {"vectorizer": vectorizer.get_params(), "regression": regression.get_params()},
            "runtime": {"python": platform.python_version(), "platform": platform.platform(),
                        "packages": {name: version(name) for name in ("numpy", "scikit-learn", "scipy", "sentence-transformers",
                                     "transformers", "torch", "sqlalchemy", "pgvector", "asyncpg")}},
            "model_hub_id": hub_id, "model_files_sha256": model_files, "references": references}


def freeze(destination):
    if destination.exists():
        raise ValueError("Freeze already exists. It will not be overwritten.")
    # UTF-8 is explicit because the host may use a Windows locale.
    command = ["docker", "compose", "exec", "-T", "api", "python", "scripts/prepare_final_evaluation.py", "_runtime"]
    runtime = json.loads(subprocess.check_output(command, cwd=ROOT).decode("utf-8"))
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    source_paths = sorted((BACKEND / "app").rglob("*.py")) + [BACKEND / "requirements.txt", BACKEND / "Dockerfile"]
    source_paths += [BACKEND / "data/pilot/decision-policies/policy.json", Path(__file__).resolve()]
    # Save exact sources as well as the Git revision: a dirty tree remains reproducible.
    files = {"references.json": json_bytes(runtime.pop("references")), "runtime.json": json_bytes(runtime),
             "known-pilot.en.json": (BACKEND / "data/pilot/tickets.en.json").read_bytes()}
    for path in source_paths:
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        files["code/" + relative] = path.read_bytes()
    sources = Counter(row["source"] for row in json.loads(files["references.json"]))
    manifest = {"schema_version": 1, "purpose": "fixed_references_for_independent_synthetic_test",
                "git_revision": revision, "git_status_at_capture": status,
                "captured_at": runtime["captured_at"], "reference_counts": dict(sources),
                "no_test_predictions_generated": True,
                "files_sha256": {name: digest(payload) for name, payload in files.items()}}
    destination.mkdir(parents=True)
    for name, payload in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(payload)
    with (destination / "manifest.json").open("xb") as stream:
        stream.write(json_bytes(manifest))
    print(f"Frozen {sum(sources.values())} references in {destination}")
    print(f"Manifest SHA-256: {digest((destination / 'manifest.json').read_bytes())}")


def verify_freeze(destination):
    manifest = json.loads((destination / "manifest.json").read_bytes())
    for name, expected in manifest["files_sha256"].items():
        path = (destination / name).resolve()
        if not path.is_relative_to(destination.resolve()) or digest(path.read_bytes()) != expected:
            raise ValueError(f"Frozen artifact changed: {name}")
    return manifest


def normalized(text):
    return " ".join(text.casefold().split())


def validate_candidates(dataset, references, known_examples, *, require_approved=False):
    if (dataset.get("schema_version") != 1 or dataset.get("language") != "en"
            or dataset.get("purpose") != "independent_synthetic_test_candidates"):
        raise ValueError("Expected EN final-test candidates, separate from the pilot.")
    examples = dataset.get("examples", [])
    if not examples or len(examples) > 60:
        raise ValueError("Expected 1–60 candidates.")
    if require_approved and len(examples) != 60:
        raise ValueError("Final assessment requires the complete 60-case collection.")
    known_texts = {normalized(row["text"]) for row in references + known_examples}
    known_groups = {row["group_id"] for row in known_examples}
    ids, groups, texts = set(), set(), set()
    for row in examples:
        if not isinstance(row.get("id"), str) or not row["id"] or row["id"] in ids:
            raise ValueError("Missing or repeated candidate ID.")
        ids.add(row["id"])
        group = row.get("group_id")
        if not isinstance(group, str) or not group or group in known_groups or group in groups:
            raise ValueError("Test incidents must be distinct and outside the pilot.")
        groups.add(group)
        value = row.get("text")
        if not isinstance(value, str) or not value.strip() or len(value) > 10000:
            raise ValueError("Missing or invalid candidate text.")
        text = normalized(value)
        if text in known_texts or text in texts:
            raise ValueError("Candidate repeats a reference, known pilot query or another candidate.")
        texts.add(text)
        if row.get("reference_eligible") is not False:
            raise ValueError("Test cases cannot become training references.")
        if row.get("proposed_category") not in CATEGORIES or row.get("proposed_base_priority") not in PRIORITIES:
            raise ValueError("Invalid proposed labels.")
        for key in ("category_reason", "priority_reason", "novelty_note"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing {key}.")
        review = row.get("review", {})
        state = review.get("status")
        if state not in ("pending", "approved", "excluded"):
            raise ValueError("Invalid review state.")
        if state == "pending":
            if any(review.get(key) is not None for key in ("category", "base_priority", "reviewer", "reviewed_at")):
                raise ValueError("Pending cases cannot contain a human approval.")
        else:
            if not review.get("reviewer") or not review.get("reviewed_at"):
                raise ValueError("Human review requires an author and date.")
            if datetime.fromisoformat(review["reviewed_at"]).utcoffset() is None:
                raise ValueError("Review date must include a timezone.")
            if state == "approved":
                if review.get("category") not in CATEGORIES or review.get("base_priority") not in PRIORITIES:
                    raise ValueError("Approved cases need both human-reviewed labels.")
                corrected = (review["category"], review["base_priority"]) != (row["proposed_category"], row["proposed_base_priority"])
                if corrected and not review.get("notes"):
                    raise ValueError("Label corrections require a reason.")
            elif not review.get("notes"):
                raise ValueError("Exclusion requires a reason before predictions are seen.")
        if require_approved and state != "approved":
            raise ValueError("All 60 cases must be approved before assessment; replace excluded cases first.")
    return Counter(row["review"]["status"] for row in examples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "verify", "validate", "_runtime"))
    parser.add_argument("--directory", type=Path, default=DEFAULT)
    parser.add_argument("--require-approved", action="store_true")
    args = parser.parse_args()
    if args.command == "_runtime":
        # Estimator get_params contains Python types (e.g. numpy.float64).
        print(json.dumps(asyncio.run(runtime_snapshot()), default=str, allow_nan=False))
    elif args.command == "freeze":
        freeze(args.directory / "frozen")
    else:
        verify_freeze(args.directory / "frozen")
        if args.command == "validate":
            dataset = json.loads((args.directory / "candidates.json").read_bytes())
            refs = json.loads((args.directory / "frozen/references.json").read_bytes())
            pilot = json.loads((args.directory / "frozen/known-pilot.en.json").read_bytes())["examples"]
            states = validate_candidates(dataset, refs, pilot, require_approved=args.require_approved)
            print(f"Candidate format and exact-overlap checks OK: {dict(states)}. No inference executed.")
        else:
            print("Frozen file hashes OK. No database access or inference.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
