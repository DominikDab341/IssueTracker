"""Seal and evaluate the approved EN holdout with the frozen runtime classifier.

Run evaluation inside the captured Docker runtime. The SQL result is replayed
from frozen vectors in memory; no application database is connected or changed.
"""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter
from types import SimpleNamespace

BACKEND = next(parent for parent in Path(__file__).resolve().parents
               if (parent / "scripts/prepare_final_evaluation.py").is_file())
sys.path.insert(0, str(BACKEND))
from scripts.prepare_final_evaluation import (
    CATEGORIES, PRIORITIES, DEFAULT, digest, json_bytes, validate_candidates, verify_freeze,
)


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def classification_metrics(truth, guesses, labels):
    """Four target classes; a deferred decision is a fifth matrix column/FN."""
    if len(truth) != len(guesses) or any(value not in labels for value in truth):
        raise ValueError("Invalid metric inputs.")
    columns = list(labels) + ["review"]
    matrix = [[sum(expected == label and guess == column for expected, guess in zip(truth, guesses))
               for column in columns] for label in labels]
    if any(value not in columns for value in guesses):
        raise ValueError("Invalid predicted label.")
    per_class = {}
    for index, label in enumerate(labels):
        tp = matrix[index][index]
        support = sum(matrix[index])
        predicted = sum(row[index] for row in matrix)
        precision, recall = rate(tp, predicted) or 0.0, rate(tp, support) or 0.0
        per_class[label] = {"support": support, "precision": precision, "recall": recall,
                            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0}
    return {"count": len(truth), "correct": sum(a == b for a, b in zip(truth, guesses)),
            "accuracy": rate(sum(a == b for a, b in zip(truth, guesses)), len(truth)),
            "macro_f1": sum(row["f1"] for row in per_class.values()) / len(labels) if truth else None,
            "labels": list(labels), "prediction_columns": columns, "confusion_matrix": matrix, "per_class": per_class}


def summarize(rows, dimension):
    labels = CATEGORIES if dimension == "category" else PRIORITIES
    known = [row for row in rows if row["expected_" + dimension] is not None]
    unknown = [row for row in rows if row["expected_" + dimension] is None]
    truth = [row["expected_" + dimension] for row in known]
    raw = [row["raw_" + dimension] for row in known]
    decisions = [row["accepted_" + dimension] or "review" for row in known]
    accepted = [row for row in known if row["accepted_" + dimension] is not None]
    unknown_review = sum(row["accepted_" + dimension] is None for row in unknown)
    correct_accepted = sum(row["expected_" + dimension] == row["accepted_" + dimension] for row in accepted)
    result = {"total": len(rows), "identifiable": len(known), "unidentifiable": len(unknown),
              "raw": classification_metrics(truth, raw, labels),
              "operational": classification_metrics(truth, decisions, labels),
              "known_accepted": len(accepted), "known_coverage": rate(len(accepted), len(known)),
              "accepted_accuracy": rate(correct_accepted, len(accepted)),
              "all_review_count": sum(row["accepted_" + dimension] is None for row in rows),
              "all_coverage": rate(sum(row["accepted_" + dimension] is not None for row in rows), len(rows)),
              "unidentifiable_review_count": unknown_review,
              "unidentifiable_review_rate": rate(unknown_review, len(unknown)),
              "unidentifiable_automatic_count": len(unknown) - unknown_review}
    if dimension == "priority":
        urgent = [row for row in known if row["expected_priority"] in ("high", "critical")]
        result["urgent"] = {"count": len(urgent),
                            "raw_as_low_medium": sum(row["raw_priority"] in ("low", "medium") for row in urgent),
                            "accepted_as_low_medium": sum(row["accepted_priority"] in ("low", "medium") for row in urgent),
                            "deferred": sum(row["accepted_priority"] is None for row in urgent),
                            "critical_raw_underestimated": sum(row["raw_priority"] != "critical" for row in known
                                                                if row["expected_priority"] == "critical")}
        result["always_medium_baseline"] = classification_metrics(truth, ["medium"] * len(truth), labels)
    return result


