# Proste metody klasyfikacji priorytetu

Pomiar: 2026-11-07T16:02:09.932862+00:00.

Język główny eksperymentu: angielski (EN); PL stanowi porównanie pomocnicze.

Model MiniLM i teksty bez zmian. Badamy wyłącznie priorytet bazowy; kategoria pozostaje k=3.
Bez checkboxa, ręcznych priorytetów i reguł eskalacji. Baza aplikacji nie jest używana.

Siatka: k=1,3,5,7,9,15; głosowanie zwykłe lub odwrotnością odległości (dla k=1 jeden wariant).
Dodatkowo regresja logistyczna: embeddingi MiniLM albo TF-IDF słów (1–2 gramów, sublinear_tf); C=0.1,1,10,100.
TF-IDF uczy słownik i IDF wyłącznie na treningu danego foldu; regresja nie używa kategorii ani checkboxa.
Wybór: macro-F1, potem accuracy, potem mniej high/critical przewidzianych jako low/medium.
120 zatwierdzonych referencji: zewnętrzne 5 foldów, wewnętrzne 4; grupy incydentów rozdzielone.
Zewnętrzne zapytania nie uczestniczą w doborze parametrów ani referencjach swojego foldu.
50 słabych opisów nie uczestniczy w doborze. Oceniane są tylko 10 ustalalnych priorytetów; 40 pomijamy.
Nowe etykiety są pending. Ta partia była wcześniej oglądana i nie jest niezależnym testem końcowym.

## EN

Wybór z 5-fold CV całej referencji: tfidf_logistic, C=100.

### Ocena doboru parametrów — zagnieżdżona walidacja grupowa

| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium | Critical zaniżone |
|---|---:|---:|---:|---:|
| Obecne k=3 | 53.3% | 0.514 | 19/48 | 7 |
| Dobór w wewnętrznej walidacji | 86.7% | 0.804 | 3/48 | 7 |

Parametry mogą różnić się między foldami. To ocena procedury doboru, nie jednej finalnej konfiguracji.

### Odtworzenie protokołu historycznego — diagnostyka

| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium |
|---|---:|---:|---:|
| k=1, uniform | 56.9% | 0.569 | 15/53 |
| k=3, uniform | 52.3% | 0.529 | 19/53 |
| k=3, distance | 53.1% | 0.538 | 19/53 |
| k=5, uniform | 53.1% | 0.524 | 15/53 |
| k=5, distance | 53.1% | 0.524 | 15/53 |
| k=7, uniform | 53.8% | 0.520 | 18/53 |
| k=7, distance | 53.8% | 0.518 | 17/53 |
| k=9, uniform | 59.2% | 0.585 | 18/53 |
| k=9, distance | 58.5% | 0.573 | 18/53 |
| k=15, uniform | 56.9% | 0.522 | 15/53 |
| k=15, distance | 56.2% | 0.528 | 16/53 |
| embedding_logistic, C=0.1 | 39.2% | 0.152 | 52/53 |
| embedding_logistic, C=1 | 62.3% | 0.469 | 13/53 |
| embedding_logistic, C=10 | 71.5% | 0.713 | 13/53 |
| embedding_logistic, C=100 | 73.8% | 0.752 | 11/53 |
| tfidf_logistic, C=0.1 | 39.2% | 0.141 | 53/53 |
| tfidf_logistic, C=1 | 67.7% | 0.459 | 11/53 |
| tfidf_logistic, C=10 | 83.1% | 0.724 | 2/53 |
| tfidf_logistic, C=100 | 85.4% | 0.767 | 2/53 |

130 ocenionych priorytetów ze 170 opisów. Własna grupa wykluczona; słabe opisy nie są referencjami.
Siatka pokazuje wyniki na znanym pilotażu; najlepszy wiersz nie stanowi niezależnego potwierdzenia poprawy.

### Wybrany wariant na 50 słabych opisach

