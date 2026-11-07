"""Proste metody priorytetu; dobór tylko na zatwierdzonych referencjach."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from scripts.evaluate_pilot import (
    BACKEND_ROOT, MODEL_ID, PRIORITIES, classification_metrics, evaluate_vectors,
    git_state, select_labels, summarize_predictions, validate_dataset,
)

PILOT = BACKEND_ROOT / "data/pilot"
REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
SEED = 20261107
BASELINE = {"k": 3, "weights": "uniform"}
# Siatka ustalona przed doborem parametrów; k=1 nie wymaga dwóch wag.
CONFIGS = [{"k": k, "weights": weights} for k in (1, 3, 5, 7, 9, 15)
           for weights in (("uniform",) if k == 1 else ("uniform", "distance"))]
CONFIGS += [{"method": method, "C": strength} for method in ("embedding_logistic", "tfidf_logistic")
            for strength in (.1, 1, 10, 100)]


def config_name(config):
    if config.get("method", "knn") == "knn":
        return f"k={config['k']}, {config['weights']}"
    return f"{config['method']}, C={config['C']}"


def vote(neighbors, weights):
    """Sąsiedzi w kolejności odległości/ID; remis wygrywa najbliższa etykieta."""
    if weights not in ("uniform", "distance") or not neighbors:
        raise ValueError("Nieprawidłowe głosowanie KNN.")
    if weights == "uniform":
        return Counter(label for label, _ in neighbors).most_common(1)[0][0]
    # Przy dokładnym dopasowaniu dalsi sąsiedzi nie głosują.
    exact = [(label, distance) for label, distance in neighbors if distance <= 1e-12]
    if exact:
        return vote(exact, "uniform")
    scores = {}
    for label, distance in neighbors:
        scores[label] = scores.get(label, 0.0) + 1.0 / distance
    return max(scores, key=scores.get)


def predict(examples, similarities, train, queries, config, vectors=None):
    if config.get("method", "knn") != "knn":
        return predict_linear(examples, train, list(queries), config, vectors)
    rows = []
    for index in queries:
        item = examples[index]
        candidates = [i for i in train if examples[i]["reference_eligible"]
                      and examples[i]["group_id"] != item["group_id"]]
        nearest = sorted(candidates, key=lambda i: (-float(similarities[index, i]), examples[i]["id"]))[:config["k"]]
        if len(nearest) != config["k"]:
            raise ValueError("Za mało niezależnych referencji.")
        neighbors = [(examples[i]["base_priority"], max(0.0, 1.0 - float(similarities[index, i])))
                     for i in nearest]
        rows.append({"id": item["id"], "group_id": item["group_id"],
                     "expected": item["base_priority"], "predicted": vote(neighbors, config["weights"]),
                     "neighbor_ids": [examples[i]["id"] for i in nearest]})
    return rows


def predict_linear(examples, train, queries, config, vectors):
    predictions = {}
    training_groups = {examples[i]["group_id"] for i in train if examples[i]["reference_eligible"]}
    buckets = {}
    for i in queries:
        group = examples[i]["group_id"]
        buckets.setdefault(group if group in training_groups else None, []).append(i)
    for group, query in buckets.items():
        eligible = [i for i in train if examples[i]["reference_eligible"] and examples[i]["group_id"] != group]
        if config["method"] == "embedding_logistic":
            features, query_features = vectors[eligible], vectors[query]
        elif config["method"] == "tfidf_logistic":
            # Słownik i IDF uczymy wyłącznie na bieżących referencjach, nigdy na zapytaniach.
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
            features = vectorizer.fit_transform([examples[i]["text"] for i in eligible])
            query_features = vectorizer.transform([examples[i]["text"] for i in query])
        else:
            raise ValueError("Nieznana metoda klasyfikacji.")
        classifier = LogisticRegression(C=config["C"], max_iter=2000, random_state=SEED)
        classifier.fit(features, [examples[i]["base_priority"] for i in eligible])
        predictions.update(zip(query, classifier.predict(query_features)))
    return [{"id": examples[i]["id"], "group_id": examples[i]["group_id"],
             "expected": examples[i]["base_priority"], "predicted": str(predictions[i]),
             "neighbor_ids": []} for i in queries]


def metrics(rows):
    scored = [row for row in rows if row["expected"] is not None]
    if not scored:
        return {"scored": 0, "unscored": len(rows), "classification": None}
    result = classification_metrics([row["expected"] for row in scored],
                                    [row["predicted"] for row in scored], PRIORITIES)
    urgent = [row for row in scored if row["expected"] in ("high", "critical")]
    # Operacyjnie groźne zaniżenie: high/critical jako low/medium.
    missed = sum(row["predicted"] in ("low", "medium") for row in urgent)
    return {"scored": len(scored), "unscored": len(rows) - len(scored), "classification": result,
            "urgent_count": len(urgent), "urgent_predicted_low_or_medium": missed,
            "urgent_detection_recall": (len(urgent) - missed) / len(urgent) if urgent else None,
            "critical_underestimated": sum(row["expected"] == "critical" and row["predicted"] != "critical"
                                          for row in scored)}


def folds(examples, indices, count, seed):
    splitter = StratifiedGroupKFold(n_splits=count, shuffle=True, random_state=seed)
    labels = [examples[i]["base_priority"] for i in indices]
    groups = [examples[i]["group_id"] for i in indices]
    return [([indices[i] for i in train], [indices[i] for i in query])
            for train, query in splitter.split(np.zeros(len(indices)), labels, groups)]


def select_config(examples, similarities, splits, vectors=None):
    results = []
    for config in CONFIGS:
        rows = [row for train, query in splits
                for row in predict(examples, similarities, train, query, config, vectors)]
        results.append({"config": config, "metrics": metrics(rows)})
    # Cel: macro-F1, następnie accuracy, następnie mniej groźnych zaniżeń.
    # Ostateczny remis rozstrzyga stała kolejność siatki.
    def score(result):
        metric = result["metrics"]
        return (metric["classification"]["macro_f1"], metric["classification"]["accuracy"],
                -metric["urgent_predicted_low_or_medium"])
    return max(results, key=score)["config"], results


def experiment(examples, vectors):
    vectors = np.asarray(vectors, dtype=float)
    if vectors.ndim != 2 or len(vectors) != len(examples) or not np.isfinite(vectors).all():
        raise ValueError("Nieprawidłowe embeddingi.")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("Zerowy embedding.")
    similarities = np.clip((vectors / norms) @ (vectors / norms).T, -1.0, 1.0)
    references = [i for i, item in enumerate(examples) if item["reference_eligible"]]
    weak = [i for i, item in enumerate(examples) if not item["reference_eligible"]]
    outer_splits = folds(examples, references, 5, SEED)
    nested_rows, baseline_rows, fold_reports = [], [], []
    for number, (train, query) in enumerate(outer_splits):
        config, _ = select_config(examples, similarities, folds(examples, train, 4, SEED + number + 1), vectors)
        selected = predict(examples, similarities, train, query, config, vectors)
        baseline = predict(examples, similarities, train, query, BASELINE)
        nested_rows.extend(selected)
        baseline_rows.extend(baseline)
        fold_reports.append({"fold": number + 1, "selected_config": config,
                             "train_ids": [examples[i]["id"] for i in train],
                             "query_ids": [examples[i]["id"] for i in query],
                             "baseline": metrics(baseline), "selected": metrics(selected)})
    config, grid = select_config(examples, similarities, outer_splits, vectors)
    historical = evaluate_vectors(examples, vectors, k=3)
    reproduced = predict(examples, similarities, references, range(len(examples)), BASELINE)
    if [row["predicted_base_priority"] for row in historical] != [row["predicted"] for row in reproduced]:
        raise ValueError("Nie odtworzono historycznego głosowania KNN.")
    diagnostic = []
    for candidate in CONFIGS:
        rows = predict(examples, similarities, references, range(len(examples)), candidate, vectors)
        diagnostic.append({"config": candidate, "metrics": metrics(rows)})
    # Parametry wybrane bez etykiet słabych opisów; null nadal nie jest oceniany.
    weak_baseline = predict(examples, similarities, references, weak, BASELINE)
    weak_selected = predict(examples, similarities, references, weak, config, vectors)
    full_selected = predict(examples, similarities, references, range(len(examples)), config, vectors)
    baseline_by_id = {row["id"]: row for row in reproduced}
    changed = [dict(row, baseline=baseline_by_id[row["id"]]["predicted"]) for row in full_selected
               if row["predicted"] != baseline_by_id[row["id"]]["predicted"]]
    return {"selected_config": config, "reference_count": len(references), "weak_count": len(weak),
            "nested_cv": {"baseline": metrics(baseline_rows), "selected": metrics(nested_rows),
                          "folds": fold_reports, "baseline_predictions": baseline_rows,
                          "selected_predictions": nested_rows},
            "selection_cv_grid": grid,
            "historical_protocol_diagnostic_grid": diagnostic,
            "historical_baseline": metrics(reproduced),
            "historical_selected": metrics(full_selected),
            "historical_category": summarize_predictions(historical)["metrics"]["category"],
            "weak_probe": {"baseline": metrics(weak_baseline), "selected": metrics(weak_selected),
                           "predictions": weak_selected}, "changed_predictions": changed}


def verify_historical_inputs(examples, snapshot_bytes, expected_sha256):
    # Po pomiarze dodano komentarze o partiach; Git na Windows zmienia też LF/CRLF.
    # Weryfikujemy oryginalny snapshot oraz wszystkie faktyczne wejścia KNN.
    lf = snapshot_bytes.replace(b"\r\n", b"\n")
    hashes = {hashlib.sha256(value).hexdigest() for value in (snapshot_bytes, lf, lf.replace(b"\n", b"\r\n"))}
    if expected_sha256 not in hashes:
        raise ValueError("Snapshot nie odpowiada historycznemu pomiarowi.")
    previous = select_labels(validate_dataset(json.loads(snapshot_bytes)), "proposed")
    if examples != previous:
        raise ValueError("Wejścia KNN zmieniły się od historycznego pomiaru.")


def render(report):
    lines = ["# Proste metody klasyfikacji priorytetu", "", f"Pomiar: {report['generated_at']}.", "",
             "Język główny eksperymentu: angielski (EN); PL stanowi porównanie pomocnicze.", "",
             "Model MiniLM i teksty bez zmian. Badamy wyłącznie priorytet bazowy; kategoria pozostaje k=3.",
             "Bez checkboxa, ręcznych priorytetów i reguł eskalacji. Baza aplikacji nie jest używana.", "",
             "Siatka: k=1,3,5,7,9,15; głosowanie zwykłe lub odwrotnością odległości (dla k=1 jeden wariant).",
             "Dodatkowo regresja logistyczna: embeddingi MiniLM albo TF-IDF słów (1–2 gramów, sublinear_tf); C=0.1,1,10,100.",
             "TF-IDF uczy słownik i IDF wyłącznie na treningu danego foldu; regresja nie używa kategorii ani checkboxa.",
             "Wybór: macro-F1, potem accuracy, potem mniej high/critical przewidzianych jako low/medium.",
             "120 zatwierdzonych referencji: zewnętrzne 5 foldów, wewnętrzne 4; grupy incydentów rozdzielone.",
             "Zewnętrzne zapytania nie uczestniczą w doborze parametrów ani referencjach swojego foldu.",
             "50 słabych opisów nie uczestniczy w doborze. Oceniane są tylko 10 ustalalnych priorytetów; 40 pomijamy.",
             "Nowe etykiety są pending. Ta partia była wcześniej oglądana i nie jest niezależnym testem końcowym.", ""]
    for language, result in report["languages"].items():
        config = result["selected_config"]
        lines += [f"## {language.upper()}", "", f"Wybór z 5-fold CV całej referencji: {config_name(config)}.", "",
                  "### Ocena doboru parametrów — zagnieżdżona walidacja grupowa", "",
                  "| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium | Critical zaniżone |", "|---|---:|---:|---:|---:|"]
        for name, metric in (("Obecne k=3", result["nested_cv"]["baseline"]),
                             ("Dobór w wewnętrznej walidacji", result["nested_cv"]["selected"])):
            value = metric["classification"]
            lines.append(f"| {name} | {value['accuracy']:.1%} | {value['macro_f1']:.3f} | "
                         f"{metric['urgent_predicted_low_or_medium']}/{metric['urgent_count']} | {metric['critical_underestimated']} |")
        lines += ["", "Parametry mogą różnić się między foldami. To ocena procedury doboru, nie jednej finalnej konfiguracji.", "",
                  "### Odtworzenie protokołu historycznego — diagnostyka", "",
                  "| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium |", "|---|---:|---:|---:|"]
        for variant in result["historical_protocol_diagnostic_grid"]:
            cfg, metric = variant["config"], variant["metrics"]
            value = metric["classification"]
            lines.append(f"| {config_name(cfg)} | {value['accuracy']:.1%} | {value['macro_f1']:.3f} | "
                         f"{metric['urgent_predicted_low_or_medium']}/{metric['urgent_count']} |")
        lines += ["", "130 ocenionych priorytetów ze 170 opisów. Własna grupa wykluczona; słabe opisy nie są referencjami.",
                  "Siatka pokazuje wyniki na znanym pilotażu; najlepszy wiersz nie stanowi niezależnego potwierdzenia poprawy.", "",
                  "### Wybrany wariant na 50 słabych opisach", "",
                  "| Wariant | Poprawne / ocenione | Macro-F1 |", "|---|---:|---:|"]
        for name in ("baseline", "selected"):
            metric = result["weak_probe"][name]
            value = metric["classification"]
            lines.append(f"| {name} | {round(value['accuracy'] * metric['scored'])}/{metric['scored']} | {value['macro_f1']:.3f} |")
        lines += ["", "40 opisów bez ustalalnego priorytetu nadal otrzymuje wymuszoną odpowiedź; nie liczymy tego jako sukces.", ""]
    lines += ["## Wniosek wdrożeniowy", "", report["deployment_decision"], "",
              "Pełne metryki klas, podziały foldów, przewidywania i zmienione decyzje: [report.json](report.json).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PILOT / "priority-methods")
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    from huggingface_hub import snapshot_download
    from sentence_transformers import SentenceTransformer

    snapshot = snapshot_download(MODEL_ID, revision=REVISION, local_files_only=not args.allow_download)
    model = SentenceTransformer(snapshot, device="cpu")
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "model_id": MODEL_ID,
              "primary_language": "en",
              "model_revision": REVISION, "seed": SEED, "configs": CONFIGS,
              "selection_metric": ["macro_f1", "accuracy", "fewer_urgent_predicted_low_or_medium"],
              "outer_folds": 5, "inner_folds": 4, "git": git_state(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "packages": {name: version(name) for name in ("numpy", "scikit-learn", "sentence-transformers", "torch")},
              "datasets": {}, "languages": {}}
    for language, filename in (("en", "tickets.en.json"), ("pl", "tickets.json")):
        path = PILOT / filename
        payload = path.read_bytes()
        raw = validate_dataset(json.loads(payload))
        references = [item for item in raw if item.get("reference_eligible", True)]
        # Zatwierdzone etykiety dla referencji, proposed jedynie dla pending zapytań.
        approved = {row["id"]: row for row in select_labels(references, "reviewed")}
        examples = [approved.get(row["id"], row) for row in select_labels(raw, "proposed")]
        if any(len(model.tokenizer.encode(row["text"], truncation=False)) > min(256, model.max_seq_length)
               for row in examples):
            raise ValueError("Tekst przekracza limit tokenów; nie obcinamy opisów.")
        vectors = model.encode([row["text"] for row in examples], batch_size=16,
                               normalize_embeddings=True, show_progress_bar=False)
        report["datasets"][language] = {"path": str(path.relative_to(BACKEND_ROOT.parent)),
                                        "sha256": hashlib.sha256(payload).hexdigest(),
                                        "reference_labels": "reviewed", "weak_labels": "proposed"}
        result = experiment(examples, vectors)
        # Odtworzenie istniejącego raportu chroni porównanie z poprzednimi wynikami.
        historical = json.loads((PILOT / "comparison" / language / "report.json").read_text(encoding="utf-8"))
        snapshot_bytes = (PILOT / "snapshots" / f"tickets.{language}.170.v3.json").read_bytes()
        verify_historical_inputs(examples, snapshot_bytes, historical["dataset_sha256"])
        report["datasets"][language]["historical_snapshot_sha256"] = historical["dataset_sha256"]
        if (result["historical_baseline"]["classification"] != historical["metrics"]["base_priority"]
                or result["historical_category"] != historical["metrics"]["category"]):
            raise ValueError("Historyczne metryki nie zostały odtworzone.")
        report["languages"][language] = result
        print(language, "selected", result["selected_config"], flush=True)
        for key in ("baseline", "selected"):
            metric = result["nested_cv"][key]
            print(f"nested {key}: accuracy={metric['classification']['accuracy']:.3f}, "
                  f"macro-F1={metric['classification']['macro_f1']:.3f}, "
                  f"urgent underestimated={metric['urgent_predicted_low_or_medium']}/{metric['urgent_count']}", flush=True)
    english = report["languages"]["en"]
    before, after = english["nested_cv"]["baseline"], english["nested_cv"]["selected"]
    critical = []
    for metric in (before, after):
        value = metric["classification"]["per_class"]["critical"]
        critical.append(f"{round(value['recall'] * value['support'])}/{value['support']}")
    weak = []
    for key in ("baseline", "selected"):
        metric = english["weak_probe"][key]
        weak.append(f"{round(metric['classification']['accuracy'] * metric['scored'])}/{metric['scored']}")
    report["deployment_decision"] = (
        f"Dla EN kandydatem jest {config_name(english['selected_config'])}. "
        f"Zagnieżdżona walidacja: accuracy {before['classification']['accuracy']:.1%} → "
        f"{after['classification']['accuracy']:.1%}; pilne jako low/medium "
        f"{before['urgent_predicted_low_or_medium']}/{before['urgent_count']} → "
        f"{after['urgent_predicted_low_or_medium']}/{after['urgent_count']}. "
        "To obiecujący wynik na syntetycznych opisach. Rozpoznawanie dokładnie critical: "
        f"{critical[0]} → {critical[1]}; na ocenialnych słabych opisach EN: {weak[0]} → {weak[1]}. "
        "Eksperyment nie przełącza automatycznie aplikacji: nowa metoda wymaga osobnego treningu na "
        "zatwierdzonych referencjach i dalszej weryfikacji na niezależnych opisach. "
        "Stare raporty i obecne ustawienia klasyfikacji kategorii pozostają punktem odniesienia.")
    args.output.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    run = args.output / "runs" / (hashlib.sha256(payload.encode()).hexdigest()[:16] + ".json")
    run.parent.mkdir(exist_ok=True)
    run.write_text(payload, encoding="utf-8", newline="\n")
    (args.output / "report.json").write_text(payload, encoding="utf-8", newline="\n")
    (args.output / "report.md").write_text(render(report), encoding="utf-8", newline="\n")
    print("Raport:", args.output / "report.md")


if __name__ == "__main__":
    main()
