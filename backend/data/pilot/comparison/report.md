# Pilotaż MiniLM: porównanie polskich opisów i angielskiego tłumaczenia

Data: 2026-11-01. 40 tych samych przypadków, 36 grup incydentów. Etykiety i tłumaczenia oczekują na ręczny przegląd.

## Wyniki

| Zadanie | Accuracy PL | Accuracy EN | Zmiana EN − PL | Macro-F1 PL | Macro-F1 EN |
|---|---:|---:|---:|---:|---:|
| Kategoria | 60,0% | 67,5% | +7,5 p.p. | 0,582 | 0,659 |
| Priorytet bazowy | 37,5% | 50,0% | +12,5 p.p. | 0,306 | 0,380 |

Punkt odniesienia „zawsze medium”: accuracy 40,0%, macro-F1 0,143 w obu językach.

Angielska wersja poprawnie klasyfikuje kategorię 27/40 spraw (PL: 24/40), a priorytet bazowy 20/40 (PL: 15/40).
To poprawa na tej konkretnej próbce. Wynik nie rozstrzyga jakości na rzeczywistych zgłoszeniach ani nie izoluje całkowicie wpływu języka od doboru słów w tłumaczeniu.

## Poprawa i pogorszenie dla tych samych przypadków

| Zadanie | Oba poprawne | Tylko PL poprawnie | Tylko EN poprawnie | Oba błędne |
|---|---:|---:|---:|---:|
| Kategoria | 19 | 5 | 8 | 8 |
| Priorytet bazowy | 9 | 6 | 11 | 14 |

## Kategorie: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba przykładów |
|---|---:|---:|---:|
| accounts_access | 5 | 7 | 10 |
| hardware | 3 | 6 | 10 |
| network | 9 | 10 | 10 |
| software | 7 | 4 | 10 |

## Priorytety bazowe: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba przykładów |
|---|---:|---:|---:|
| low | 4 | 0 | 8 |
| medium | 6 | 11 | 16 |
| high | 5 | 8 | 12 |
| critical | 0 | 1 | 4 |

Poprawa nie obejmuje każdej klasy: Oprogramowanie spada z 7/10 do 4/10, a niski priorytet z 4/8 do 0/8.
Wyniki przemawiają za osobną analizą kategorii i priorytetu oraz przeglądem błędów; tłumaczenie nie rozwiązuje problemu automatycznie.

## Warunki i zachowanie oryginału

