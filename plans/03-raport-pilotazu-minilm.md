# Raport pilotażu MiniLM — 2026-10-28

Zapis wyników pierwszego przebiegu na 40 syntetycznych zgłoszeniach.
Etykiety oczekują na ręczny przegląd autora (0/40 zatwierdzonych).

Materiały: [dane](../backend/data/pilot/tickets.json), [próbka do przeglądu](../backend/data/pilot/review.md), [instrukcja etykietowania](../backend/data/pilot/labeling-guide.md), [skrypt pomiaru](../backend/scripts/evaluate_pilot.py).

Tryb etykiet: **proposed**. Rekordy: 40; grupy: 36.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje generatora nie są etykietami zatwierdzonymi przez autora.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `b6f1137290e7a95cd0ad79cdac8ccff553049851958acfe98fc5120686a3b542`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; pokrycie 100%.

| Zadanie | Accuracy | Macro-F1 |
|---|---:|---:|
| Kategoria | 60.0% | 0.582 |
| Priorytet bazowy | 37.5% | 0.306 |
| Punkt odniesienia: zawsze medium | 40.0% | 0.143 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 56–95 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji języka polskiego.

Ładowanie modelu: 0.11 s; embeddingi: 0.26 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

## Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 5 | 0 | 2 | 3 |
| hardware | 1 | 3 | 2 | 4 |
| network | 0 | 0 | 9 | 1 |
| software | 2 | 0 | 1 | 7 |

## Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 4 | 2 | 2 | 0 |
| medium | 6 | 6 | 3 | 1 |
| high | 3 | 2 | 5 | 2 |
| critical | 1 | 1 | 2 | 0 |

## Błędy do obejrzenia

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-01 | accounts_access → accounts_access | low → medium | SW-01 (0.790) |
| ACC-03 | accounts_access → software | medium → low | SW-01 (0.739) |
| ACC-04 | accounts_access → software | medium → low | SW-01 (0.762) |
| ACC-05 | accounts_access → network | medium → high | NET-08 (0.742) |
| ACC-06 | accounts_access → accounts_access | medium → low | ACC-01 (0.764) |
| ACC-07 | accounts_access → accounts_access | high → critical | ACC-09 (0.832) |
| ACC-08 | accounts_access → network | high → high | NET-07 (0.883) |
| ACC-10 | accounts_access → software | critical → low | SW-01 (0.734) |
| HW-01 | hardware → software | low → low | SW-01 (0.722) |
| HW-02 | hardware → software | low → low | SW-01 (0.718) |
| HW-03 | hardware → software | medium → medium | SW-01 (0.668) |
| HW-04 | hardware → accounts_access | medium → low | SW-01 (0.800) |
| HW-05 | hardware → network | medium → medium | HW-06 (0.818) |
| HW-06 | hardware → network | medium → medium | HW-05 (0.818) |
| HW-07 | hardware → hardware | high → critical | HW-10 (0.736) |
| HW-09 | hardware → hardware | high → low | NET-01 (0.698) |
| HW-10 | hardware → software | critical → high | SW-01 (0.742) |
| NET-01 | network → network | low → medium | NET-05 (0.833) |
| NET-02 | network → network | low → high | NET-08 (0.801) |
| NET-04 | network → network | medium → low | NET-02 (0.765) |
| NET-05 | network → network | medium → low | NET-01 (0.833) |
| NET-08 | network → network | high → low | NET-02 (0.801) |
| NET-09 | network → software | high → low | SW-01 (0.726) |
| NET-10 | network → network | critical → medium | NET-05 (0.819) |
| SW-01 | software → accounts_access | low → low | HW-04 (0.800) |
| SW-02 | software → software | low → high | SW-05 (0.703) |
| SW-03 | software → software | medium → high | SW-07 (0.743) |
| SW-04 | software → network | medium → high | NET-08 (0.697) |
| SW-05 | software → software | medium → critical | SW-10 (0.763) |
| SW-07 | software → software | high → medium | SW-10 (0.763) |
| SW-08 | software → software | high → medium | ACC-06 (0.666) |
| SW-10 | software → accounts_access | critical → high | ACC-07 (0.820) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w [report.json](../backend/data/pilot/results/report.json).
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.

