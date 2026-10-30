"""Diagnostyka polskiego pilotażu, bez połączenia z bazą aplikacji."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = BACKEND_ROOT / "data/pilot/tickets.json"
CATEGORIES = ("accounts_access", "hardware", "network", "software")
PRIORITIES = ("low", "medium", "high", "critical")
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_dataset(dataset):
    if not isinstance(dataset, dict) or dataset.get("schema_version") != 1:
        raise ValueError("Nieobsługiwana wersja formatu danych.")
    if dataset.get("purpose") != "exploratory_pilot_only" or dataset.get("language") != "pl":
        raise ValueError("Oczekiwano polskiej próbki pilotażowej.")
    if not nonempty(dataset.get("dataset_id")):
        raise ValueError("Brak identyfikatora zbioru.")
    provenance = dataset.get("provenance", {})
    if not isinstance(provenance, dict) or provenance.get("method") != "llm_assisted_synthetic":
        raise ValueError("Brak informacji o syntetycznym pochodzeniu danych.")
    examples = dataset.get("examples")
    if not isinstance(examples, list) or len(examples) != 40:
        raise ValueError("Pilotaż musi zawierać dokładnie 40 rekordów.")
    ids, texts, groups = set(), set(), {}
    for item in examples:
        if not isinstance(item, dict):
            raise ValueError("Rekord musi być obiektem JSON.")
        ident = item.get("id")
        if not nonempty(ident) or ident in ids:
            raise ValueError("Puste lub powtórzone ID zgłoszenia.")
        ids.add(ident)
        for field in ("text", "group_id", "category_reason", "priority_reason"):
            if not nonempty(item.get(field)):
                raise ValueError(f"{ident}: wymagane niepuste pole {field}.")
        if item["text"] != item["text"].strip() or len(item["text"]) > 10000:
            raise ValueError(f"{ident}: nieprawidłowa długość lub otaczające białe znaki.")
        normalized = " ".join(item["text"].casefold().split())
        if normalized in texts:
            raise ValueError(f"{ident}: identyczna treść innego rekordu.")
        texts.add(normalized)
        if item.get("proposed_category") not in CATEGORIES or item.get("proposed_base_priority") not in PRIORITIES:
            raise ValueError(f"{ident}: nieznana propozycja etykiety.")
        if type(item.get("work_blocked")) is not bool:
            raise ValueError(f"{ident}: work_blocked musi być wartością logiczną.")
        labels = (item["proposed_category"], item["proposed_base_priority"])
        if item["group_id"] in groups and groups[item["group_id"]] != labels:
            raise ValueError(f"{ident}: parafrazy mają sprzeczne propozycje etykiet.")
        groups[item["group_id"]] = labels
        review = item.get("review")
        if not isinstance(review, dict) or review.get("status") not in ("pending", "approved", "excluded"):
            raise ValueError(f"{ident}: nieprawidłowy stan przeglądu.")
        if review["status"] == "pending":
            if any(review.get(field) is not None for field in ("category", "base_priority", "reviewer", "reviewed_at")):
                raise ValueError(f"{ident}: niezatwierdzony rekord zawiera decyzję przeglądu.")
            continue
        if not nonempty(review.get("reviewer")) or not nonempty(review.get("reviewed_at")):
            raise ValueError(f"{ident}: przegląd wymaga autora i daty.")
        try:
            reviewed_at = datetime.fromisoformat(review["reviewed_at"])
        except ValueError as exc:
            raise ValueError(f"{ident}: nieprawidłowa data przeglądu.") from exc
        if reviewed_at.utcoffset() is None:
            raise ValueError(f"{ident}: data przeglądu musi zawierać strefę czasową.")
        if review["status"] == "approved":
            if review.get("category") not in CATEGORIES or review.get("base_priority") not in PRIORITIES:
                raise ValueError(f"{ident}: wymagane zatwierdzone etykiety.")
            corrected = (review["category"], review["base_priority"]) != labels
            if corrected and not nonempty(review.get("notes")):
                raise ValueError(f"{ident}: korekta etykiety wymaga uzasadnienia.")
        elif not nonempty(review.get("notes")):
            raise ValueError(f"{ident}: wykluczenie wymaga uzasadnienia.")
    counts = Counter(item["proposed_category"] for item in examples)
    if any(counts[label] != 10 for label in CATEGORIES):
        raise ValueError("W próbce musi być po 10 propozycji każdej kategorii.")
    return examples


def select_labels(examples, mode):
    if mode not in ("proposed", "reviewed"):
        raise ValueError("Nieznany tryb etykiet.")
    if mode == "reviewed" and any(item["review"]["status"] == "pending" for item in examples):
        raise ValueError("Najpierw zakończ ręczny przegląd wszystkich rekordów (approved/excluded).")
    selected = []
    for item in examples:
        if item["review"]["status"] == "excluded":
            continue
        selected.append({
            "id": item["id"], "group_id": item["group_id"], "text": item["text"],
            "category": item["proposed_category"] if mode == "proposed" else item["review"]["category"],
            "base_priority": item["proposed_base_priority"] if mode == "proposed" else item["review"]["base_priority"],
        })
    if len({item["group_id"] for item in selected}) < 2:
        raise ValueError("Do oceny potrzebne są co najmniej dwie niezależne grupy.")
    return selected


def majority(labels):
    # Counter zachowuje kolejność sąsiadów: remis wygrywa najbliższa etykieta.
    return Counter(labels).most_common(1)[0][0]


def classification_metrics(expected, predicted, labels):
    if not expected or len(expected) != len(predicted):
        raise ValueError("Metryki wymagają niepustych, równie długich list etykiet.")
    if any(label not in labels for label in [*expected, *predicted]):
        raise ValueError("Metryki zawierają nieznaną etykietę.")
    matrix = [[sum(a == row and b == column for a, b in zip(expected, predicted))
               for column in labels] for row in labels]
    per_class = {}
    for index, label in enumerate(labels):
        tp = matrix[index][index]
        support = sum(matrix[index])
        predicted_count = sum(row[index] for row in matrix)
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = dict(precision=precision, recall=recall, f1=f1, support=support)
    return {
        "accuracy": sum(a == b for a, b in zip(expected, predicted)) / len(expected),
        "macro_f1": sum(item["f1"] for item in per_class.values()) / len(labels),
        "labels": list(labels), "confusion_matrix": matrix, "per_class": per_class,
    }


def evaluate_vectors(examples, vectors, k=3):
    import numpy as np

    if k < 1:
        raise ValueError("k musi być dodatnie.")
    vectors = np.asarray(vectors, dtype=float)
    if vectors.ndim != 2 or len(vectors) != len(examples) or not np.isfinite(vectors).all():
        raise ValueError("Nieprawidłowa macierz embeddingów.")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Embedding nie może być zerowy.")
    similarities = (vectors / norms) @ (vectors / norms).T
    rows = []
    for index, item in enumerate(examples):
        candidates = [i for i, other in enumerate(examples) if other["group_id"] != item["group_id"]]
        nearest = sorted(candidates, key=lambda i: (-float(similarities[index, i]), examples[i]["id"]))[:k]
        if len(nearest) != k:
            raise ValueError(f"{item['id']}: za mało niezależnych referencji dla k={k}.")
        rows.append({
            "id": item["id"], "group_id": item["group_id"],
            "expected_category": item["category"],
            "predicted_category": majority([examples[i]["category"] for i in nearest]),
            "expected_base_priority": item["base_priority"],
            "predicted_base_priority": majority([examples[i]["base_priority"] for i in nearest]),
            "neighbors": [{"id": examples[i]["id"], "group_id": examples[i]["group_id"],
                           "category": examples[i]["category"], "base_priority": examples[i]["base_priority"],
                           "cosine_similarity": float(similarities[index, i])} for i in nearest],
        })
    return rows


def git_state():
    def git(*args):
        return subprocess.run(["git", *args], cwd=BACKEND_ROOT.parent, capture_output=True,
                              text=True, check=True, creationflags=0x08000000 if sys.platform == "win32" else 0).stdout.strip()
    try:
        return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def render_report(report):
    lines = ["# Wstępna diagnostyka polskiego MiniLM", "",
             f"Tryb etykiet: **{report['labels_mode']}**. Rekordy: {report['count']}; grupy: {report['groups']}.", "",
             "To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje generatora nie są etykietami zatwierdzonymi przez autora.",
             "Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.", "",
             f"Model: `{MODEL_ID}`; snapshot: `{report['model_revision']}`.",
             f"SHA-256 danych: `{report['dataset_sha256']}`.",
             "Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.",
             "Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; pokrycie 100%.", "",
             "| Zadanie | Accuracy | Macro-F1 |", "|---|---:|---:|"]
    for key, label in (("category", "Kategoria"), ("base_priority", "Priorytet bazowy")):
        metric = report["metrics"][key]
        lines.append(f"| {label} | {metric['accuracy']:.1%} | {metric['macro_f1']:.3f} |")
    baseline = report["fixed_medium_baseline"]
    lines += [f"| Punkt odniesienia: zawsze medium | {baseline['accuracy']:.1%} | {baseline['macro_f1']:.3f} |", "",
              "Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.",
              "Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.", "",
              f"Tokeny z tokenami specjalnymi: {report['tokens']['min']}–{report['tokens']['max']} (limit {report['tokens']['limit']}).",
              f"Tokeny nieznane [UNK]: {report['tokens']['unknown_count']}; udział {report['tokens']['unknown_fraction']:.2%}.",
              "Brak [UNK] nie dowodzi dobrej reprezentacji języka polskiego.", "",
              f"Ładowanie modelu: {report['timings_seconds']['model_load']:.2f} s; embeddingi: {report['timings_seconds']['embedding_batch']:.2f} s.",
              "Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu."]
    for key, title in (("category", "Kategorie"), ("base_priority", "Priorytety bazowe")):
        metric = report["metrics"][key]
        lines += ["", f"## {title}: macierz pomyłek", "", "Wiersz: oczekiwana etykieta; kolumna: przewidywana.", "",
                  "| Etykieta | " + " | ".join(metric["labels"]) + " |",
                  "|---|" + "---:|" * len(metric["labels"])]
        for label, row in zip(metric["labels"], metric["confusion_matrix"]):
            lines.append(f"| {label} | " + " | ".join(map(str, row)) + " |")
    lines += ["", "## Błędy do obejrzenia", "",
              "Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.", "",
              "| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |",
              "|---|---|---|---|"]
    for row in report["predictions"]:
        if row["expected_category"] != row["predicted_category"] or row["expected_base_priority"] != row["predicted_base_priority"]:
            neighbor = row["neighbors"][0]
            lines.append(f"| {row['id']} | {row['expected_category']} → {row['predicted_category']} | "
                         f"{row['expected_base_priority']} → {row['predicted_base_priority']} | "
                         f"{neighbor['id']} ({neighbor['cosine_similarity']:.3f}) |")
    lines += ["", "Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.",
              "Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.",
              "Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_DATASET.parent / "results")
    parser.add_argument("--labels", choices=("proposed", "reviewed"), default="proposed")
    parser.add_argument("--revision", help="Opcjonalny identyfikator snapshotu Hugging Face.")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        data_bytes = args.dataset.read_bytes()
        dataset = json.loads(data_bytes)
        examples = validate_dataset(dataset)
        selected = select_labels(examples, args.labels)
        print(f"Format poprawny: {len(examples)} rekordow, {len({i['group_id'] for i in examples})} grup; "
              f"zatwierdzonych: {sum(i['review']['status'] == 'approved' for i in examples)}.")
        if args.validate_only:
            return
        print(f"Diagnostyka eksploracyjna, tryb etykiet: {args.labels}. Baza aplikacji nie jest uzywana.", flush=True)
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer

        started = perf_counter()
        snapshot = snapshot_download(MODEL_ID, revision=args.revision, local_files_only=not args.allow_download)
        model = SentenceTransformer(snapshot, device="cpu")
        loaded = perf_counter()
        texts = [item["text"] for item in selected]
        tokens = [model.tokenizer.encode(text, add_special_tokens=True, truncation=False) for text in texts]
        token_limit = min(256, model.max_seq_length)
        if any(len(item) > token_limit for item in tokens):
            raise ValueError(f"Co najmniej jeden opis przekracza limit {token_limit} tokenów; nie obcinamy tekstu.")
        encoded_at = perf_counter()
        vectors = model.encode(texts, batch_size=16, normalize_embeddings=True, show_progress_bar=False)
        encoded = perf_counter()
        rows = evaluate_vectors(selected, vectors)
        unknown_count = sum(token == model.tokenizer.unk_token_id for row in tokens for token in row)
        total_tokens = sum(map(len, tokens))
        report = {
            "dataset_id": dataset["dataset_id"], "dataset_sha256": hashlib.sha256(data_bytes).hexdigest(),
            "evaluation_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "generated_at": datetime.now(timezone.utc).isoformat(), "labels_mode": args.labels,
            "human_approved_count": sum(i["review"]["status"] == "approved" for i in examples),
            "count": len(selected), "groups": len({i["group_id"] for i in selected}),
            "model_id": MODEL_ID, "model_revision": Path(snapshot).name,
            "parameters": {"k": 3, "similarity": "cosine", "evaluation": "leave_one_group_out", "device": "cpu",
                           "confidence_threshold": None, "coverage": 1.0, "tie_break": "nearest_then_id"},
            "label_counts": {key: dict(Counter(i[key] for i in selected)) for key in ("category", "base_priority")},
            "git": git_state(), "python": platform.python_version(), "platform": platform.platform(),
            "packages": {name: version(name) for name in ("sentence-transformers", "transformers", "torch", "numpy", "huggingface-hub")},
            "tokens": {"min": min(map(len, tokens)), "max": max(map(len, tokens)), "limit": token_limit,
                       "unknown_count": unknown_count, "unknown_fraction": unknown_count / total_tokens},
            "timings_seconds": {"model_load": loaded - started, "embedding_batch": encoded - encoded_at},
            "metrics": {
                "category": classification_metrics([r["expected_category"] for r in rows], [r["predicted_category"] for r in rows], CATEGORIES),
                "base_priority": classification_metrics([r["expected_base_priority"] for r in rows], [r["predicted_base_priority"] for r in rows], PRIORITIES),
            },
            "fixed_medium_baseline": classification_metrics(
                [r["expected_base_priority"] for r in rows], ["medium"] * len(rows), PRIORITIES
            ),
            "predictions": rows,
        }
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.output / "report.md").write_text(render_report(report), encoding="utf-8")
        print(f"Zapisano {args.output / 'report.md'}")
        for key, metric in report["metrics"].items():
            print(f"{key}: accuracy={metric['accuracy']:.3f}, macro-F1={metric['macro_f1']:.3f}")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Blad pilotazu: {exc}\n")


if __name__ == "__main__":
    main()