- Model: `sentence-transformers/all-MiniLM-L6-v2`; ten sam snapshot `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
- Obie wersje przeliczono tym samym skryptem, w tym samym środowisku, na CPU, z k=3, kosinusem i wykluczeniem całej grupy badanego incydentu.
- Zachowano ID, grupy incydentów, proponowane etykiety i checkboxy. Do modelu trafia wyłącznie tekst opisu.
- Wariant PL ma wyłącznie polskie referencje, a EN wyłącznie angielskie; nie ma par tłumaczeń wśród sąsiadów ocenianego przykładu.
- Nie dobierano parametrów ani progów na wynikach tego porównania.
- Ponowny polski pomiar odtworzył wszystkie przewidywania kategorii i priorytetu oraz metryki z 2026-10-28.
- Oryginalne polskie dane i raporty zachowano. Nowe przebiegi są w oddzielnych katalogach `pl/` i `en/`.
- Długość opisu z tokenami specjalnymi: PL 56–95, EN 32–51; limit 256. W obu wersjach 0 tokenów [UNK].

Oba zbiory są syntetyczne i mają 0/40 etykiet zatwierdzonych przez autora. Tłumaczenie nie jest niezależnym zbiorem testowym.
Nie ma końcowej ewaluacji ani podstaw do wnioskowania o istotności statystycznej. Pojedynczych pomiarów czasu nie porównujemy jako benchmarku.

## Pliki i odtwarzanie

- [Polskie dane](../tickets.json), [polska wersja do przeglądu](../review.md).
- [Angielskie dane](../tickets.en.json), [angielska wersja do przeglądu](../review.en.md).
- [Nowy raport PL](pl/report.md), [nowy raport EN](en/report.md), [pierwotny raport PL](../results/report.md).
- [Pochodzenie tłumaczenia i polecenia odtworzenia](../translation-en.md).
- [Wyniki porównania w JSON](report.json).

## Przewidywania dla poszczególnych zgłoszeń

| ID | Kategoria oczekiwana | Kategoria PL | Kategoria EN | Priorytet oczekiwany | Priorytet PL | Priorytet EN |
|---|---|---|---|---|---|---|
| ACC-01 | accounts_access | accounts_access | accounts_access | low | medium | medium |
| ACC-02 | accounts_access | accounts_access | accounts_access | low | low | high |
| ACC-03 | accounts_access | software | software | medium | low | medium |
| ACC-04 | accounts_access | software | software | medium | low | medium |
| ACC-05 | accounts_access | network | accounts_access | medium | high | critical |
| ACC-06 | accounts_access | accounts_access | accounts_access | medium | low | low |
| ACC-07 | accounts_access | accounts_access | network | high | critical | critical |
| ACC-08 | accounts_access | network | accounts_access | high | high | high |
| ACC-09 | accounts_access | accounts_access | accounts_access | high | high | high |
| ACC-10 | accounts_access | software | accounts_access | critical | low | critical |
| HW-01 | hardware | software | hardware | low | low | medium |
| HW-02 | hardware | software | hardware | low | low | high |
| HW-03 | hardware | software | software | medium | medium | medium |
| HW-04 | hardware | accounts_access | network | medium | low | medium |
| HW-05 | hardware | network | network | medium | medium | medium |
| HW-06 | hardware | network | hardware | medium | medium | medium |
| HW-07 | hardware | hardware | hardware | high | critical | high |
| HW-08 | hardware | hardware | hardware | high | high | medium |
| HW-09 | hardware | hardware | hardware | high | low | high |
| HW-10 | hardware | software | accounts_access | critical | high | high |
| NET-01 | network | network | network | low | medium | medium |
| NET-02 | network | network | network | low | high | medium |
| NET-03 | network | network | network | medium | medium | low |
| NET-04 | network | network | network | medium | low | low |
| NET-05 | network | network | network | medium | low | low |
| NET-06 | network | network | network | medium | medium | medium |
| NET-07 | network | network | network | high | high | high |
| NET-08 | network | network | network | high | low | critical |
| NET-09 | network | software | network | high | low | medium |
| NET-10 | network | network | network | critical | medium | high |
| SW-01 | software | accounts_access | hardware | low | low | medium |
| SW-02 | software | software | software | low | high | medium |
| SW-03 | software | software | accounts_access | medium | high | medium |
| SW-04 | software | network | accounts_access | medium | high | medium |
| SW-05 | software | software | hardware | medium | critical | medium |
| SW-06 | software | software | network | medium | medium | medium |
| SW-07 | software | software | software | high | medium | high |
| SW-08 | software | software | software | high | medium | high |
| SW-09 | software | software | accounts_access | high | high | high |
| SW-10 | software | accounts_access | software | critical | high | high |


---

## Pomiar 2026-11-01T13:30:42.184277+00:00 — 120 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/120-436296d23e8c2244.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-680a135dcc13ee9b.json).

## Porównanie PL/EN

120 tych samych przypadków; 108 grup incydentów; tryb etykiet `proposed`.
Zatwierdzone etykiety: PL 40/120, EN 40/120.
Pozostałe nowe przykłady i tłumaczenia oczekują na ręczny przegląd.

| Zadanie | Accuracy PL | Accuracy EN | Zmiana EN − PL | Macro-F1 PL | Macro-F1 EN |
|---|---:|---:|---:|---:|---:|
| Kategoria | 79,2% | 93,3% | +14.17 p.p. | 0.792 | 0.933 |
| Priorytet bazowy | 40,8% | 49,2% | +8.33 p.p. | 0.424 | 0.489 |

Stałe medium: accuracy 40,0%; macro-F1 0.143.

### Poprzedni i bieżący rozmiar próbki

| Zadanie | Język | Poprzednia próbka | Bieżąca próbka |
|---|---|---:|---:|
| Kategoria | PL | 60,0% (40) | 79,2% (120) |
| Kategoria | EN | 67,5% (40) | 93,3% (120) |
| Priorytet bazowy | PL | 37,5% (40) | 40,8% (120) |
| Priorytet bazowy | EN | 50,0% (40) | 49,2% (120) |

Zmieniły się zarówno oceniane przypadki, jak i pula sąsiadów. Różnica między rozmiarami nie jest pomiarem poprawy na stałym zbiorze testowym.

### Podzbiory przy pełnej puli referencji bieżącego przebiegu

Każde zgłoszenie nadal wyklucza własną grupę. Podzbiory poniżej nie uruchamiają ponownie modelu.

| Podzbiór | Liczba | Kategoria PL | Kategoria EN | Priorytet PL | Priorytet EN |
|---|---:|---:|---:|---:|---:|
| original_40 | 40 | 87,5% | 90,0% | 42,5% | 65,0% |
| new_80 | 80 | 75,0% | 95,0% | 40,0% | 41,2% |

### Kategoria: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba |
|---|---:|---:|---:|
| accounts_access | 22 | 27 | 30 |
| hardware | 23 | 30 | 30 |
| network | 23 | 30 | 30 |
| software | 27 | 25 | 30 |

### Priorytet bazowy: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba |
|---|---:|---:|---:|
| low | 16 | 11 | 24 |
| medium | 15 | 28 | 48 |
| high | 11 | 13 | 36 |
| critical | 7 | 7 | 12 |

### Warunki i ograniczenia

Model `sentence-transformers/all-MiniLM-L6-v2`, snapshot `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
Te same parametry: k=3, kosinus, głosowanie większościowe, leave-one-group-out, CPU; bez strojenia progów.
Wariant PL ma polskie referencje, a EN angielskie. MiniLM otrzymuje wyłącznie text; uzasadnienia i checkbox nie są wejściem modelu.
Zbiór jest syntetyczny. Tłumaczenia są sparowane i nie stanowią niezależnych danych. Wpływu języka nie izolujemy od doboru słów w tłumaczeniu.
Nie jest to końcowy test ani pomiar na danych organizacji. Pierwotne pomiary 40 przypadków i ich źródła zachowano w historii oraz snapshots/.

