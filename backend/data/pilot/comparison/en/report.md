# Wstępna diagnostyka MiniLM — język: en

Zbiór: `pilot-en-v1`.

Tryb etykiet: **proposed**. Rekordy: 40; grupy: 36.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje generatora nie są etykietami zatwierdzonymi przez autora.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `f4ed3f066ab8549781946f85c0f1794565332b16402b5b8cb6b60aa29763ecf0`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; pokrycie 100%.

| Zadanie | Accuracy | Macro-F1 |
|---|---:|---:|
| Kategoria | 67.5% | 0.659 |
| Priorytet bazowy | 50.0% | 0.380 |
| Punkt odniesienia: zawsze medium | 40.0% | 0.143 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 32–51 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.

Ładowanie modelu: 0.47 s; embeddingi: 0.93 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

## Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 7 | 0 | 1 | 2 |
| hardware | 1 | 6 | 2 | 1 |
| network | 0 | 0 | 10 | 0 |
| software | 3 | 2 | 1 | 4 |

## Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 0 | 6 | 2 | 0 |
| medium | 4 | 11 | 0 | 1 |
| high | 0 | 2 | 8 | 2 |
| critical | 0 | 0 | 3 | 1 |

## Błędy do obejrzenia

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-01 | accounts_access → accounts_access | low → medium | ACC-06 (0.527) |
| ACC-02 | accounts_access → accounts_access | low → high | ACC-06 (0.652) |
| ACC-03 | accounts_access → software | medium → medium | SW-03 (0.417) |
| ACC-04 | accounts_access → software | medium → medium | ACC-09 (0.433) |
| ACC-05 | accounts_access → accounts_access | medium → critical | ACC-10 (0.265) |
| ACC-06 | accounts_access → accounts_access | medium → low | ACC-02 (0.652) |
| ACC-07 | accounts_access → network | high → critical | ACC-10 (0.479) |
| HW-01 | hardware → hardware | low → medium | HW-06 (0.263) |
| HW-02 | hardware → hardware | low → high | HW-07 (0.300) |
| HW-03 | hardware → software | medium → medium | SW-05 (0.482) |
| HW-04 | hardware → network | medium → medium | SW-05 (0.488) |
| HW-05 | hardware → network | medium → medium | NET-03 (0.356) |
| HW-08 | hardware → hardware | high → medium | HW-03 (0.361) |
| HW-10 | hardware → accounts_access | critical → high | HW-07 (0.510) |
| NET-01 | network → network | low → medium | NET-02 (0.579) |
| NET-02 | network → network | low → medium | NET-04 (0.604) |
| NET-03 | network → network | medium → low | NET-01 (0.579) |
| NET-04 | network → network | medium → low | NET-02 (0.604) |
| NET-05 | network → network | medium → low | NET-02 (0.561) |
| NET-08 | network → network | high → critical | NET-10 (0.617) |
| NET-09 | network → network | high → medium | NET-05 (0.440) |
| NET-10 | network → network | critical → high | NET-08 (0.617) |
| SW-01 | software → hardware | low → medium | SW-04 (0.274) |
| SW-02 | software → software | low → medium | SW-03 (0.314) |
| SW-03 | software → accounts_access | medium → medium | SW-05 (0.530) |
| SW-04 | software → accounts_access | medium → medium | SW-05 (0.458) |
| SW-05 | software → hardware | medium → medium | SW-03 (0.530) |
| SW-06 | software → network | medium → medium | NET-03 (0.414) |
| SW-09 | software → accounts_access | high → high | ACC-09 (0.419) |
| SW-10 | software → software | critical → high | SW-08 (0.375) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.


---

## Pomiar 2026-11-01T13:30:26.091211+00:00 — 120 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/120-7c5b825674340c90.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-4a9e21ee8555ec05.json).

## Wstępna diagnostyka MiniLM — język: en

Zbiór: `pilot-en-v2-120`.

Tryb etykiet: **proposed**. Rekordy: 120; grupy: 108.

Etykiety zatwierdzone przez użytkownika: 40/120.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje nowych etykiet wymagają osobnego przeglądu.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `aa27cc96743bb20687c54818b8c27104c1b457d210dbc9434453d67712bb32b2`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; pokrycie 100%.