---

## Kolejny pomiar — 2026-11-01, 120 zgłoszeń PL i EN

Zbiory rozszerzono do 120 odpowiadających sobie zgłoszeń w każdym języku, po 30 na kategorię i 108 grup incydentów. Użytkownik zatwierdził pierwotne 40 przykładów w obu wersjach; nowe 80 pozostaje do przeglądu. Pomiar używa trybu `proposed`, bez zmiany proponowanych etykiet.

| Zadanie | Accuracy PL | Accuracy EN | Macro-F1 PL | Macro-F1 EN |
|---|---:|---:|---:|---:|
| Kategoria | 79,2% | 93,3% | 0,792 | 0,933 |
| Priorytet bazowy | 40,8% | 49,2% | 0,424 | 0,489 |

Zachowano snapshot MiniLM `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, k=3, kosinus, głosowanie większościowe i wykluczenie całej grupy incydentu. Stałe medium daje 40% accuracy i macro-F1 0,143. Nie strojono progów ani parametrów.

Wyniki nie stanowią końcowego testu. Względem 40 przykładów zmieniły się zarazem oceniane przypadki i pula referencji. Pełne [porównanie](../backend/data/pilot/comparison/report.md) zawiera też wyniki pierwotnych 40 przypadków przy nowej puli sąsiadów. Priorytet bazowy pozostaje wyraźnie słabszym zadaniem niż kategoria.

Nowe wyniki dopisano na dole istniejących raportów, zachowując stare sekcje. Oryginalne dane 40 i stan 120 są w `backend/data/pilot/snapshots/`; stare JSON-y pomiarów zachowano w katalogach `runs/`. [Opis rozszerzenia](../backend/data/pilot/expansion-120.md) zawiera metadane i polecenia odtwarzania.

---

## Ostatni pomiar tej serii — 2026-11-01, 120 referencji i 50 słabych opisów

Użytkownik zatwierdził pozostałe 80 przykładów. Wszystkie wcześniejsze 120 jest approved. Dodano 50 nowych par PL/EN jako zapytania do tej stałej referencji, bez dopisywania ich do sąsiadów KNN. Nowe adnotacje są proposed/pending. Snapshot, k=3, kosinus i głosowanie zachowano.

| Zakres | Zadanie | Ocenione | Accuracy PL | Accuracy EN | Macro-F1 PL | Macro-F1 EN |
|---|---|---:|---:|---:|---:|---:|
| Nowe 50 | Kategoria | 30/50 | 76,7% | 96,7% | 0,772 | 0,966 |
| Nowe 50 | Priorytet bazowy | 10/50 | 40,0% | 90,0% | 0,367 | 0,914 |
| Całe 170 | Kategoria | 150/170 | 78,7% | 94,0% | 0,786 | 0,939 |
| Całe 170 | Priorytet bazowy | 130/170 | 40,8% | 52,3% | 0,428 | 0,529 |

Nie wymyślano etykiet dla niejednoznacznych tekstów: 20 opisów nie pozwala ustalić kategorii, a 40 priorytetu. Są oznaczone null i nie wchodzą do mianownika accuracy/F1. W obu językach klasyfikator mimo to wymusił odpowiednio 20 kategorii i 40 priorytetów. Obecny wynik uwidacznia potrzebę doprecyzowania takich opisów; nie potwierdza poprawności tych wymuszonych odpowiedzi.

Metryki na oryginalnych 120 odtworzono bez zmian. Nowe wyniki dopisano pod poprzednimi w istniejących raportach. [Pełne porównanie](../backend/data/pilot/comparison/report.md) i [protokół ostatniej partii](../backend/data/pilot/weak-170.md) zachowują mianowniki, podzbiory, kopie źródeł i wyniki JSON. Wzrost do 300 nie jest już zakresem tego pilotażu; 170 to decyzja o zakresie, a nie dowód wystarczającej próby wynikający z 93,3%.