### Przewidywania według ID

| ID | Kategoria oczekiwana | Kategoria PL | Kategoria EN | Priorytet oczekiwany | Priorytet PL | Priorytet EN |
|---|---|---|---|---|---|---|
| ACC-01 | accounts_access | accounts_access | accounts_access | low | low | low |
| ACC-02 | accounts_access | software | accounts_access | low | low | medium |
| ACC-03 | accounts_access | software | accounts_access | medium | low | medium |
| ACC-04 | accounts_access | accounts_access | accounts_access | medium | high | high |
| ACC-05 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-06 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-07 | accounts_access | accounts_access | software | high | high | critical |
| ACC-08 | accounts_access | network | network | high | medium | high |
| ACC-09 | accounts_access | accounts_access | accounts_access | high | high | high |
| ACC-10 | accounts_access | software | accounts_access | critical | low | high |
| HW-01 | hardware | hardware | hardware | low | low | low |
| HW-02 | hardware | hardware | hardware | low | medium | high |
| HW-03 | hardware | hardware | hardware | medium | medium | medium |
| HW-04 | hardware | hardware | hardware | medium | low | medium |
| HW-05 | hardware | hardware | hardware | medium | medium | medium |
| HW-06 | hardware | hardware | hardware | medium | low | medium |
| HW-07 | hardware | hardware | hardware | high | critical | critical |
| HW-08 | hardware | hardware | hardware | high | medium | medium |
| HW-09 | hardware | hardware | hardware | high | low | high |
| HW-10 | hardware | hardware | hardware | critical | critical | critical |
| NET-01 | network | network | network | low | low | low |
| NET-02 | network | network | network | low | low | low |
| NET-03 | network | network | network | medium | medium | low |
| NET-04 | network | network | network | medium | high | low |
| NET-05 | network | network | network | medium | high | low |
| NET-06 | network | network | network | medium | high | medium |
| NET-07 | network | network | network | high | medium | high |
| NET-08 | network | network | network | high | high | medium |
| NET-09 | network | software | network | high | low | medium |
| NET-10 | network | network | network | critical | medium | high |
| SW-01 | software | software | software | low | low | low |
| SW-02 | software | software | software | low | medium | medium |
| SW-03 | software | software | software | medium | high | medium |
| SW-04 | software | software | software | medium | medium | medium |
| SW-05 | software | software | hardware | medium | medium | medium |
| SW-06 | software | software | network | medium | medium | medium |
| SW-07 | software | software | software | high | critical | high |
| SW-08 | software | software | software | high | medium | high |
| SW-09 | software | software | software | high | high | high |
| SW-10 | software | software | software | critical | high | critical |
| ACC-11 | accounts_access | accounts_access | accounts_access | low | medium | medium |
| ACC-12 | accounts_access | accounts_access | network | low | low | low |
| ACC-13 | accounts_access | accounts_access | accounts_access | low | low | medium |
| ACC-14 | accounts_access | accounts_access | accounts_access | low | medium | critical |
| ACC-15 | accounts_access | accounts_access | accounts_access | medium | medium | high |
| ACC-16 | accounts_access | accounts_access | accounts_access | medium | high | medium |
| ACC-17 | accounts_access | accounts_access | accounts_access | medium | medium | medium |
| ACC-18 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-19 | accounts_access | accounts_access | accounts_access | medium | low | low |
| ACC-20 | accounts_access | software | accounts_access | medium | low | high |
| ACC-21 | accounts_access | accounts_access | accounts_access | medium | high | medium |
| ACC-22 | accounts_access | accounts_access | accounts_access | medium | high | high |
| ACC-23 | accounts_access | software | accounts_access | high | low | high |
| ACC-24 | accounts_access | software | accounts_access | high | low | medium |
| ACC-25 | accounts_access | accounts_access | accounts_access | high | low | critical |
| ACC-26 | accounts_access | accounts_access | accounts_access | high | high | medium |
| ACC-27 | accounts_access | accounts_access | accounts_access | high | medium | medium |
| ACC-28 | accounts_access | accounts_access | accounts_access | high | low | medium |
| ACC-29 | accounts_access | software | accounts_access | critical | critical | high |
| ACC-30 | accounts_access | accounts_access | accounts_access | critical | critical | critical |
| HW-11 | hardware | network | hardware | low | low | high |
| HW-12 | hardware | network | hardware | low | low | medium |
| HW-13 | hardware | hardware | hardware | low | high | medium |
| HW-14 | hardware | hardware | hardware | low | low | high |
| HW-15 | hardware | accounts_access | hardware | medium | low | high |
| HW-16 | hardware | hardware | hardware | medium | medium | high |
| HW-17 | hardware | hardware | hardware | medium | medium | medium |
| HW-18 | hardware | hardware | hardware | medium | high | high |
| HW-19 | hardware | software | hardware | medium | low | medium |
| HW-20 | hardware | hardware | hardware | medium | medium | medium |
| HW-21 | hardware | hardware | hardware | medium | medium | critical |
| HW-22 | hardware | network | hardware | medium | low | medium |
| HW-23 | hardware | hardware | hardware | high | low | high |
| HW-24 | hardware | accounts_access | hardware | high | medium | medium |
| HW-25 | hardware | network | hardware | high | critical | high |
| HW-26 | hardware | hardware | hardware | high | medium | critical |
| HW-27 | hardware | hardware | hardware | high | critical | medium |
| HW-28 | hardware | hardware | hardware | high | medium | medium |
| HW-29 | hardware | hardware | hardware | critical | critical | critical |
| HW-30 | hardware | hardware | hardware | critical | critical | critical |
| NET-11 | network | network | network | low | medium | medium |
| NET-12 | network | network | network | low | low | low |
| NET-13 | network | network | network | low | high | low |
| NET-14 | network | network | network | low | low | medium |
| NET-15 | network | hardware | network | medium | low | medium |
| NET-16 | network | software | network | medium | low | low |
| NET-17 | network | network | network | medium | low | critical |
| NET-18 | network | network | network | medium | critical | medium |
| NET-19 | network | network | network | medium | high | high |
| NET-20 | network | network | network | medium | high | high |
| NET-21 | network | network | network | medium | high | high |
| NET-22 | network | hardware | network | medium | low | low |
| NET-23 | network | hardware | network | high | critical | high |
| NET-24 | network | network | network | high | medium | medium |
| NET-25 | network | network | network | high | high | high |
| NET-26 | network | software | network | high | high | medium |
| NET-27 | network | network | network | high | medium | critical |
| NET-28 | network | accounts_access | network | high | high | critical |
| NET-29 | network | network | network | critical | medium | medium |
| NET-30 | network | network | network | critical | critical | critical |
| SW-11 | software | software | software | low | low | low |
| SW-12 | software | software | software | low | low | medium |
| SW-13 | software | software | software | low | critical | low |
| SW-14 | software | software | software | low | low | low |
| SW-15 | software | software | software | medium | medium | medium |
| SW-16 | software | software | software | medium | critical | high |
| SW-17 | software | software | software | medium | high | medium |
| SW-18 | software | software | accounts_access | medium | medium | low |
| SW-19 | software | software | software | medium | low | medium |
| SW-20 | software | software | software | medium | medium | medium |
| SW-21 | software | software | software | medium | high | medium |
| SW-22 | software | software | software | medium | low | medium |
| SW-23 | software | software | software | high | critical | high |
| SW-24 | software | network | software | high | medium | medium |
| SW-25 | software | software | software | high | high | medium |
| SW-26 | software | software | software | high | high | medium |
| SW-27 | software | accounts_access | software | high | high | medium |
| SW-28 | software | software | software | high | medium | medium |
| SW-29 | software | network | network | critical | critical | critical |
| SW-30 | software | software | network | critical | high | medium |