| Wariant | Poprawne / ocenione | Macro-F1 |
|---|---:|---:|
| baseline | 9/10 | 0.914 |
| selected | 8/10 | 0.688 |

40 opisów bez ustalalnego priorytetu nadal otrzymuje wymuszoną odpowiedź; nie liczymy tego jako sukces.

## PL

Wybór z 5-fold CV całej referencji: tfidf_logistic, C=100.

### Ocena doboru parametrów — zagnieżdżona walidacja grupowa

| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium | Critical zaniżone |
|---|---:|---:|---:|---:|
| Obecne k=3 | 47.5% | 0.486 | 20/48 | 5 |
| Dobór w wewnętrznej walidacji | 78.3% | 0.717 | 7/48 | 8 |

Parametry mogą różnić się między foldami. To ocena procedury doboru, nie jednej finalnej konfiguracji.

### Odtworzenie protokołu historycznego — diagnostyka

| Wariant | Accuracy | Macro-F1 | Pilne jako low/medium |
|---|---:|---:|---:|
| k=1, uniform | 46.2% | 0.480 | 20/53 |
| k=3, uniform | 40.8% | 0.428 | 24/53 |
| k=3, distance | 40.8% | 0.428 | 24/53 |
| k=5, uniform | 42.3% | 0.431 | 21/53 |
| k=5, distance | 42.3% | 0.436 | 20/53 |
| k=7, uniform | 45.4% | 0.468 | 19/53 |
| k=7, distance | 47.7% | 0.499 | 18/53 |
| k=9, uniform | 41.5% | 0.423 | 19/53 |
| k=9, distance | 43.1% | 0.440 | 19/53 |
| k=15, uniform | 46.2% | 0.429 | 20/53 |
| k=15, distance | 46.2% | 0.440 | 19/53 |
| embedding_logistic, C=0.1 | 39.2% | 0.141 | 53/53 |
| embedding_logistic, C=1 | 51.5% | 0.319 | 24/53 |
| embedding_logistic, C=10 | 57.7% | 0.517 | 15/53 |
| embedding_logistic, C=100 | 63.1% | 0.638 | 13/53 |
| tfidf_logistic, C=0.1 | 39.2% | 0.141 | 53/53 |
| tfidf_logistic, C=1 | 63.8% | 0.384 | 12/53 |
| tfidf_logistic, C=10 | 78.5% | 0.697 | 7/53 |
| tfidf_logistic, C=100 | 80.0% | 0.732 | 6/53 |

130 ocenionych priorytetów ze 170 opisów. Własna grupa wykluczona; słabe opisy nie są referencjami.
Siatka pokazuje wyniki na znanym pilotażu; najlepszy wiersz nie stanowi niezależnego potwierdzenia poprawy.

### Wybrany wariant na 50 słabych opisach

| Wariant | Poprawne / ocenione | Macro-F1 |
|---|---:|---:|
| baseline | 4/10 | 0.367 |
| selected | 8/10 | 0.762 |

40 opisów bez ustalalnego priorytetu nadal otrzymuje wymuszoną odpowiedź; nie liczymy tego jako sukces.

## Wniosek wdrożeniowy

Dla EN kandydatem jest tfidf_logistic, C=100. Zagnieżdżona walidacja: accuracy 53.3% → 86.7%; pilne jako low/medium 19/48 → 3/48. To obiecujący wynik na syntetycznych opisach. Rozpoznawanie dokładnie critical: 5/12 → 5/12; na ocenialnych słabych opisach EN: 9/10 → 8/10. Eksperyment nie przełącza automatycznie aplikacji: nowa metoda wymaga osobnego treningu na zatwierdzonych referencjach i dalszej weryfikacji na niezależnych opisach. Stare raporty i obecne ustawienia klasyfikacji kategorii pozostają punktem odniesienia.

Pełne metryki klas, podziały foldów, przewidywania i zmienione decyzje: [report.json](report.json).