| Zadanie | Accuracy | Macro-F1 |
|---|---:|---:|
| Kategoria | 93.3% | 0.933 |
| Priorytet bazowy | 49.2% | 0.489 |
| Punkt odniesienia: zawsze medium | 40.0% | 0.143 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 32–51 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.

Ładowanie modelu: 0.11 s; embeddingi: 0.60 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

### Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 27 | 0 | 2 | 1 |
| hardware | 0 | 30 | 0 | 0 |
| network | 0 | 0 | 30 | 0 |
| software | 1 | 1 | 3 | 25 |

### Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 11 | 9 | 3 | 1 |
| medium | 7 | 28 | 11 | 2 |
| high | 0 | 17 | 13 | 6 |
| critical | 0 | 2 | 3 | 7 |

### Błędy do obejrzenia

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-02 | accounts_access → accounts_access | low → medium | ACC-06 (0.652) |
| ACC-04 | accounts_access → accounts_access | medium → high | ACC-28 (0.509) |
| ACC-07 | accounts_access → software | high → critical | SW-29 (0.607) |
| ACC-08 | accounts_access → network | high → high | NET-20 (0.627) |
| ACC-10 | accounts_access → accounts_access | critical → high | ACC-25 (0.611) |
| HW-02 | hardware → hardware | low → high | HW-07 (0.300) |
| HW-07 | hardware → hardware | high → critical | HW-30 (0.550) |
| HW-08 | hardware → hardware | high → medium | HW-25 (0.475) |
| NET-03 | network → network | medium → low | NET-11 (0.618) |
| NET-04 | network → network | medium → low | NET-11 (0.703) |
| NET-05 | network → network | medium → low | NET-14 (0.599) |
| NET-08 | network → network | high → medium | NET-24 (0.809) |
| NET-09 | network → network | high → medium | NET-25 (0.669) |
| NET-10 | network → network | critical → high | NET-28 (0.656) |
| SW-02 | software → software | low → medium | SW-18 (0.424) |
| SW-05 | software → hardware | medium → medium | SW-03 (0.530) |
| SW-06 | software → network | medium → medium | NET-03 (0.414) |
| ACC-11 | accounts_access → accounts_access | low → medium | ACC-01 (0.482) |
| ACC-12 | accounts_access → network | low → low | ACC-01 (0.596) |
| ACC-13 | accounts_access → accounts_access | low → medium | ACC-01 (0.542) |
| ACC-14 | accounts_access → accounts_access | low → critical | ACC-10 (0.276) |
| ACC-15 | accounts_access → accounts_access | medium → high | ACC-03 (0.531) |
| ACC-19 | accounts_access → accounts_access | medium → low | ACC-02 (0.644) |
| ACC-20 | accounts_access → accounts_access | medium → high | ACC-23 (0.433) |
| ACC-22 | accounts_access → accounts_access | medium → high | ACC-04 (0.425) |
| ACC-24 | accounts_access → accounts_access | high → medium | ACC-06 (0.484) |
| ACC-25 | accounts_access → accounts_access | high → critical | ACC-10 (0.611) |
| ACC-26 | accounts_access → accounts_access | high → medium | ACC-21 (0.430) |
| ACC-27 | accounts_access → accounts_access | high → medium | ACC-04 (0.506) |
| ACC-28 | accounts_access → accounts_access | high → medium | ACC-04 (0.509) |
| ACC-29 | accounts_access → accounts_access | critical → high | ACC-09 (0.481) |
| HW-11 | hardware → hardware | low → high | HW-23 (0.312) |
| HW-12 | hardware → hardware | low → medium | HW-22 (0.493) |
| HW-13 | hardware → hardware | low → medium | HW-05 (0.550) |
| HW-14 | hardware → hardware | low → high | HW-23 (0.322) |
| HW-15 | hardware → hardware | medium → high | HW-08 (0.414) |
| HW-16 | hardware → hardware | medium → high | HW-08 (0.428) |
| HW-18 | hardware → hardware | medium → high | HW-27 (0.503) |
| HW-21 | hardware → hardware | medium → critical | HW-10 (0.490) |
| HW-24 | hardware → hardware | high → medium | HW-03 (0.485) |
| HW-26 | hardware → hardware | high → critical | HW-10 (0.457) |
| HW-27 | hardware → hardware | high → medium | HW-18 (0.503) |
| HW-28 | hardware → hardware | high → medium | HW-09 (0.465) |
| NET-11 | network → network | low → medium | NET-04 (0.703) |
| NET-14 | network → network | low → medium | NET-02 (0.813) |
| NET-16 | network → network | medium → low | NET-04 (0.639) |
| NET-17 | network → network | medium → critical | NET-29 (0.685) |
| NET-19 | network → network | medium → high | NET-24 (0.794) |
| NET-20 | network → network | medium → high | ACC-08 (0.627) |
| NET-21 | network → network | medium → high | NET-08 (0.624) |
| NET-22 | network → network | medium → low | NET-13 (0.449) |
| NET-24 | network → network | high → medium | NET-08 (0.809) |
| NET-26 | network → network | high → medium | NET-15 (0.532) |
| NET-27 | network → network | high → critical | NET-23 (0.679) |
| NET-28 | network → network | high → critical | NET-23 (0.695) |
| NET-29 | network → network | critical → medium | NET-17 (0.685) |
| SW-12 | software → software | low → medium | SW-18 (0.271) |
| SW-16 | software → software | medium → high | SW-04 (0.532) |
| SW-18 | software → accounts_access | medium → low | SW-02 (0.424) |
| SW-24 | software → software | high → medium | SW-16 (0.447) |
| SW-25 | software → software | high → medium | SW-15 (0.403) |
| SW-26 | software → software | high → medium | SW-19 (0.459) |
| SW-27 | software → software | high → medium | SW-03 (0.399) |
| SW-28 | software → software | high → medium | SW-04 (0.511) |
| SW-29 | software → network | critical → critical | NET-30 (0.665) |
| SW-30 | software → network | critical → medium | NET-18 (0.563) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.


