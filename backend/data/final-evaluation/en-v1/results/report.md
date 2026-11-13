# Końcowy test klasyfikacji EN — 100 przypadków (70/30)

Pomiar: 2026-11-07T19:00:01.277619+00:00
Test SHA-256: `7a21d23718c49444107d3c05c8b0f5497c724b999697c7b492189eb704e1c846`.

100 zatwierdzonych przypadków syntetycznych; 120 stałych referencji.
Dane testowe nie uczestniczą w uczeniu TF-IDF, IDF lub regresji. Modele i progi zachowano po teście.

## Trafność dla ustalalnych etykiet

Raw = propozycja przed progami; operacyjna = po progach, odmowa liczona jako FN.
Macro-F1 obejmuje cztery klasy. Poprawność zaakceptowanych zawsze czytać razem z pokryciem.

| Część | Zadanie | Ocenialne / wszystkie | Raw accuracy | Raw macro-F1 | Operacyjna accuracy | Operacyjna macro-F1 | Pokrycie ocenialnych | Accuracy zaakceptowanych |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| all | category | 88/100 | 88.6% | 0.885 | 85.2% | 0.883 | 92.0% | 92.6% |
| all | priority | 82/100 | 74.4% | 0.699 | 73.2% | 0.697 | 95.1% | 76.9% |
| complete | category | 70/70 | 88.6% | 0.886 | 85.7% | 0.886 | 92.9% | 92.3% |
| complete | priority | 70/70 | 75.7% | 0.713 | 74.3% | 0.711 | 94.3% | 78.8% |
| weak | category | 18/30 | 88.9% | 0.882 | 83.3% | 0.865 | 88.9% | 93.8% |
| weak | priority | 12/30 | 66.7% | 0.625 | 66.7% | 0.625 | 100.0% | 66.7% |

## Brak informacji do ustalenia etykiety

Null nie jest klasą i nie jest zaliczane jako trafienie lub pomyłka klasyfikacji.
Przyjęcie automatycznej etykiety mimo braku danych raportujemy osobno.

| Zadanie | Nieustalalne | Do weryfikacji | Odsetek weryfikacji | Automatycznie przyjęte mimo braku danych |
|---|---:|---:|---:|---:|
| category | 12 | 2 | 16.7% | 10 |
| priority | 18 | 1 | 5.6% | 17 |

Baseline zawsze medium: 28.0% na 82 ustalalnych priorytetach.
Pilne (high/critical): 42; raw zaniżone do low/medium: 3; po progach: 3; do weryfikacji: 1.
Critical raw zaniżone do dowolnego niższego poziomu: 9.
Checkbox, eskalacja i ręczne decyzje nie są częścią jakości przewidywania priorytetu bazowego.

## Macierz pomyłek: category, raw

Wiersze: etykiety wzorcowe; kolumny: odpowiedź. review oznacza odmowę.

| Wzorcowa | accounts_access | hardware | network | software | review |
|---|---:|---:|---:|---:|---:|
| accounts_access | 21 | 0 | 0 | 1 | 0 |
| hardware | 1 | 18 | 0 | 3 | 0 |
| network | 0 | 0 | 22 | 0 | 0 |
| software | 2 | 3 | 0 | 17 | 0 |

## Macierz pomyłek: category, operational

Wiersze: etykiety wzorcowe; kolumny: odpowiedź. review oznacza odmowę.

| Wzorcowa | accounts_access | hardware | network | software | review |
|---|---:|---:|---:|---:|---:|
| accounts_access | 21 | 0 | 0 | 1 | 0 |
| hardware | 1 | 17 | 0 | 1 | 3 |
| network | 0 | 0 | 22 | 0 | 0 |
| software | 1 | 2 | 0 | 15 | 4 |

## Macierz pomyłek: priority, raw

Wiersze: etykiety wzorcowe; kolumny: odpowiedź. review oznacza odmowę.

