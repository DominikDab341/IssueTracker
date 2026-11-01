"""Porównuje sparowane pomiary PL/EN i dopisuje wynik do historii Markdown."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.evaluate_pilot import (
    BACKEND_ROOT, CATEGORIES, PRIORITIES, classification_metrics,
    select_labels, validate_dataset, write_report,
)

PILOT = BACKEND_ROOT / "data/pilot"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def paired_comparison(pl, en, datasets):
    for key in ("model_id", "model_revision", "evaluation_script_sha256", "parameters",
                "labels_mode", "count", "groups", "label_counts", "packages", "python", "platform"):
        if pl[key] != en[key]:
            raise ValueError(f"Niezgodne warunki porównania: {key}.")
    if (pl["language"], en["language"]) != ("pl", "en"):
        raise ValueError("Oczekiwano raportów PL i EN.")
    selected = {}
    for language, report in (("pl", pl), ("en", en)):
        path = datasets[language]
        payload = path.read_bytes()
        dataset = json.loads(payload)
        if hashlib.sha256(payload).hexdigest() != report["dataset_sha256"]:
            raise ValueError(f"Dane {language} zmieniły się od pomiaru.")
        selected[language] = {row["id"]: row for row in select_labels(validate_dataset(dataset), report["labels_mode"])}
    if selected["pl"].keys() != selected["en"].keys():
        raise ValueError("Zbiory mają różne ID.")
    raw = {language: {row["id"]: row for row in read_json(path)["examples"]}
           for language, path in datasets.items()}
    for ident in selected["pl"]:
        for field in ("group_id", "proposed_category", "proposed_base_priority", "work_blocked", "reference_eligible", "description_quality"):
            if raw["pl"][ident].get(field) != raw["en"][ident].get(field):
                raise ValueError(f"{ident}: niesparowane pole {field}.")
    english = {row["id"]: row for row in en["predictions"]}
    if set(english) != set(selected["en"]) or {row["id"] for row in pl["predictions"]} != set(selected["pl"]):
        raise ValueError("Raport nie obejmuje dokładnie wybranych przykładów.")
    paired = []
    for p in pl["predictions"]:
        e = english[p["id"]]
        for language, row in (("pl", p), ("en", e)):
            expected = selected[language][row["id"]]
            if (row["group_id"], row["expected_category"], row["expected_base_priority"]) != (
                    expected["group_id"], expected["category"], expected["base_priority"]):
                raise ValueError(f"{row['id']}: raport ma niezgodne etykiety lub grupę.")
            if any(neighbor["group_id"] == row["group_id"] for neighbor in row["neighbors"]):
                raise ValueError(f"{row['id']}: przeciek grupy incydentu do sąsiadów.")
            if any(not raw[language][neighbor["id"]].get("reference_eligible", True) for neighbor in row["neighbors"]):
                raise ValueError(f"{row['id']}: słaby opis trafił do referencji.")
        paired.append({"id": p["id"], "group_id": p["group_id"],
                       "cohort": p.get("cohort", "reference"),
                       "expected_category": p["expected_category"],
                       "category_pl": p["predicted_category"], "category_en": e["predicted_category"],
                       "expected_base_priority": p["expected_base_priority"],
                       "base_priority_pl": p["predicted_base_priority"], "base_priority_en": e["predicted_base_priority"]})
    tasks = {}
    for task, labels in (("category", CATEGORIES), ("base_priority", PRIORITIES)):
        outcomes = {key: [] for key in ("both_correct", "pl_only_correct", "en_only_correct", "both_wrong", "unscored")}
        expected = f"expected_{task}"
        for row in paired:
            if row[expected] is None:
                outcomes["unscored"].append(row["id"])
                continue
            pc, ec = row[expected] == row[f"{task}_pl"], row[expected] == row[f"{task}_en"]
            key = ("both_correct" if ec else "pl_only_correct") if pc else ("en_only_correct" if ec else "both_wrong")
            outcomes[key].append(row["id"])
        for language, report in (("pl", pl), ("en", en)):
            scored = [row for row in paired if row[expected] is not None]
            metric = classification_metrics([row[expected] for row in scored],
                                            [row[f"{task}_{language}"] for row in scored], labels)
            if metric != report["metrics"][task]:
                raise ValueError(f"Niezgodne metryki {task}/{language}.")
        tasks[task] = {"pl": pl["metrics"][task], "en": en["metrics"][task],
                       "scored_count": len(paired) - len(outcomes["unscored"]),
                       "unscored_count": len(outcomes["unscored"]),
                       "accuracy_delta_percentage_points": round((en["metrics"][task]["accuracy"] - pl["metrics"][task]["accuracy"]) * 100, 8),
                       "paired_outcomes": outcomes}
    original_ids = {row["id"] for row in read_json(PILOT / "snapshots/tickets.pl.40.v1.json")["examples"]}
    subsets = {}
    for name, rows in (("original_40", [row for row in paired if row["id"] in original_ids]),
                       ("new_80", [row for row in paired if row["id"] not in original_ids and row["cohort"] != "weak"]),
                       ("weak_50", [row for row in paired if row["cohort"] == "weak"])):
        if rows:
            subsets[name] = {"count": len(rows), "metrics": {
                task: {language: (classification_metrics([row[f"expected_{task}"] for row in rows if row[f"expected_{task}"] is not None],
                                                         [row[f"{task}_{language}"] for row in rows if row[f"expected_{task}"] is not None], labels)
                                   if any(row[f"expected_{task}"] is not None for row in rows) else None)
                       for language in ("pl", "en")}
                for task, labels in (("category", CATEGORIES), ("base_priority", PRIORITIES))},
                "scored_counts": {task: sum(row[f"expected_{task}"] is not None for row in rows)
                                  for task in ("category", "base_priority")}}
    return {"dataset_id": f"paired-pl-en-{pl['count']}", "generated_at": datetime.now(timezone.utc).isoformat(),
            "experiment": "paired_language_translation_pilot", "count": pl["count"], "groups": pl["groups"],
            "labels_mode": pl["labels_mode"],
            "human_approved_count": {language: report["human_approved_count"] for language, report in (("pl", pl), ("en", en))},
            "dataset_sha256": {"pl": pl["dataset_sha256"], "en": en["dataset_sha256"]},
            "conditions": {key: pl[key] for key in ("model_id", "model_revision", "evaluation_script_sha256", "parameters", "packages", "python", "platform")},
            "checks": {"same_ids_groups_labels_and_checkbox": True, "same_evaluation_conditions": True,
                       "source_hashes_match": True, "no_same_group_neighbors": True,
                       "no_weak_examples_in_reference": True},
            "insufficient_information": {"pl": pl.get("insufficient_information"), "en": en.get("insufficient_information")},
            "metrics": tasks, "fixed_medium_baseline": pl["fixed_medium_baseline"],
            "tokens": {"pl": pl["tokens"], "en": en["tokens"]},
            "subsets_with_full_reference_pool": subsets, "paired_predictions": paired}


def render_comparison(report, previous):
    def percent(value):
        return f"{value:.1%}".replace(".", ",")

    lines = ["# Porównanie PL/EN", "",
             f"{report['count']} tych samych przypadków; {report['groups']} grup incydentów; tryb etykiet `{report['labels_mode']}`.",
             f"Zatwierdzone etykiety: PL {report['human_approved_count']['pl']}/{report['count']}, EN {report['human_approved_count']['en']}/{report['count']}.",
             "Pozostałe nowe przykłady i tłumaczenia oczekują na ręczny przegląd.", "",
             "Accuracy i F1 pomijają przykłady bez ustalalnej etykiety. Mianowniki podajemy jawnie; przewidywania pozostają widoczne dla wszystkich opisów.", "",
             "| Zadanie | Accuracy PL | Accuracy EN | Ocenione / wszystkie | Zmiana EN − PL | Macro-F1 PL | Macro-F1 EN |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    names = (("category", "Kategoria"), ("base_priority", "Priorytet bazowy"))
    for task, label in names:
        metric = report["metrics"][task]
        lines.append(f"| {label} | {percent(metric['pl']['accuracy'])} | {percent(metric['en']['accuracy'])} | {metric['scored_count']}/{report['count']} | "
                     f"{metric['accuracy_delta_percentage_points']:+.2f} p.p. | {metric['pl']['macro_f1']:.3f} | {metric['en']['macro_f1']:.3f} |")
    lines += ["", f"Stałe medium: accuracy {percent(report['fixed_medium_baseline']['accuracy'])}; "
              f"macro-F1 {report['fixed_medium_baseline']['macro_f1']:.3f}.", ""]
    if previous:
        previous_count = previous.get("count", previous.get("conditions", {}).get("count"))
        lines += ["## Poprzedni i bieżący rozmiar próbki", "",
                  "| Zadanie | Język | Poprzednia próbka | Bieżąca próbka |", "|---|---|---:|---:|"]
        for task, label in names:
            for language in ("pl", "en"):
                lines.append(f"| {label} | {language.upper()} | {percent(previous['metrics'][task][language]['accuracy'])} "
                             f"({previous_count}) | {percent(report['metrics'][task][language]['accuracy'])} ({report['count']}) |")
        lines += ["", "Zmienił się skład ocenianych przypadków, a brakujące etykiety mają jawne mianowniki. Różnica między rozmiarami nie jest pomiarem poprawy na stałym zbiorze testowym.", ""]
    lines += ["## Podzbiory przy pełnej puli referencji bieżącego przebiegu", "",
              "Każde zgłoszenie nadal wyklucza własną grupę. Podzbiory poniżej nie uruchamiają ponownie modelu.", "",
              "| Podzbiór | Liczba | Kategoria PL | Kategoria EN | Ocenione kategorie | Priorytet PL | Priorytet EN | Ocenione priorytety |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, subset in report["subsets_with_full_reference_pool"].items():
        metric = subset["metrics"]
        lines.append(f"| {name} | {subset['count']} | {percent(metric['category']['pl']['accuracy'])} | "
                     f"{percent(metric['category']['en']['accuracy'])} | {subset['scored_counts']['category']} | {percent(metric['base_priority']['pl']['accuracy'])} | "
                     f"{percent(metric['base_priority']['en']['accuracy'])} | {subset['scored_counts']['base_priority']} |")
    if "weak_50" in report["subsets_with_full_reference_pool"]:
        lines += ["", "## Opisy bez wystarczających informacji", "",
                  "Referencja pozostaje stała: zatwierdzone 120. Nowe 50 jest wyłącznie zapytaniami; nie podpowiada sobie nawzajem.", "",
                  "| Zadanie | Język | Brak etykiety | Wymuszona odpowiedź modelu |", "|---|---|---:|---:|"]
        for task, label in names:
            for language in ("pl", "en"):
                missing = report["insufficient_information"][language][task]
                lines.append(f"| {label} | {language.upper()} | {missing['count']} | {missing['forced_predictions']} |")
        lines += ["", "To nie jest accuracy na niejasnych opisach. Brak możliwości ustalenia etykiety oznaczono null; wymuszone odpowiedzi ujawniają brak mechanizmu odmowy lub prośby o doprecyzowanie."]
    for task, label in names:
        lines += ["", f"## {label}: poprawne rozpoznania na klasę", "",
                  "| Etykieta | PL | EN | Liczba |", "|---|---:|---:|---:|"]
        metric = report["metrics"][task]
        for index, category in enumerate(metric["pl"]["labels"]):
            lines.append(f"| {category} | {metric['pl']['confusion_matrix'][index][index]} | "
                         f"{metric['en']['confusion_matrix'][index][index]} | {metric['pl']['per_class'][category]['support']} |")
    lines += ["", "## Warunki i ograniczenia", "",
              f"Model `{report['conditions']['model_id']}`, snapshot `{report['conditions']['model_revision']}`.",
              "Te same parametry: k=3, kosinus, głosowanie większościowe, wykluczenie grupy incydentu, CPU; bez strojenia progów. Sąsiadami są wyłącznie rekordy reference_eligible.",
              "Wariant PL ma polskie referencje, a EN angielskie. MiniLM otrzymuje wyłącznie text; uzasadnienia i checkbox nie są wejściem modelu.",
              "Zbiór jest syntetyczny. Tłumaczenia są sparowane i nie stanowią niezależnych danych. Wpływu języka nie izolujemy od doboru słów w tłumaczeniu.",
              "Nie jest to końcowy test ani pomiar na danych organizacji. Pierwotne pomiary 40 przypadków i ich źródła zachowano w historii oraz snapshots/.", "",
              "## Przewidywania według ID", "",
              "| ID | Kategoria oczekiwana | Kategoria PL | Kategoria EN | Priorytet oczekiwany | Priorytet PL | Priorytet EN |",
              "|---|---|---|---|---|---|---|"]
    for row in report["paired_predictions"]:
        lines.append(f"| {row['id']} | {row['expected_category']} | {row['category_pl']} | {row['category_en']} | "
                     f"{row['expected_base_priority']} | {row['base_priority_pl']} | {row['base_priority_en']} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--polish-report", type=Path, default=PILOT / "comparison/pl/report.json")
    parser.add_argument("--english-report", type=Path, default=PILOT / "comparison/en/report.json")
    parser.add_argument("--polish-dataset", type=Path, default=PILOT / "tickets.json")
    parser.add_argument("--english-dataset", type=Path, default=PILOT / "tickets.en.json")
    parser.add_argument("--output", type=Path, default=PILOT / "comparison")
    args = parser.parse_args()
    try:
        pl, en = read_json(args.polish_report), read_json(args.english_report)
        previous_path = args.output / "report.json"
        previous = read_json(previous_path) if previous_path.exists() else None
        report = paired_comparison(pl, en, {"pl": args.polish_dataset, "en": args.english_dataset})
        report["sources"] = {"pl_report": str(args.polish_report), "en_report": str(args.english_report),
                             "pl_dataset": str(args.polish_dataset), "en_dataset": str(args.english_dataset)}
        if previous:
            report["previous_comparison"] = {"count": previous.get("count", previous.get("conditions", {}).get("count")),
                                              "generated_at": previous["generated_at"],
                                              "metrics": {task: {language: previous["metrics"][task][language]
                                                                 for language in ("pl", "en")}
                                                          for task in ("category", "base_priority")}}
        write_report(report, args.output, render_comparison(report, previous))
        print(f"Dopisano porownanie {report['count']} zgloszen: {args.output / 'report.md'}")
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f"Blad porownania: {exc}\n")


if __name__ == "__main__":
    main()