---

## Pomiar 2026-11-01T13:47:31.671663+00:00 — 170 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/170-a36822aa1fadb91c.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-436296d23e8c2244.json).

## Porównanie PL/EN

170 tych samych przypadków; 158 grup incydentów; tryb etykiet `proposed`.
Zatwierdzone etykiety: PL 120/170, EN 120/170.
Pozostałe nowe przykłady i tłumaczenia oczekują na ręczny przegląd.

Accuracy i F1 pomijają przykłady bez ustalalnej etykiety. Mianowniki podajemy jawnie; przewidywania pozostają widoczne dla wszystkich opisów.

| Zadanie | Accuracy PL | Accuracy EN | Ocenione / wszystkie | Zmiana EN − PL | Macro-F1 PL | Macro-F1 EN |
|---|---:|---:|---:|---:|---:|---:|
| Kategoria | 78,7% | 94,0% | 150/170 | +15.33 p.p. | 0.786 | 0.939 |
| Priorytet bazowy | 40,8% | 52,3% | 130/170 | +11.54 p.p. | 0.428 | 0.529 |

Stałe medium: accuracy 39,2%; macro-F1 0.141.

### Poprzedni i bieżący rozmiar próbki

| Zadanie | Język | Poprzednia próbka | Bieżąca próbka |
|---|---|---:|---:|
| Kategoria | PL | 79,2% (120) | 78,7% (170) |
| Kategoria | EN | 93,3% (120) | 94,0% (170) |
| Priorytet bazowy | PL | 40,8% (120) | 40,8% (170) |
| Priorytet bazowy | EN | 49,2% (120) | 52,3% (170) |