def seal(directory):
    target = directory / "sealed"
    if target.exists():
        raise ValueError("Sealed test exists; it will not be overwritten.")
    verify_freeze(directory / "frozen")
    payload = (directory / "candidates.json").read_bytes()
    data = json.loads(payload)
    refs = json.loads((directory / "frozen/references.json").read_bytes())
    pilot = json.loads((directory / "frozen/known-pilot.en.json").read_bytes())["examples"]
    validate_candidates(data, refs, pilot, require_approved=True)
    protocol = {"schema_version": 1, "total": 100, "quality": {"complete": 70, "weak": 30},
                "classification": "raw and gated accuracy/macro-F1 on each identifiable label; review is FN",
                "cohorts": ["all", "complete", "weak"], "macro_f1_classes": "all four target classes",
                "missing_labels": "not scored as right/wrong; report review and unjustified automatic acceptance independently per task",
                "priority_scope": "base priority only, without checkbox/admin/escalation; always-medium baseline",
                "references": "fixed snapshot only; test texts never fit TF-IDF, IDF or regression",
                "ranking": "cosine over stored float32 reference vectors replayed as float64, ties by database ID",
                "runtime_code": "frozen app.services.classifier.classify; in-memory reference-query adapter",
                "no_retuning_on_test": True, "real_world_data": False}
    files = {"test.en.json": payload, "protocol.json": json_bytes(protocol)}
    files["evaluation-script.py"] = Path(__file__).read_bytes()
    files["preparation-script.py"] = (BACKEND / "scripts/prepare_final_evaluation.py").read_bytes()
    files["approval-event.json"] = (directory / "reviews/final-approval-100.json").read_bytes()
    manifest = {"schema_version": 1, "sealed_at": datetime.now(timezone.utc).isoformat(),
                "reference_manifest_sha256": digest((directory / "frozen/manifest.json").read_bytes()),
                "files_sha256": {name: digest(value) for name, value in files.items()}}
    target.mkdir()
    for name, value in files.items():
        with (target / name).open("xb") as stream:
            stream.write(value)
    with (target / "manifest.json").open("xb") as stream:
        stream.write(json_bytes(manifest))
    print(f"Sealed 100 approved cases. Test SHA-256: {digest(payload)}")


class MemoryReferences:
    """Substitute only the frozen classifier's SELECT result, never its decisions."""
    def __init__(self, references):
        import numpy as np
        self.references = references
        vectors = np.asarray([row["embedding_vector"] for row in references], dtype=np.float64)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if not np.isfinite(vectors).all() or (norms == 0).any():
            raise ValueError("Invalid frozen vectors.")
        self.normalized = vectors / norms
        self.last_neighbors = []

    async def execute(self, query):
        import numpy as np
        params = query.compile().params
        vectors = [value for value in params.values() if isinstance(value, (list, tuple)) and len(value) == 384]
        if len(vectors) != 1:
            raise ValueError("Expected exactly one frozen classifier vector query.")
        vector = np.asarray(vectors[0], dtype=np.float64)
        norm = np.linalg.norm(vector)
        if not np.isfinite(vector).all() or not norm:
            raise ValueError("Invalid query vector.")
        scores = np.clip(self.normalized @ (vector / norm), -1, 1)
        order = sorted(range(len(self.references)), key=lambda i: (-float(scores[i]), self.references[i]["id"]))
        keys = ("source_key", "text", "source", "category", "base_priority")
        selected = [{**{key: self.references[i][key] for key in keys}, "distance": 1 - float(scores[i])} for i in order]
        self.last_neighbors = [{"id": self.references[i]["id"], "source_key": self.references[i]["source_key"],
                                "category": self.references[i]["category"], "similarity": float(scores[i])} for i in order[:3]]
        return SimpleNamespace(mappings=lambda: SimpleNamespace(all=lambda: selected))