| Wzorcowa | low | medium | high | critical | review |
|---|---:|---:|---:|---:|---:|
| low | 8 | 6 | 3 | 0 | 0 |
| medium | 1 | 22 | 0 | 0 | 0 |
| high | 0 | 2 | 25 | 0 | 0 |
| critical | 0 | 1 | 8 | 6 | 0 |

## Macierz pomyłek: priority, operational

Wiersze: etykiety wzorcowe; kolumny: odpowiedź. review oznacza odmowę.

| Wzorcowa | low | medium | high | critical | review |
|---|---:|---:|---:|---:|---:|
| low | 7 | 6 | 2 | 0 | 2 |
| medium | 0 | 22 | 0 | 0 | 1 |
| high | 0 | 2 | 25 | 0 | 0 |
| critical | 0 | 1 | 7 | 6 | 1 |

## Pomyłki i odmowy na ustalalnych etykietach

| ID | Zadanie | Wzorcowa | Raw | Po progach | Powód weryfikacji |
|---|---|---|---|---|---|
| FINAL-EN-001 | category | accounts_access | software | software | — |
| FINAL-EN-003 | priority | low | medium | medium | — |
| FINAL-EN-004 | priority | critical | high | review | low_priority_score |
| FINAL-EN-008 | priority | critical | high | high | — |
| FINAL-EN-016 | priority | high | medium | medium | — |
| FINAL-EN-021 | priority | critical | medium | medium | — |
| FINAL-EN-023 | priority | low | medium | medium | — |
| FINAL-EN-028 | category | hardware | software | review | split_category_vote |
| FINAL-EN-032 | category | hardware | accounts_access | accounts_access | — |
| FINAL-EN-034 | category | hardware | software | software | — |
| FINAL-EN-034 | priority | critical | high | high | — |
| FINAL-EN-036 | priority | low | low | review | low_priority_score |
| FINAL-EN-037 | priority | low | medium | medium | — |
| FINAL-EN-044 | priority | high | medium | medium | — |
| FINAL-EN-047 | priority | critical | high | high | — |
| FINAL-EN-049 | category | software | hardware | hardware | — |
| FINAL-EN-058 | category | software | software | review | split_category_vote |
| FINAL-EN-060 | priority | critical | high | high | — |
| FINAL-EN-067 | category | software | hardware | hardware | — |
| FINAL-EN-068 | category | software | accounts_access | review | split_category_vote |
| FINAL-EN-069 | priority | low | medium | medium | — |
| FINAL-EN-072 | category | software | software | review | split_category_vote |
| FINAL-EN-072 | priority | critical | high | high | — |
| FINAL-EN-077 | priority | low | medium | medium | — |
| FINAL-EN-080 | priority | critical | high | high | — |
| FINAL-EN-081 | priority | low | high | review | low_priority_score |
| FINAL-EN-082 | priority | low | medium | medium | — |
| FINAL-EN-088 | priority | critical | high | high | — |
| FINAL-EN-094 | category | hardware | software | review | split_category_vote |
| FINAL-EN-096 | category | hardware | hardware | review | split_category_vote |
| FINAL-EN-097 | priority | low | high | high | — |
| FINAL-EN-104 | priority | low | high | high | — |
| FINAL-EN-106 | priority | medium | low | review | low_priority_score |
| FINAL-EN-107 | category | software | hardware | review | split_category_vote |
| FINAL-EN-109 | category | software | accounts_access | accounts_access | — |

## Warunki i ograniczenia

- synthetic cases, author-reviewed; same authoring assistant knew the pilot
- small and purposefully sampled cohorts; not real-world ticket prevalence
- host pilot and frozen Docker library versions differ
- float64 cosine replay may differ at floating-point boundaries from pgvector
- raw model scores are not calibrated correctness probabilities
- no changes to thresholds, references or model based on these results

Ładowanie modelu: 0.20 s; klasyfikacja 100: 3.05 s.
Pomiar jednorazowy, nie benchmark opóźnienia endpointu. Szczegóły per klasa, wszystkie odpowiedzi i sąsiedzi: [report.json](report.json).