Zmienił się skład ocenianych przypadków, a brakujące etykiety mają jawne mianowniki. Różnica między rozmiarami nie jest pomiarem poprawy na stałym zbiorze testowym.

### Podzbiory przy pełnej puli referencji bieżącego przebiegu

Każde zgłoszenie nadal wyklucza własną grupę. Podzbiory poniżej nie uruchamiają ponownie modelu.

| Podzbiór | Liczba | Kategoria PL | Kategoria EN | Ocenione kategorie | Priorytet PL | Priorytet EN | Ocenione priorytety |
|---|---:|---:|---:|---:|---:|---:|---:|
| original_40 | 40 | 87,5% | 90,0% | 40 | 42,5% | 65,0% | 40 |
| new_80 | 80 | 75,0% | 95,0% | 80 | 40,0% | 41,2% | 80 |
| weak_50 | 50 | 76,7% | 96,7% | 30 | 40,0% | 90,0% | 10 |

### Opisy bez wystarczających informacji

Referencja pozostaje stała: zatwierdzone 120. Nowe 50 jest wyłącznie zapytaniami; nie podpowiada sobie nawzajem.

| Zadanie | Język | Brak etykiety | Wymuszona odpowiedź modelu |
|---|---|---:|---:|
| Kategoria | PL | 20 | 20 |
| Kategoria | EN | 20 | 20 |
| Priorytet bazowy | PL | 40 | 40 |
| Priorytet bazowy | EN | 40 | 40 |