def runtime_preflight(directory):
    frozen = directory / "frozen"
    verify_freeze(frozen)
    verify_freeze(directory / "sealed")
    sealed = json.loads((directory / "sealed/manifest.json").read_bytes())
    if digest((frozen / "manifest.json").read_bytes()) != sealed["reference_manifest_sha256"]:
        raise ValueError("Reference snapshot changed after sealing.")
    if digest(Path(__file__).read_bytes()) != sealed["files_sha256"]["evaluation-script.py"]:
        raise ValueError("Evaluator changed after sealing; run the sealed evaluator copy.")
    if digest((BACKEND / "scripts/prepare_final_evaluation.py").read_bytes()) != sealed["files_sha256"]["preparation-script.py"]:
        raise ValueError("Preparation/validation code changed after sealing; restore its sealed copy before replay.")
    runtime = json.loads((frozen / "runtime.json").read_bytes())
    actual = {name: version(name) for name in runtime["runtime"]["packages"]}
    if actual != runtime["runtime"]["packages"] or platform.python_version() != runtime["runtime"]["python"]:
        raise ValueError("Runtime differs from the frozen Docker runtime; do not evaluate in the host venv.")
    from huggingface_hub import snapshot_download
    cache = Path(snapshot_download(runtime["model_hub_id"], revision=runtime["configuration"]["MODEL_REVISION"], local_files_only=True))
    for name, expected in runtime["model_files_sha256"].items():
        if digest((cache / name).read_bytes()) != expected:
            raise ValueError(f"Cached model asset changed: {name}")
    return runtime, cache