---

## Pomiar 2026-11-01T13:46:26.560123+00:00 — 170 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/170-0f9742ff5c812b9a.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-7c5b825674340c90.json).

## Wstępna diagnostyka MiniLM — język: en

Zbiór: `pilot-en-v3-170`.

Tryb etykiet: **proposed**. Rekordy: 170; grupy: 158.

Etykiety zatwierdzone przez użytkownika: 120/170.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje nowych etykiet wymagają osobnego przeglądu.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `13e2afc1946fe0d2448e126f5bb9960e0df917139c51a467cb12f94533bb401c`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; model odpowiada na 100% opisów.

Przykłady bez możliwej do ustalenia etykiety nie wchodzą do mianownika accuracy ani F1; ich liczebność raportujemy jawnie.

| Zadanie | Accuracy | Macro-F1 | Ocenione / wszystkie |
|---|---:|---:|---:|
| Kategoria | 94.0% | 0.939 | 150/170 |
| Priorytet bazowy | 52.3% | 0.529 | 130/170 |
| Punkt odniesienia: zawsze medium | 39.2% | 0.141 | 130/170 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 5–51 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.

Ładowanie modelu: 0.10 s; embeddingi: 0.58 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

### Grupy jakości opisu

| Grupa | Liczba | Accuracy kategorii | Ocenione kategorie | Accuracy priorytetu | Ocenione priorytety |
|---|---:|---:|---:|---:|---:|
| reference | 120 | 93.3% | 120 | 49.2% | 120 |
| weak | 50 | 96.7% | 30 | 90.0% | 10 |

Słabe opisy są wyłącznie zapytaniami do stałej referencji 120; nie stają się sąsiadami innych zgłoszeń.
Bez ustalalnej kategorii: 20; wymuszonych kategorii: 20.
Bez ustalalnego priorytetu: 40; wymuszonych priorytetów: 40.
Wymuszona etykieta przy braku informacji nie jest poprawnym rozpoznaniem; pokazuje brak mechanizmu odmowy.

### Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 35 | 0 | 2 | 1 |
| hardware | 0 | 38 | 0 | 0 |
| network | 1 | 0 | 36 | 0 |
| software | 1 | 1 | 3 | 32 |

### Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 13 | 9 | 3 | 1 |
| medium | 7 | 30 | 12 | 2 |
| high | 0 | 17 | 16 | 6 |
| critical | 0 | 2 | 3 | 9 |

### Błędy i odpowiedzi wymagające doprecyzowania

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

