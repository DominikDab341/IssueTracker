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
TARGET_COUNT = 100
QUALITY_COUNTS = {"complete": 70, "weak": 30}
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


def label_is_valid(value, labels, *, weak):
    # null is a reviewed lack of information, never an extra classifier class.
    return value in labels or (weak and value is None)


def candidate_summary(dataset):
    rows = dataset["examples"]
    return {"total": len(rows),
            "quality": dict(Counter(row.get("description_quality", "complete") for row in rows)),
            "review": dict(Counter(row["review"]["status"] for row in rows)),
            "proposed_identifiable": {
                quality: {dimension: sum(row[field] is not None for row in rows
                                        if row.get("description_quality", "complete") == quality)
                          for dimension, field in (("category", "proposed_category"), ("priority", "proposed_base_priority"))}
                for quality in ("complete", "weak")}}


def validate_candidates(dataset, references, known_examples, *, require_approved=False):
    if (dataset.get("schema_version") != 1 or dataset.get("language") != "en"
            or dataset.get("purpose") != "independent_synthetic_test_candidates"):
        raise ValueError("Expected EN final-test candidates, separate from the pilot.")
    examples = dataset.get("examples", [])
    if not examples or len(examples) > TARGET_COUNT:
        raise ValueError(f"Expected 1–{TARGET_COUNT} candidates.")
    if require_approved and len(examples) != TARGET_COUNT:
        raise ValueError(f"Final assessment requires the complete {TARGET_COUNT}-case collection.")
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
        quality = row.get("description_quality", "complete")
        if quality not in ("complete", "weak"):
            raise ValueError("Unknown description quality.")
        weak = quality == "weak"
        if weak and (not isinstance(row.get("missing_information"), str) or not row["missing_information"].strip()):
            raise ValueError("Weak descriptions require an explanation of missing information.")
        if ("proposed_category" not in row or "proposed_base_priority" not in row
                or not label_is_valid(row["proposed_category"], CATEGORIES, weak=weak)
                or not label_is_valid(row["proposed_base_priority"], PRIORITIES, weak=weak)):
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
                if ("category" not in review or "base_priority" not in review
                        or not label_is_valid(review["category"], CATEGORIES, weak=weak)
                        or not label_is_valid(review["base_priority"], PRIORITIES, weak=weak)):
                    raise ValueError("Approved cases need both explicit human-reviewed labels; null only for weak descriptions.")
                if (review["category"] is None or review["base_priority"] is None) and not review.get("notes"):
                    raise ValueError("An unidentifiable label requires a human review note.")
                corrected = (review["category"], review["base_priority"]) != (row["proposed_category"], row["proposed_base_priority"])
                if corrected and not review.get("notes"):
                    raise ValueError("Label corrections require a reason.")
            elif not review.get("notes"):
                raise ValueError("Exclusion requires a reason before predictions are seen.")
        if require_approved and state != "approved":
            raise ValueError(f"All {TARGET_COUNT} cases must be approved before assessment; replace excluded cases first.")
    if len(examples) == TARGET_COUNT and (require_approved or "description_quality_counts" in dataset.get("design", {})):
        if candidate_summary(dataset)["quality"] != QUALITY_COUNTS:
            raise ValueError("Final test design requires 70 complete and 30 weak descriptions.")
    return Counter(row["review"]["status"] for row in examples)


def render_reviews(directory, dataset):
    """Render the review copies from JSON, preserving human review state."""
    all_rows = dataset["examples"]
    states = Counter(row["review"]["status"] for row in all_rows)
    quality = candidate_summary(dataset)["quality"]
    for filename, rows, title in (
        ("review.md", all_rows, "Wszystkie przypadki testu EN v1"),
        ("review-new.md", [row for row in all_rows if row["review"]["status"] == "pending"],
         "Nowe przypadki EN do przeglądu autora"),
        ("review-weak.md", [row for row in all_rows if row.get("description_quality") == "weak"],
         f"{quality.get('weak', 0)} słabych opisów EN do przeglądu autora"),
    ):
        lines = [f"# {title}", "", f"Cały zbiór: {len(all_rows)} przypadków; zatwierdzone: {states['approved']}; oczekujące: {states['pending']}.",
                 "", "Etykiety poniżej są propozycjami asystenta, nie przewidywaniami klasyfikatora.",
                 "Przegląd obejmuje treść, kategorię, priorytet bazowy i odrębność od pilotażu.",
                 "Zatwierdzenia dotyczą wyłącznie wskazanych ID; nie obejmują nowo dopisanych przypadków.",
                 "Wszystkie przypadki mają reference_eligible=false i pozostają poza treningiem.",
                 f"Układ: {quality.get('complete', 0)} pełniejszych opisów oraz {quality.get('weak', 0)} słabych. Null = brak informacji do ustalenia etykiety, nie klasa unknown.",
                 "Zatwierdzenie słabego opisu może oznaczać potwierdzenie, że kategorii lub priorytetu nie da się ustalić.",
                 "", "[Protokół i historia przeglądu](README.md)", ""]
        for row in rows:
            review = row["review"]
            lines += [f"## {row['id']}", "", row["text"], "",
                      f"Jakość opisu: **{row.get('description_quality', 'complete')}**.", "",
                      f"Propozycja: **{row['proposed_category'] or 'nieustalalna kategoria'} / {row['proposed_base_priority'] or 'nieustalalny priorytet'}**.", "",
                      f"Kategoria: {row['category_reason']}", f"Priorytet: {row['priority_reason']}", "",
                      f"Odrębność: {row['novelty_note']}", "", f"Decyzja autora: **{review['status']}**."]
            if row.get("missing_information"):
                lines += [f"Brakujące informacje / ograniczenia: {row['missing_information']}"]
            if review["status"] == "approved":
                lines += [f"Zatwierdzone etykiety: **{review['category']} / {review['base_priority']}**.",
                          f"Autor: {review['reviewer']}; zapis decyzji: {review['reviewed_at']}.", review["notes"]]
            lines.append("")
        (directory / filename).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "verify", "validate", "review", "_runtime"))
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
        if args.command in ("validate", "review"):
            dataset = json.loads((args.directory / "candidates.json").read_bytes())
            refs = json.loads((args.directory / "frozen/references.json").read_bytes())
            pilot = json.loads((args.directory / "frozen/known-pilot.en.json").read_bytes())["examples"]
            states = validate_candidates(dataset, refs, pilot, require_approved=args.require_approved)
            print(f"Candidate format and exact-overlap checks OK: {dict(states)}. No inference executed.")
            if args.command == "review":
                render_reviews(args.directory, dataset)
                print("Updated review.md, review-new.md and review-weak.md from the recorded review states.")
            print(json.dumps(candidate_summary(dataset), ensure_ascii=False))
        else:
            print("Frozen file hashes OK. No database access or inference.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
