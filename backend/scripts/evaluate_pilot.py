"""Diagnostyka pilotażu PL lub EN, bez połączenia z bazą aplikacji."""
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
    if dataset.get("purpose") != "exploratory_pilot_only" or dataset.get("language") not in ("pl", "en"):
        raise ValueError("Oczekiwano próbki pilotażowej w języku pl lub en.")
    if not nonempty(dataset.get("dataset_id")):
        raise ValueError("Brak identyfikatora zbioru.")
    provenance = dataset.get("provenance", {})
    if not isinstance(provenance, dict) or provenance.get("method") != "llm_assisted_synthetic":
        raise ValueError("Brak informacji o syntetycznym pochodzeniu danych.")
    examples = dataset.get("examples")
    expected_count = dataset.get("expected_count", 40)
    if type(expected_count) is not int or expected_count < 4:
        raise ValueError("Liczebność pilotażu musi być liczbą całkowitą nie mniejszą niż cztery.")
    reference_count = dataset.get("reference_count", expected_count)
    if (type(reference_count) is not int or reference_count < 4
            or reference_count > expected_count or reference_count % len(CATEGORIES)):
        raise ValueError("Liczebność referencji musi być wielokrotnością czterech i nie przekraczać zbioru.")
    if not isinstance(examples, list) or len(examples) != expected_count:
        raise ValueError(f"Pilotaż musi zawierać dokładnie {expected_count} rekordów.")
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
        eligible = item.get("reference_eligible", True)
        if type(eligible) is not bool:
            raise ValueError(f"{ident}: reference_eligible musi być wartością logiczną.")
        weak = not eligible and item.get("description_quality") == "weak"
        if not eligible and not weak:
            raise ValueError(f"{ident}: przykład poza referencją wymaga oznaczenia weak.")
        category_ok = item.get("proposed_category") in CATEGORIES or (weak and item.get("proposed_category") is None)
        priority_ok = item.get("proposed_base_priority") in PRIORITIES or (weak and item.get("proposed_base_priority") is None)
        if not category_ok or not priority_ok:
            raise ValueError(f"{ident}: nieznana propozycja etykiety.")
        if type(item.get("work_blocked")) is not bool and not (weak and item.get("work_blocked") is None):
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
            category_ok = review.get("category") in CATEGORIES or (weak and "category" in review and review["category"] is None)
            priority_ok = review.get("base_priority") in PRIORITIES or (weak and "base_priority" in review and review["base_priority"] is None)
            if not category_ok or not priority_ok:
                raise ValueError(f"{ident}: wymagane zatwierdzone etykiety.")
            corrected = (review["category"], review["base_priority"]) != labels
            if corrected and not nonempty(review.get("notes")):
                raise ValueError(f"{ident}: korekta etykiety wymaga uzasadnienia.")
        elif not nonempty(review.get("notes")):
            raise ValueError(f"{ident}: wykluczenie wymaga uzasadnienia.")
    references = [item for item in examples if item.get("reference_eligible", True)]
    if len(references) != reference_count:
        raise ValueError(f"Oczekiwano {reference_count} przykładów referencyjnych.")
    counts = Counter(item["proposed_category"] for item in references)
    per_category = reference_count // len(CATEGORIES)
    if any(counts[label] != per_category for label in CATEGORIES):
        raise ValueError(f"W próbce musi być po {per_category} propozycji każdej kategorii.")
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
            "reference_eligible": item.get("reference_eligible", True),
            "cohort": "weak" if item.get("description_quality") == "weak" else "reference",
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
        candidates = [i for i, other in enumerate(examples)
                      if other.get("reference_eligible", True) and other["group_id"] != item["group_id"]]
        nearest = sorted(candidates, key=lambda i: (-float(similarities[index, i]), examples[i]["id"]))[:k]
        if len(nearest) != k:
            raise ValueError(f"{item['id']}: za mało niezależnych referencji dla k={k}.")
        rows.append({
            "id": item["id"], "group_id": item["group_id"],
            "reference_eligible": item.get("reference_eligible", True),
            "cohort": item.get("cohort", "reference"),
            "expected_category": item["category"],
            "predicted_category": majority([examples[i]["category"] for i in nearest]),
            "expected_base_priority": item["base_priority"],
            "predicted_base_priority": majority([examples[i]["base_priority"] for i in nearest]),
            "neighbors": [{"id": examples[i]["id"], "group_id": examples[i]["group_id"],
                           "category": examples[i]["category"], "base_priority": examples[i]["base_priority"],
                           "cosine_similarity": float(similarities[index, i])} for i in nearest],
        })
    return rows