async def evaluate(directory):
    output = directory / "results"
    if output.exists():
        raise ValueError("Final results exist; they will not be overwritten.")
    runtime, cache = runtime_preflight(directory)
    frozen = directory / "frozen"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(frozen / "code/backend"))
    # Imports now resolve to the frozen app, not the mutable working-tree app.
    from app.services import classifier, priority_classifier
    if not Path(classifier.__file__).resolve().is_relative_to(frozen.resolve()):
        raise ValueError("Classifier did not load from the frozen snapshot.")
    classifier.settings = SimpleNamespace(**runtime["configuration"])
    estimator = priority_classifier.make_priority_model()
    parameters = {"vectorizer": estimator.steps[0][1].get_params(), "regression": estimator.steps[1][1].get_params()}
    if json.loads(json.dumps(parameters, default=str)) != runtime["priority_estimator"]:
        raise ValueError("Estimator parameters differ from the freeze.")
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    references = json.loads((frozen / "references.json").read_bytes())
    dataset = json.loads((directory / "sealed/test.en.json").read_bytes())
    pilot = json.loads((frozen / "known-pilot.en.json").read_bytes())["examples"]
    validate_candidates(dataset, references, pilot, require_approved=True)
    adapter = MemoryReferences(references)
    started = perf_counter()
    model = SentenceTransformer(str(cache), device="cpu")
    load_seconds = perf_counter() - started
    classifier.get_model = lambda: model
    examples, vectors, rows = dataset["examples"], [], []
    started = perf_counter()
    for index, item in enumerate(examples, 1):
        prediction = await classifier.classify(item["text"], adapter)
        vector = np.asarray(prediction.vector, dtype=np.float32)
        if vector.shape != (384,):
            raise ValueError("Unexpected embedding dimension.")
        vectors.append(vector)
        rows.append({"id": item["id"], "group_id": item["group_id"], "text": item["text"],
                     "quality": item.get("description_quality", "complete"),
                     "expected_category": item["review"]["category"], "expected_priority": item["review"]["base_priority"],
                     "raw_category": prediction.predicted_category, "raw_priority": prediction.predicted_base_priority,
                     "accepted_category": None if prediction.category == "unknown" else prediction.category,
                     "accepted_priority": prediction.base_priority,
                     "category_score": prediction.category_score, "priority_score": prediction.priority_score,
                     "category_review_reason": prediction.category_review_reason, "priority_review_reason": prediction.priority_review_reason,
                     "classification_version": prediction.classification_version, "neighbors": adapter.last_neighbors})
        if index % 10 == 0:
            print(f"Classified {index}/100 with frozen references", flush=True)
    elapsed = perf_counter() - started
    cohorts = {name: {"count": len(selected), **{dimension: summarize(selected, dimension) for dimension in ("category", "priority")}}
               for name in ("all", "complete", "weak")
               for selected in [[row for row in rows if name == "all" or row["quality"] == name]]}
    report = {"schema_version": 1, "evaluated_at": datetime.now(timezone.utc).isoformat(),
              "test_sha256": digest((directory / "sealed/test.en.json").read_bytes()),
              "reference_manifest_sha256": digest((frozen / "manifest.json").read_bytes()),
              "evaluator_sha256": digest(Path(__file__).read_bytes()), "reference_count": len(references),
              "model_revision": runtime["configuration"]["MODEL_REVISION"], "configuration": runtime["configuration"],
              "runtime": runtime["runtime"], "hardware": {"cpu_count": os.cpu_count(), "machine": platform.machine(),
                                                         "torch_threads": torch.get_num_threads()},
              "timings_seconds": {"model_load": load_seconds, "classification_100": elapsed},
              "method": "frozen runtime classify(), offline float64 cosine over stored reference vectors, ID tie-break",
              "limitations": ["synthetic cases, author-reviewed; same authoring assistant knew the pilot",
                              "small and purposefully sampled cohorts; not real-world ticket prevalence",
                              "host pilot and frozen Docker library versions differ",
                              "float64 cosine replay may differ at floating-point boundaries from pgvector",
                              "raw model scores are not calibrated correctness probabilities",
                              "no changes to thresholds, references or model based on these results"],
              "cohorts": cohorts, "predictions": rows}
    output.mkdir()
    np.save(output / "query-vectors.npy", np.asarray(vectors), allow_pickle=False)
    import joblib
    joblib.dump(priority_classifier._cached_model, output / "priority-model.joblib")
    report["artifacts_sha256"] = {name: digest((output / name).read_bytes()) for name in ("query-vectors.npy", "priority-model.joblib")}
    (output / "report.json").write_bytes(json_bytes(report))
    (output / "report.md").write_text(render_report(report), encoding="utf-8")
    (output / "manifest.json").write_bytes(json_bytes({
        "schema_version": 1, "files_sha256": {name: digest((output / name).read_bytes())
                                              for name in ("report.json", "report.md", "query-vectors.npy", "priority-model.joblib")}}))
    print(json.dumps({name: {key: value[key] for key in ("count",)} for name, value in cohorts.items()}), flush=True)
    print(f"Saved final evaluation to {output}", flush=True)


def percent(value):
    return f"{value:.1%}" if value is not None else "—"