None oznacza brak ustalalnej etykiety i nie jest liczone jako błąd ani sukces klasyfikacji.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-02 | accounts_access → accounts_access | low → medium | ACC-06 (0.652) |
| ACC-04 | accounts_access → accounts_access | medium → high | ACC-28 (0.509) |
| ACC-07 | accounts_access → software | high → critical | SW-29 (0.607) |
| ACC-08 | accounts_access → network | high → high | NET-20 (0.627) |
| ACC-10 | accounts_access → accounts_access | critical → high | ACC-25 (0.611) |
| HW-02 | hardware → hardware | low → high | HW-07 (0.300) |
| HW-07 | hardware → hardware | high → critical | HW-30 (0.550) |
| HW-08 | hardware → hardware | high → medium | HW-25 (0.475) |
| NET-03 | network → network | medium → low | NET-11 (0.618) |
| NET-04 | network → network | medium → low | NET-11 (0.703) |
| NET-05 | network → network | medium → low | NET-14 (0.599) |
| NET-08 | network → network | high → medium | NET-24 (0.809) |
| NET-09 | network → network | high → medium | NET-25 (0.669) |
| NET-10 | network → network | critical → high | NET-28 (0.656) |
| SW-02 | software → software | low → medium | SW-18 (0.424) |
| SW-05 | software → hardware | medium → medium | SW-03 (0.530) |
| SW-06 | software → network | medium → medium | NET-03 (0.414) |
| ACC-11 | accounts_access → accounts_access | low → medium | ACC-01 (0.482) |
| ACC-12 | accounts_access → network | low → low | ACC-01 (0.596) |
| ACC-13 | accounts_access → accounts_access | low → medium | ACC-01 (0.542) |
| ACC-14 | accounts_access → accounts_access | low → critical | ACC-10 (0.276) |
| ACC-15 | accounts_access → accounts_access | medium → high | ACC-03 (0.531) |
| ACC-19 | accounts_access → accounts_access | medium → low | ACC-02 (0.644) |
| ACC-20 | accounts_access → accounts_access | medium → high | ACC-23 (0.433) |
| ACC-22 | accounts_access → accounts_access | medium → high | ACC-04 (0.425) |
| ACC-24 | accounts_access → accounts_access | high → medium | ACC-06 (0.484) |
| ACC-25 | accounts_access → accounts_access | high → critical | ACC-10 (0.611) |
| ACC-26 | accounts_access → accounts_access | high → medium | ACC-21 (0.430) |
| ACC-27 | accounts_access → accounts_access | high → medium | ACC-04 (0.506) |
| ACC-28 | accounts_access → accounts_access | high → medium | ACC-04 (0.509) |
| ACC-29 | accounts_access → accounts_access | critical → high | ACC-09 (0.481) |
| HW-11 | hardware → hardware | low → high | HW-23 (0.312) |
| HW-12 | hardware → hardware | low → medium | HW-22 (0.493) |
| HW-13 | hardware → hardware | low → medium | HW-05 (0.550) |
| HW-14 | hardware → hardware | low → high | HW-23 (0.322) |
| HW-15 | hardware → hardware | medium → high | HW-08 (0.414) |
| HW-16 | hardware → hardware | medium → high | HW-08 (0.428) |
| HW-18 | hardware → hardware | medium → high | HW-27 (0.503) |
| HW-21 | hardware → hardware | medium → critical | HW-10 (0.490) |
| HW-24 | hardware → hardware | high → medium | HW-03 (0.485) |
| HW-26 | hardware → hardware | high → critical | HW-10 (0.457) |
| HW-27 | hardware → hardware | high → medium | HW-18 (0.503) |
| HW-28 | hardware → hardware | high → medium | HW-09 (0.465) |
| NET-11 | network → network | low → medium | NET-04 (0.703) |
| NET-14 | network → network | low → medium | NET-02 (0.813) |
| NET-16 | network → network | medium → low | NET-04 (0.639) |
| NET-17 | network → network | medium → critical | NET-29 (0.685) |
| NET-19 | network → network | medium → high | NET-24 (0.794) |
| NET-20 | network → network | medium → high | ACC-08 (0.627) |
| NET-21 | network → network | medium → high | NET-08 (0.624) |
| NET-22 | network → network | medium → low | NET-13 (0.449) |
| NET-24 | network → network | high → medium | NET-08 (0.809) |
| NET-26 | network → network | high → medium | NET-15 (0.532) |
| NET-27 | network → network | high → critical | NET-23 (0.679) |
| NET-28 | network → network | high → critical | NET-23 (0.695) |
| NET-29 | network → network | critical → medium | NET-17 (0.685) |
| SW-12 | software → software | low → medium | SW-18 (0.271) |
| SW-16 | software → software | medium → high | SW-04 (0.532) |
| SW-18 | software → accounts_access | medium → low | SW-02 (0.424) |
| SW-24 | software → software | high → medium | SW-16 (0.447) |
| SW-25 | software → software | high → medium | SW-15 (0.403) |
| SW-26 | software → software | high → medium | SW-19 (0.459) |
| SW-27 | software → software | high → medium | SW-03 (0.399) |
| SW-28 | software → software | high → medium | SW-04 (0.511) |
| SW-29 | software → network | critical → critical | NET-30 (0.665) |
| SW-30 | software → network | critical → medium | NET-18 (0.563) |
| WEAK-01 | accounts_access → accounts_access | None → high | ACC-07 (0.525) |
| WEAK-02 | accounts_access → accounts_access | None → medium | ACC-15 (0.508) |
| WEAK-03 | accounts_access → accounts_access | None → medium | ACC-17 (0.545) |
| WEAK-04 | accounts_access → accounts_access | None → medium | ACC-06 (0.696) |
| WEAK-05 | accounts_access → accounts_access | None → low | ACC-13 (0.500) |
| WEAK-06 | accounts_access → accounts_access | None → medium | ACC-17 (0.641) |
| WEAK-09 | hardware → hardware | None → medium | HW-05 (0.491) |
| WEAK-10 | hardware → hardware | None → low | HW-11 (0.584) |
| WEAK-11 | hardware → hardware | None → low | HW-02 (0.417) |
| WEAK-12 | hardware → hardware | None → high | HW-09 (0.339) |
| WEAK-13 | hardware → hardware | None → high | HW-09 (0.436) |
| WEAK-17 | network → network | None → medium | NET-04 (0.588) |
| WEAK-18 | network → network | None → high | NET-07 (0.660) |
| WEAK-19 | network → network | None → medium | NET-17 (0.585) |
| WEAK-20 | network → network | None → high | NET-09 (0.541) |
| WEAK-21 | network → network | medium → high | NET-24 (0.644) |
| WEAK-22 | network → accounts_access | high → high | ACC-07 (0.426) |
| WEAK-24 | software → software | None → medium | SW-26 (0.552) |
| WEAK-25 | software → software | None → medium | SW-16 (0.742) |
| WEAK-26 | software → software | None → medium | SW-06 (0.578) |
| WEAK-27 | software → software | None → medium | SW-19 (0.638) |
| WEAK-30 | software → software | None → low | SW-14 (0.437) |
| WEAK-31 | None → accounts_access | None → medium | ACC-06 (0.238) |
| WEAK-32 | None → software | None → medium | SW-16 (0.159) |
| WEAK-33 | None → accounts_access | None → high | ACC-08 (0.166) |
| WEAK-34 | None → hardware | None → low | HW-12 (0.189) |
| WEAK-35 | None → network | None → medium | NET-22 (0.320) |
| WEAK-36 | None → accounts_access | None → medium | ACC-21 (0.397) |
| WEAK-37 | None → software | None → high | SW-28 (0.395) |
| WEAK-38 | None → hardware | None → critical | HW-10 (0.259) |
| WEAK-39 | None → software | None → low | HW-15 (0.322) |
| WEAK-40 | None → hardware | None → low | HW-01 (0.315) |
| WEAK-41 | None → software | None → low | SW-13 (0.400) |
| WEAK-42 | None → software | None → critical | SW-01 (0.246) |
| WEAK-43 | None → accounts_access | None → medium | ACC-18 (0.306) |
| WEAK-44 | None → accounts_access | None → critical | ACC-29 (0.166) |
| WEAK-45 | None → accounts_access | None → low | ACC-06 (0.241) |
| WEAK-46 | None → hardware | None → critical | HW-30 (0.201) |
| WEAK-47 | None → hardware | None → low | HW-02 (0.266) |
| WEAK-48 | None → hardware | None → low | SW-14 (0.270) |
| WEAK-49 | None → network | None → critical | SW-10 (0.174) |
| WEAK-50 | None → hardware | None → critical | HW-29 (0.266) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.