def summarize_predictions(rows):
    metrics, scoring = {}, {}
    for task, labels in (("category", CATEGORIES), ("base_priority", PRIORITIES)):
        scored = [row for row in rows if row[f"expected_{task}"] is not None]
        metrics[task] = (classification_metrics([row[f"expected_{task}"] for row in scored],
                                               [row[f"predicted_{task}"] for row in scored], labels)
                         if scored else None)
        scoring[task] = {"scored": len(scored), "unscored": len(rows) - len(scored),
                         "coverage": len(scored) / len(rows) if rows else 0.0}
    priority_rows = [row for row in rows if row["expected_base_priority"] is not None]
    baseline = (classification_metrics([row["expected_base_priority"] for row in priority_rows],
                                       ["medium"] * len(priority_rows), PRIORITIES)
                if priority_rows else None)
    unlabelled_category = [row for row in rows if row["expected_category"] is None]
    unlabelled_priority = [row for row in rows if row["expected_base_priority"] is None]
    return {"count": len(rows), "metrics": metrics, "scoring": scoring, "fixed_medium_baseline": baseline,
            "insufficient_information": {
                "category": {"count": len(unlabelled_category),
                             "forced_predictions": sum(row["predicted_category"] in CATEGORIES for row in unlabelled_category)},
                "base_priority": {"count": len(unlabelled_priority),
                                  "forced_predictions": sum(row["predicted_base_priority"] in PRIORITIES for row in unlabelled_priority)}}}