def render_report(report):
    lines = ["# Końcowy test klasyfikacji EN — 100 przypadków (70/30)", "", f"Pomiar: {report['evaluated_at']}",
             f"Test SHA-256: `{report['test_sha256']}`.", "", "100 zatwierdzonych przypadków syntetycznych; 120 stałych referencji.",
             "Dane testowe nie uczestniczą w uczeniu TF-IDF, IDF lub regresji. Modele i progi zachowano po teście.", "",
             "## Trafność dla ustalalnych etykiet", "",
             "Raw = propozycja przed progami; operacyjna = po progach, odmowa liczona jako FN.",
             "Macro-F1 obejmuje cztery klasy. Poprawność zaakceptowanych zawsze czytać razem z pokryciem.", "",
             "| Część | Zadanie | Ocenialne / wszystkie | Raw accuracy | Raw macro-F1 | Operacyjna accuracy | Operacyjna macro-F1 | Pokrycie ocenialnych | Accuracy zaakceptowanych |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, cohort in report["cohorts"].items():
        for dimension in ("category", "priority"):
            result = cohort[dimension]
            raw, operational = result["raw"], result["operational"]
            lines.append(f"| {name} | {dimension} | {result['identifiable']}/{cohort['count']} | {percent(raw['accuracy'])} | {raw['macro_f1']:.3f} | "
                         f"{percent(operational['accuracy'])} | {operational['macro_f1']:.3f} | {percent(result['known_coverage'])} | {percent(result['accepted_accuracy'])} |")
    lines += ["", "## Brak informacji do ustalenia etykiety", "",
              "Null nie jest klasą i nie jest zaliczane jako trafienie lub pomyłka klasyfikacji.",
              "Przyjęcie automatycznej etykiety mimo braku danych raportujemy osobno.", "",
              "| Zadanie | Nieustalalne | Do weryfikacji | Odsetek weryfikacji | Automatycznie przyjęte mimo braku danych |",
              "|---|---:|---:|---:|---:|"]
    for dimension in ("category", "priority"):
        result = report["cohorts"]["all"][dimension]
        lines.append(f"| {dimension} | {result['unidentifiable']} | {result['unidentifiable_review_count']} | {percent(result['unidentifiable_review_rate'])} | {result['unidentifiable_automatic_count']} |")
    priority = report["cohorts"]["all"]["priority"]
    lines += ["", f"Baseline zawsze medium: {percent(priority['always_medium_baseline']['accuracy'])} na {priority['identifiable']} ustalalnych priorytetach.",
              f"Pilne (high/critical): {priority['urgent']['count']}; raw zaniżone do low/medium: {priority['urgent']['raw_as_low_medium']}; po progach: {priority['urgent']['accepted_as_low_medium']}; do weryfikacji: {priority['urgent']['deferred']}.",
              f"Critical raw zaniżone do dowolnego niższego poziomu: {priority['urgent']['critical_raw_underestimated']}.",
              "Checkbox, eskalacja i ręczne decyzje nie są częścią jakości przewidywania priorytetu bazowego."]
    for dimension in ("category", "priority"):
        for mode in ("raw", "operational"):
            metric = report["cohorts"]["all"][dimension][mode]
            lines += ["", f"## Macierz pomyłek: {dimension}, {mode}", "", "Wiersze: etykiety wzorcowe; kolumny: odpowiedź. review oznacza odmowę.", "",
                      "| Wzorcowa | " + " | ".join(metric["prediction_columns"]) + " |",
                      "|---|" + "---:|" * len(metric["prediction_columns"])]
            for label, counts in zip(metric["labels"], metric["confusion_matrix"]):
                lines.append(f"| {label} | " + " | ".join(map(str, counts)) + " |")
    lines += ["", "## Pomyłki i odmowy na ustalalnych etykietach", "",
              "| ID | Zadanie | Wzorcowa | Raw | Po progach | Powód weryfikacji |", "|---|---|---|---|---|---|"]
    for row in report["predictions"]:
        for dimension in ("category", "priority"):
            expected = row["expected_" + dimension]
            if expected is not None and expected != row["accepted_" + dimension]:
                lines.append(f"| {row['id']} | {dimension} | {expected} | {row['raw_' + dimension]} | {row['accepted_' + dimension] or 'review'} | {row[dimension + '_review_reason'] or '—'} |")
    lines += ["", "## Warunki i ograniczenia", ""]
    lines += [f"- {item}" for item in report["limitations"]]
    lines += ["", f"Ładowanie modelu: {report['timings_seconds']['model_load']:.2f} s; klasyfikacja 100: {report['timings_seconds']['classification_100']:.2f} s.",
              "Pomiar jednorazowy, nie benchmark opóźnienia endpointu. Szczegóły per klasa, wszystkie odpowiedzi i sąsiedzi: [report.json](report.json).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "evaluate"))
    parser.add_argument("--directory", type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.command == "seal":
        seal(args.directory)
    else:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        asyncio.run(evaluate(args.directory))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