To nie jest accuracy na niejasnych opisach. Brak możliwości ustalenia etykiety oznaczono null; wymuszone odpowiedzi ujawniają brak mechanizmu odmowy lub prośby o doprecyzowanie.

### Kategoria: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba |
|---|---:|---:|---:|
| accounts_access | 28 | 35 | 38 |
| hardware | 28 | 38 | 38 |
| network | 29 | 36 | 37 |
| software | 33 | 32 | 37 |

### Priorytet bazowy: poprawne rozpoznania na klasę

| Etykieta | PL | EN | Liczba |
|---|---:|---:|---:|
| low | 17 | 13 | 26 |
| medium | 16 | 30 | 51 |
| high | 11 | 16 | 39 |
| critical | 9 | 9 | 14 |

### Warunki i ograniczenia

Model `sentence-transformers/all-MiniLM-L6-v2`, snapshot `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
Te same parametry: k=3, kosinus, głosowanie większościowe, wykluczenie grupy incydentu, CPU; bez strojenia progów. Sąsiadami są wyłącznie rekordy reference_eligible.
Wariant PL ma polskie referencje, a EN angielskie. MiniLM otrzymuje wyłącznie text; uzasadnienia i checkbox nie są wejściem modelu.
Zbiór jest syntetyczny. Tłumaczenia są sparowane i nie stanowią niezależnych danych. Wpływu języka nie izolujemy od doboru słów w tłumaczeniu.
Nie jest to końcowy test ani pomiar na danych organizacji. Pierwotne pomiary 40 przypadków i ich źródła zachowano w historii oraz snapshots/.

### Przewidywania według ID

| ID | Kategoria oczekiwana | Kategoria PL | Kategoria EN | Priorytet oczekiwany | Priorytet PL | Priorytet EN |
|---|---|---|---|---|---|---|
| ACC-01 | accounts_access | accounts_access | accounts_access | low | low | low |
| ACC-02 | accounts_access | software | accounts_access | low | low | medium |
| ACC-03 | accounts_access | software | accounts_access | medium | low | medium |
| ACC-04 | accounts_access | accounts_access | accounts_access | medium | high | high |
| ACC-05 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-06 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-07 | accounts_access | accounts_access | software | high | high | critical |
| ACC-08 | accounts_access | network | network | high | medium | high |
| ACC-09 | accounts_access | accounts_access | accounts_access | high | high | high |
| ACC-10 | accounts_access | software | accounts_access | critical | low | high |
| HW-01 | hardware | hardware | hardware | low | low | low |
| HW-02 | hardware | hardware | hardware | low | medium | high |
| HW-03 | hardware | hardware | hardware | medium | medium | medium |
| HW-04 | hardware | hardware | hardware | medium | low | medium |
| HW-05 | hardware | hardware | hardware | medium | medium | medium |
| HW-06 | hardware | hardware | hardware | medium | low | medium |
| HW-07 | hardware | hardware | hardware | high | critical | critical |
| HW-08 | hardware | hardware | hardware | high | medium | medium |
| HW-09 | hardware | hardware | hardware | high | low | high |
| HW-10 | hardware | hardware | hardware | critical | critical | critical |
| NET-01 | network | network | network | low | low | low |
| NET-02 | network | network | network | low | low | low |
| NET-03 | network | network | network | medium | medium | low |
| NET-04 | network | network | network | medium | high | low |
| NET-05 | network | network | network | medium | high | low |
| NET-06 | network | network | network | medium | high | medium |
| NET-07 | network | network | network | high | medium | high |
| NET-08 | network | network | network | high | high | medium |
| NET-09 | network | software | network | high | low | medium |
| NET-10 | network | network | network | critical | medium | high |
| SW-01 | software | software | software | low | low | low |
| SW-02 | software | software | software | low | medium | medium |
| SW-03 | software | software | software | medium | high | medium |
| SW-04 | software | software | software | medium | medium | medium |
| SW-05 | software | software | hardware | medium | medium | medium |
| SW-06 | software | software | network | medium | medium | medium |
| SW-07 | software | software | software | high | critical | high |
| SW-08 | software | software | software | high | medium | high |
| SW-09 | software | software | software | high | high | high |
| SW-10 | software | software | software | critical | high | critical |
| ACC-11 | accounts_access | accounts_access | accounts_access | low | medium | medium |
| ACC-12 | accounts_access | accounts_access | network | low | low | low |
| ACC-13 | accounts_access | accounts_access | accounts_access | low | low | medium |
| ACC-14 | accounts_access | accounts_access | accounts_access | low | medium | critical |
| ACC-15 | accounts_access | accounts_access | accounts_access | medium | medium | high |
| ACC-16 | accounts_access | accounts_access | accounts_access | medium | high | medium |
| ACC-17 | accounts_access | accounts_access | accounts_access | medium | medium | medium |
| ACC-18 | accounts_access | accounts_access | accounts_access | medium | low | medium |
| ACC-19 | accounts_access | accounts_access | accounts_access | medium | low | low |
| ACC-20 | accounts_access | software | accounts_access | medium | low | high |
| ACC-21 | accounts_access | accounts_access | accounts_access | medium | high | medium |
| ACC-22 | accounts_access | accounts_access | accounts_access | medium | high | high |
| ACC-23 | accounts_access | software | accounts_access | high | low | high |
| ACC-24 | accounts_access | software | accounts_access | high | low | medium |
| ACC-25 | accounts_access | accounts_access | accounts_access | high | low | critical |
| ACC-26 | accounts_access | accounts_access | accounts_access | high | high | medium |
| ACC-27 | accounts_access | accounts_access | accounts_access | high | medium | medium |
| ACC-28 | accounts_access | accounts_access | accounts_access | high | low | medium |
| ACC-29 | accounts_access | software | accounts_access | critical | critical | high |
| ACC-30 | accounts_access | accounts_access | accounts_access | critical | critical | critical |
| HW-11 | hardware | network | hardware | low | low | high |
| HW-12 | hardware | network | hardware | low | low | medium |
| HW-13 | hardware | hardware | hardware | low | high | medium |
| HW-14 | hardware | hardware | hardware | low | low | high |
| HW-15 | hardware | accounts_access | hardware | medium | low | high |
| HW-16 | hardware | hardware | hardware | medium | medium | high |
| HW-17 | hardware | hardware | hardware | medium | medium | medium |
| HW-18 | hardware | hardware | hardware | medium | high | high |
| HW-19 | hardware | software | hardware | medium | low | medium |
| HW-20 | hardware | hardware | hardware | medium | medium | medium |
| HW-21 | hardware | hardware | hardware | medium | medium | critical |
| HW-22 | hardware | network | hardware | medium | low | medium |
| HW-23 | hardware | hardware | hardware | high | low | high |
| HW-24 | hardware | accounts_access | hardware | high | medium | medium |
| HW-25 | hardware | network | hardware | high | critical | high |
| HW-26 | hardware | hardware | hardware | high | medium | critical |
| HW-27 | hardware | hardware | hardware | high | critical | medium |
| HW-28 | hardware | hardware | hardware | high | medium | medium |
| HW-29 | hardware | hardware | hardware | critical | critical | critical |
| HW-30 | hardware | hardware | hardware | critical | critical | critical |
| NET-11 | network | network | network | low | medium | medium |
| NET-12 | network | network | network | low | low | low |
| NET-13 | network | network | network | low | high | low |
| NET-14 | network | network | network | low | low | medium |
| NET-15 | network | hardware | network | medium | low | medium |
| NET-16 | network | software | network | medium | low | low |
| NET-17 | network | network | network | medium | low | critical |
| NET-18 | network | network | network | medium | critical | medium |
| NET-19 | network | network | network | medium | high | high |
| NET-20 | network | network | network | medium | high | high |
| NET-21 | network | network | network | medium | high | high |
| NET-22 | network | hardware | network | medium | low | low |
| NET-23 | network | hardware | network | high | critical | high |
| NET-24 | network | network | network | high | medium | medium |
| NET-25 | network | network | network | high | high | high |
| NET-26 | network | software | network | high | high | medium |
| NET-27 | network | network | network | high | medium | critical |
| NET-28 | network | accounts_access | network | high | high | critical |
| NET-29 | network | network | network | critical | medium | medium |
| NET-30 | network | network | network | critical | critical | critical |
| SW-11 | software | software | software | low | low | low |
| SW-12 | software | software | software | low | low | medium |
| SW-13 | software | software | software | low | critical | low |
| SW-14 | software | software | software | low | low | low |
| SW-15 | software | software | software | medium | medium | medium |
| SW-16 | software | software | software | medium | critical | high |
| SW-17 | software | software | software | medium | high | medium |
| SW-18 | software | software | accounts_access | medium | medium | low |
| SW-19 | software | software | software | medium | low | medium |
| SW-20 | software | software | software | medium | medium | medium |
| SW-21 | software | software | software | medium | high | medium |
| SW-22 | software | software | software | medium | low | medium |
| SW-23 | software | software | software | high | critical | high |
| SW-24 | software | network | software | high | medium | medium |
| SW-25 | software | software | software | high | high | medium |
| SW-26 | software | software | software | high | high | medium |
| SW-27 | software | accounts_access | software | high | high | medium |
| SW-28 | software | software | software | high | medium | medium |
| SW-29 | software | network | network | critical | critical | critical |
| SW-30 | software | software | network | critical | high | medium |
| WEAK-01 | accounts_access | accounts_access | accounts_access | None | high | high |
| WEAK-02 | accounts_access | accounts_access | accounts_access | None | medium | medium |
| WEAK-03 | accounts_access | accounts_access | accounts_access | None | medium | medium |
| WEAK-04 | accounts_access | software | accounts_access | None | low | medium |
| WEAK-05 | accounts_access | accounts_access | accounts_access | None | critical | low |
| WEAK-06 | accounts_access | accounts_access | accounts_access | None | medium | medium |
| WEAK-07 | accounts_access | accounts_access | accounts_access | low | medium | low |
| WEAK-08 | accounts_access | hardware | accounts_access | medium | medium | medium |
| WEAK-09 | hardware | network | hardware | None | low | medium |
| WEAK-10 | hardware | hardware | hardware | None | low | low |
| WEAK-11 | hardware | hardware | hardware | None | low | low |
| WEAK-12 | hardware | accounts_access | hardware | None | low | high |
| WEAK-13 | hardware | hardware | hardware | None | critical | high |
| WEAK-14 | hardware | hardware | hardware | low | low | low |
| WEAK-15 | hardware | accounts_access | hardware | medium | low | medium |
| WEAK-16 | hardware | hardware | hardware | high | medium | high |
| WEAK-17 | network | network | network | None | medium | medium |
| WEAK-18 | network | network | network | None | high | high |
| WEAK-19 | network | network | network | None | medium | medium |
| WEAK-20 | network | accounts_access | network | None | low | high |
| WEAK-21 | network | network | network | medium | low | high |
| WEAK-22 | network | network | accounts_access | high | critical | high |
| WEAK-23 | network | network | network | critical | critical | critical |
| WEAK-24 | software | software | software | None | high | medium |
| WEAK-25 | software | software | software | None | medium | medium |
| WEAK-26 | software | hardware | software | None | medium | medium |
| WEAK-27 | software | software | software | None | medium | medium |
| WEAK-28 | software | software | software | high | low | high |
| WEAK-29 | software | software | software | critical | critical | critical |
| WEAK-30 | software | software | software | None | high | low |
| WEAK-31 | None | accounts_access | accounts_access | None | low | medium |
| WEAK-32 | None | network | software | None | medium | medium |
| WEAK-33 | None | software | accounts_access | None | medium | high |
| WEAK-34 | None | accounts_access | hardware | None | low | low |
| WEAK-35 | None | network | network | None | low | medium |
| WEAK-36 | None | accounts_access | accounts_access | None | medium | medium |
| WEAK-37 | None | accounts_access | software | None | critical | high |
| WEAK-38 | None | accounts_access | hardware | None | medium | critical |
| WEAK-39 | None | software | software | None | medium | low |
| WEAK-40 | None | accounts_access | hardware | None | high | low |
| WEAK-41 | None | hardware | software | None | medium | low |
| WEAK-42 | None | accounts_access | software | None | low | critical |
| WEAK-43 | None | hardware | accounts_access | None | high | medium |
| WEAK-44 | None | accounts_access | accounts_access | None | low | critical |
| WEAK-45 | None | network | accounts_access | None | low | low |
| WEAK-46 | None | network | hardware | None | critical | critical |
| WEAK-47 | None | hardware | hardware | None | low | low |
| WEAK-48 | None | accounts_access | hardware | None | low | low |
| WEAK-49 | None | hardware | network | None | medium | critical |
| WEAK-50 | None | software | hardware | None | low | critical |