def git_state():
    def git(*args):
        return subprocess.run(["git", *args], cwd=BACKEND_ROOT.parent, capture_output=True,
                              text=True, check=True, creationflags=0x08000000 if sys.platform == "win32" else 0).stdout.strip()
    try:
        return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def render_report(report):
    language = report.get("language", "pl")
    lines = [f"# Wstępna diagnostyka MiniLM — język: {language}", "",
             f"Zbiór: `{report['dataset_id']}`.", "",
             f"Tryb etykiet: **{report['labels_mode']}**. Rekordy: {report['count']}; grupy: {report['groups']}.", "",
             f"Etykiety zatwierdzone przez użytkownika: {report['human_approved_count']}/{report['count']}.", "",
             "To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje nowych etykiet wymagają osobnego przeglądu.",
             "Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.", "",
             f"Model: `{MODEL_ID}`; snapshot: `{report['model_revision']}`.",
             f"SHA-256 danych: `{report['dataset_sha256']}`.",
             "Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.",
             "Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; model odpowiada na 100% opisów.", "",
             "Przykłady bez możliwej do ustalenia etykiety nie wchodzą do mianownika accuracy ani F1; ich liczebność raportujemy jawnie.", "",
             "| Zadanie | Accuracy | Macro-F1 | Ocenione / wszystkie |", "|---|---:|---:|---:|"]
    for key, label in (("category", "Kategoria"), ("base_priority", "Priorytet bazowy")):
        metric = report["metrics"][key]
        scored = report['scoring'][key]['scored']
        lines.append(f"| {label} | {metric['accuracy']:.1%} | {metric['macro_f1']:.3f} | {scored}/{report['count']} |")
    baseline = report["fixed_medium_baseline"]
    lines += [f"| Punkt odniesienia: zawsze medium | {baseline['accuracy']:.1%} | {baseline['macro_f1']:.3f} | {report['scoring']['base_priority']['scored']}/{report['count']} |", "",
              "Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.",
              "Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.", "",
              f"Tokeny z tokenami specjalnymi: {report['tokens']['min']}–{report['tokens']['max']} (limit {report['tokens']['limit']}).",
              f"Tokeny nieznane [UNK]: {report['tokens']['unknown_count']}; udział {report['tokens']['unknown_fraction']:.2%}.",
              "Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.", "",
              f"Ładowanie modelu: {report['timings_seconds']['model_load']:.2f} s; embeddingi: {report['timings_seconds']['embedding_batch']:.2f} s.",
              "Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu."]
    lines += ["", "## Grupy jakości opisu", "",
              "| Grupa | Liczba | Accuracy kategorii | Ocenione kategorie | Accuracy priorytetu | Ocenione priorytety |",
              "|---|---:|---:|---:|---:|---:|"]
    for name, cohort in report.get("cohorts", {}).items():
        category, priority = cohort["metrics"]["category"], cohort["metrics"]["base_priority"]
        category_text = f"{category['accuracy']:.1%}" if category else "brak etykiet"
        priority_text = f"{priority['accuracy']:.1%}" if priority else "brak etykiet"
        lines.append(f"| {name} | {cohort['count']} | {category_text} | {cohort['scoring']['category']['scored']} | "
                     f"{priority_text} | {cohort['scoring']['base_priority']['scored']} |")
    lines += ["", "Słabe opisy są wyłącznie zapytaniami do stałej referencji 120; nie stają się sąsiadami innych zgłoszeń."]
    insufficient = report["insufficient_information"]
    lines += [f"Bez ustalalnej kategorii: {insufficient['category']['count']}; wymuszonych kategorii: {insufficient['category']['forced_predictions']}.",
              f"Bez ustalalnego priorytetu: {insufficient['base_priority']['count']}; wymuszonych priorytetów: {insufficient['base_priority']['forced_predictions']}.",
              "Wymuszona etykieta przy braku informacji nie jest poprawnym rozpoznaniem; pokazuje brak mechanizmu odmowy."]
    for key, title in (("category", "Kategorie"), ("base_priority", "Priorytety bazowe")):
        metric = report["metrics"][key]
        lines += ["", f"## {title}: macierz pomyłek", "", "Wiersz: oczekiwana etykieta; kolumna: przewidywana.", "",
                  "| Etykieta | " + " | ".join(metric["labels"]) + " |",
                  "|---|" + "---:|" * len(metric["labels"])]
        for label, row in zip(metric["labels"], metric["confusion_matrix"]):
            lines.append(f"| {label} | " + " | ".join(map(str, row)) + " |")
    lines += ["", "## Błędy i odpowiedzi wymagające doprecyzowania", "",
              "Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.", "",
              "None oznacza brak ustalalnej etykiety i nie jest liczone jako błąd ani sukces klasyfikacji.", "",
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


def write_report(report, output, markdown=None):
    """Dopisuje Markdown i zachowuje niezmienne JSON-y poprzednich przebiegów."""
    output = Path(output)
    runs = output / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    latest = output / "report.json"
    previous_name = None
    if latest.exists():
        previous = latest.read_bytes()
        previous_name = f"previous-{hashlib.sha256(previous).hexdigest()[:16]}.json"
        previous_path = runs / previous_name
        if not previous_path.exists():
            previous_path.write_bytes(previous)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    run_name = f"{report['count']}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}.json"
    run_path = runs / run_name
    if not run_path.exists():
        run_path.write_text(payload, encoding="utf-8", newline="\n")
    body = render_report(report) if markdown is None else markdown
    body = "\n".join("#" + line if line.startswith("#") else line for line in body.splitlines())
    section = (f"\n\n---\n\n## Pomiar {report['generated_at']} — {report['count']} zgłoszeń\n\n"
               f"Pełny zapis tego przebiegu: [JSON](runs/{run_name}).\n\n")
    if previous_name is not None:
        section += f"Zachowany poprzedni zapis JSON: [archiwum](runs/{previous_name}).\n\n"
    section += body + "\n"
    markdown_path = output / "report.md"
    if not markdown_path.exists():
        markdown_path.write_text("# Historia pomiarów pilotażu\n", encoding="utf-8", newline="\n")
    with markdown_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(section)
    latest.write_text(payload, encoding="utf-8", newline="\n")
    return run_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, help="Katalog raportów; domyślnie results dla PL, results-en dla EN obok danych.")
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
        if args.output is None:
            args.output = args.dataset.parent / ("results" if dataset["language"] == "pl" else "results-en")
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
        summary = summarize_predictions(rows)
        unknown_count = sum(token == model.tokenizer.unk_token_id for row in tokens for token in row)
        total_tokens = sum(map(len, tokens))
        report = {
            "dataset_id": dataset["dataset_id"], "dataset_sha256": hashlib.sha256(data_bytes).hexdigest(),
            "language": dataset["language"], "provenance": dataset["provenance"],
            "evaluation_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "generated_at": datetime.now(timezone.utc).isoformat(), "labels_mode": args.labels,
            "human_approved_count": sum(i["review"]["status"] == "approved" for i in examples),
            "count": len(selected), "groups": len({i["group_id"] for i in selected}),
            "model_id": MODEL_ID, "model_revision": Path(snapshot).name,
            "parameters": {"k": 3, "similarity": "cosine", "evaluation": "leave_one_group_out", "device": "cpu",
                           "confidence_threshold": None, "coverage": 1.0, "tie_break": "nearest_then_id",
                           "reference_policy": "reference_eligible_only",
                           "reference_count": sum(item["reference_eligible"] for item in selected)},
            "label_counts": {key: dict(Counter(i[key] for i in selected if i[key] is not None)) for key in ("category", "base_priority")},
            "git": git_state(), "python": platform.python_version(), "platform": platform.platform(),
            "packages": {name: version(name) for name in ("sentence-transformers", "transformers", "torch", "numpy", "huggingface-hub")},
            "tokens": {"min": min(map(len, tokens)), "max": max(map(len, tokens)), "limit": token_limit,
                       "unknown_count": unknown_count, "unknown_fraction": unknown_count / total_tokens},
            "timings_seconds": {"model_load": loaded - started, "embedding_batch": encoded - encoded_at},
            **{key: summary[key] for key in ("metrics", "scoring", "fixed_medium_baseline", "insufficient_information")},
            "cohorts": {name: summarize_predictions([row for row in rows if row["cohort"] == name])
                        for name in dict.fromkeys(row["cohort"] for row in rows)},
            "predictions": rows,
        }
        write_report(report, args.output)
        print(f"Zapisano {args.output / 'report.md'}")
        for key, metric in report["metrics"].items():
            print(f"{key}: accuracy={metric['accuracy']:.3f}, macro-F1={metric['macro_f1']:.3f}")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Blad pilotazu: {exc}\n")


if __name__ == "__main__":
    main()
