# Wstępna diagnostyka polskiego MiniLM

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

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.


---

## Pomiar 2026-11-01T13:28:58.898898+00:00 — 120 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/120-92a05e9a2df36260.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-6091acabb35d18dc.json).

## Wstępna diagnostyka MiniLM — język: pl

Zbiór: `pilot-pl-v2-120`.

Tryb etykiet: **proposed**. Rekordy: 120; grupy: 108.

Etykiety zatwierdzone przez użytkownika: 40/120.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje nowych etykiet wymagają osobnego przeglądu.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `137b5e7501b4be72dd00a2c97a914cd583c1dc8e4dcc5caa7f3c6a91c2662ae0`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; pokrycie 100%.

| Zadanie | Accuracy | Macro-F1 |
|---|---:|---:|
| Kategoria | 79.2% | 0.792 |
| Priorytet bazowy | 40.8% | 0.424 |
| Punkt odniesienia: zawsze medium | 40.0% | 0.143 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 56–111 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.

Ładowanie modelu: 0.46 s; embeddingi: 1.57 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

### Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 22 | 0 | 1 | 7 |
| hardware | 2 | 23 | 4 | 1 |
| network | 1 | 3 | 23 | 3 |
| software | 1 | 0 | 2 | 27 |

### Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 16 | 5 | 2 | 1 |
| medium | 17 | 15 | 14 | 2 |
| high | 7 | 12 | 11 | 6 |
| critical | 1 | 2 | 2 | 7 |

### Błędy do obejrzenia

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-02 | accounts_access → software | low → low | SW-01 (0.779) |
| ACC-03 | accounts_access → software | medium → low | ACC-27 (0.809) |
| ACC-04 | accounts_access → accounts_access | medium → high | ACC-28 (0.799) |
| ACC-05 | accounts_access → accounts_access | medium → low | ACC-17 (0.797) |
| ACC-06 | accounts_access → accounts_access | medium → low | ACC-01 (0.764) |
| ACC-08 | accounts_access → network | high → medium | NET-07 (0.883) |
| ACC-10 | accounts_access → software | critical → low | SW-01 (0.734) |
| HW-02 | hardware → hardware | low → medium | SW-01 (0.718) |
| HW-04 | hardware → hardware | medium → low | HW-20 (0.806) |
| HW-06 | hardware → hardware | medium → low | HW-05 (0.818) |
| HW-07 | hardware → hardware | high → critical | HW-30 (0.769) |
| HW-08 | hardware → hardware | high → medium | HW-20 (0.691) |
| HW-09 | hardware → hardware | high → low | HW-11 (0.738) |
| NET-04 | network → network | medium → high | NET-02 (0.765) |
| NET-05 | network → network | medium → high | NET-24 (0.833) |
| NET-06 | network → network | medium → high | NET-24 (0.794) |
| NET-07 | network → network | high → medium | ACC-08 (0.883) |
| NET-09 | network → software | high → low | NET-13 (0.782) |
| NET-10 | network → network | critical → medium | NET-05 (0.819) |
| SW-02 | software → software | low → medium | SW-11 (0.736) |
| SW-03 | software → software | medium → high | SW-23 (0.763) |
| SW-07 | software → software | high → critical | SW-23 (0.830) |
| SW-08 | software → software | high → medium | SW-26 (0.786) |
| SW-10 | software → software | critical → high | SW-23 (0.824) |
| ACC-11 | accounts_access → accounts_access | low → medium | ACC-05 (0.758) |
| ACC-14 | accounts_access → accounts_access | low → medium | ACC-01 (0.732) |
| ACC-16 | accounts_access → accounts_access | medium → high | ACC-28 (0.694) |
| ACC-18 | accounts_access → accounts_access | medium → low | ACC-01 (0.794) |
| ACC-19 | accounts_access → accounts_access | medium → low | ACC-02 (0.714) |
| ACC-20 | accounts_access → software | medium → low | ACC-13 (0.718) |
| ACC-21 | accounts_access → accounts_access | medium → high | ACC-26 (0.799) |
| ACC-22 | accounts_access → accounts_access | medium → high | ACC-09 (0.704) |
| ACC-23 | accounts_access → software | high → low | NET-11 (0.712) |
| ACC-24 | accounts_access → software | high → low | SW-01 (0.697) |
| ACC-25 | accounts_access → accounts_access | high → low | ACC-18 (0.726) |
| ACC-27 | accounts_access → accounts_access | high → medium | ACC-03 (0.809) |
| ACC-28 | accounts_access → accounts_access | high → low | ACC-04 (0.799) |
| ACC-29 | accounts_access → software | critical → critical | SW-29 (0.788) |
| HW-11 | hardware → network | low → low | NET-01 (0.836) |
| HW-12 | hardware → network | low → low | ACC-02 (0.747) |
| HW-13 | hardware → hardware | low → high | HW-07 (0.594) |
| HW-15 | hardware → accounts_access | medium → low | ACC-11 (0.637) |
| HW-18 | hardware → hardware | medium → high | HW-27 (0.783) |
| HW-19 | hardware → software | medium → low | SW-01 (0.776) |
| HW-22 | hardware → network | medium → low | NET-01 (0.789) |
| HW-23 | hardware → hardware | high → low | HW-14 (0.709) |
| HW-24 | hardware → accounts_access | high → medium | ACC-09 (0.763) |
| HW-25 | hardware → network | high → critical | HW-30 (0.628) |
| HW-26 | hardware → hardware | high → medium | HW-03 (0.720) |
| HW-27 | hardware → hardware | high → critical | HW-18 (0.783) |
| HW-28 | hardware → hardware | high → medium | HW-18 (0.684) |
| NET-11 | network → network | low → medium | ACC-05 (0.777) |
| NET-13 | network → network | low → high | NET-09 (0.782) |
| NET-15 | network → hardware | medium → low | HW-12 (0.690) |
| NET-16 | network → software | medium → low | SW-01 (0.724) |
| NET-17 | network → network | medium → low | NET-29 (0.782) |
| NET-18 | network → network | medium → critical | NET-29 (0.753) |
| NET-19 | network → network | medium → high | NET-24 (0.844) |
| NET-20 | network → network | medium → high | NET-07 (0.875) |
| NET-21 | network → network | medium → high | NET-14 (0.788) |
| NET-22 | network → hardware | medium → low | HW-07 (0.743) |
| NET-23 | network → hardware | high → critical | HW-29 (0.845) |
| NET-24 | network → network | high → medium | NET-19 (0.844) |
| NET-26 | network → software | high → high | SW-23 (0.716) |
| NET-27 | network → network | high → medium | NET-21 (0.767) |
| NET-28 | network → accounts_access | high → high | ACC-09 (0.792) |
| NET-29 | network → network | critical → medium | SW-29 (0.788) |
| SW-13 | software → software | low → critical | SW-30 (0.782) |
| SW-16 | software → software | medium → critical | SW-04 (0.728) |
| SW-17 | software → software | medium → high | SW-23 (0.690) |
| SW-19 | software → software | medium → low | SW-13 (0.750) |
| SW-21 | software → software | medium → high | SW-23 (0.779) |
| SW-22 | software → software | medium → low | SW-01 (0.746) |
| SW-23 | software → software | high → critical | SW-07 (0.830) |
| SW-24 | software → network | high → medium | NET-21 (0.783) |
| SW-27 | software → accounts_access | high → high | ACC-26 (0.724) |
| SW-28 | software → software | high → medium | SW-04 (0.671) |
| SW-29 | software → network | critical → critical | NET-30 (0.814) |
| SW-30 | software → software | critical → high | SW-23 (0.829) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.


---

## Pomiar 2026-11-01T13:45:45.262198+00:00 — 170 zgłoszeń

Pełny zapis tego przebiegu: [JSON](runs/170-edd150ad4764ab2f.json).

Zachowany poprzedni zapis JSON: [archiwum](runs/previous-92a05e9a2df36260.json).

## Wstępna diagnostyka MiniLM — język: pl

Zbiór: `pilot-pl-v3-170`.

Tryb etykiet: **proposed**. Rekordy: 170; grupy: 158.

Etykiety zatwierdzone przez użytkownika: 120/170.

To pilotaż syntetyczny, nie końcowa ewaluacja. Propozycje nowych etykiet wymagają osobnego przeglądu.
Wyniki nie służą do wyboru progów ani deklaracji jakości produkcyjnej.

Model: `sentence-transformers/all-MiniLM-L6-v2`; snapshot: `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`.
SHA-256 danych: `60321f0dca837c09d5c8b6616948a2161db9a28837d973ce03f8d2d965791f58`.
Metoda: leave-one-group-out, kosinus, k=3, głosowanie większościowe.
Remis: najbliższa etykieta; równe podobieństwo: ID. Bez progu pewności; model odpowiada na 100% opisów.

Przykłady bez możliwej do ustalenia etykiety nie wchodzą do mianownika accuracy ani F1; ich liczebność raportujemy jawnie.

| Zadanie | Accuracy | Macro-F1 | Ocenione / wszystkie |
|---|---:|---:|---:|
| Kategoria | 78.7% | 0.786 | 150/170 |
| Priorytet bazowy | 40.8% | 0.428 | 130/170 |
| Punkt odniesienia: zawsze medium | 39.2% | 0.141 | 130/170 |

Punkt odniesienia ignoruje tekst i zawsze wybiera obecny priorytet zastępczy aplikacji.
Porównujemy tu priorytety bazowe, bez checkboxa, decyzji administratora i eskalacji.

Tokeny z tokenami specjalnymi: 8–111 (limit 256).
Tokeny nieznane [UNK]: 0; udział 0.00%.
Brak [UNK] nie dowodzi dobrej reprezentacji badanego języka.

Ładowanie modelu: 0.10 s; embeddingi: 1.10 s.
Pomiar jednorazowy na CPU; bez wnioskowania o wydajności po rozgrzaniu.

### Grupy jakości opisu

| Grupa | Liczba | Accuracy kategorii | Ocenione kategorie | Accuracy priorytetu | Ocenione priorytety |
|---|---:|---:|---:|---:|---:|
| reference | 120 | 79.2% | 120 | 40.8% | 120 |
| weak | 50 | 76.7% | 30 | 40.0% | 10 |

Słabe opisy są wyłącznie zapytaniami do stałej referencji 120; nie stają się sąsiadami innych zgłoszeń.
Bez ustalalnej kategorii: 20; wymuszonych kategorii: 20.
Bez ustalalnego priorytetu: 40; wymuszonych priorytetów: 40.
Wymuszona etykieta przy braku informacji nie jest poprawnym rozpoznaniem; pokazuje brak mechanizmu odmowy.

### Kategorie: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | accounts_access | hardware | network | software |
|---|---:|---:|---:|---:|
| accounts_access | 28 | 1 | 1 | 8 |
| hardware | 4 | 28 | 5 | 1 |
| network | 2 | 3 | 29 | 3 |
| software | 1 | 1 | 2 | 33 |

### Priorytety bazowe: macierz pomyłek

Wiersz: oczekiwana etykieta; kolumna: przewidywana.

| Etykieta | low | medium | high | critical |
|---|---:|---:|---:|---:|
| low | 17 | 6 | 2 | 1 |
| medium | 19 | 16 | 14 | 2 |
| high | 8 | 13 | 11 | 7 |
| critical | 1 | 2 | 2 | 9 |

### Błędy i odpowiedzi wymagające doprecyzowania

Oczekiwane etykiety oznaczają etykiety wybranego trybu, a nie automatycznie prawdę wzorcową.

None oznacza brak ustalalnej etykiety i nie jest liczone jako błąd ani sukces klasyfikacji.

| ID | Kategoria: oczekiwana → wynik | Priorytet: oczekiwany → wynik | Najbliższy sąsiad |
|---|---|---|---|
| ACC-02 | accounts_access → software | low → low | SW-01 (0.779) |
| ACC-03 | accounts_access → software | medium → low | ACC-27 (0.809) |
| ACC-04 | accounts_access → accounts_access | medium → high | ACC-28 (0.799) |
| ACC-05 | accounts_access → accounts_access | medium → low | ACC-17 (0.797) |
| ACC-06 | accounts_access → accounts_access | medium → low | ACC-01 (0.764) |
| ACC-08 | accounts_access → network | high → medium | NET-07 (0.883) |
| ACC-10 | accounts_access → software | critical → low | SW-01 (0.734) |
| HW-02 | hardware → hardware | low → medium | SW-01 (0.718) |
| HW-04 | hardware → hardware | medium → low | HW-20 (0.806) |
| HW-06 | hardware → hardware | medium → low | HW-05 (0.818) |
| HW-07 | hardware → hardware | high → critical | HW-30 (0.769) |
| HW-08 | hardware → hardware | high → medium | HW-20 (0.691) |
| HW-09 | hardware → hardware | high → low | HW-11 (0.738) |
| NET-04 | network → network | medium → high | NET-02 (0.765) |
| NET-05 | network → network | medium → high | NET-24 (0.833) |
| NET-06 | network → network | medium → high | NET-24 (0.794) |
| NET-07 | network → network | high → medium | ACC-08 (0.883) |
| NET-09 | network → software | high → low | NET-13 (0.782) |
| NET-10 | network → network | critical → medium | NET-05 (0.819) |
| SW-02 | software → software | low → medium | SW-11 (0.736) |
| SW-03 | software → software | medium → high | SW-23 (0.763) |
| SW-07 | software → software | high → critical | SW-23 (0.830) |
| SW-08 | software → software | high → medium | SW-26 (0.786) |
| SW-10 | software → software | critical → high | SW-23 (0.824) |
| ACC-11 | accounts_access → accounts_access | low → medium | ACC-05 (0.758) |
| ACC-14 | accounts_access → accounts_access | low → medium | ACC-01 (0.732) |
| ACC-16 | accounts_access → accounts_access | medium → high | ACC-28 (0.694) |
| ACC-18 | accounts_access → accounts_access | medium → low | ACC-01 (0.794) |
| ACC-19 | accounts_access → accounts_access | medium → low | ACC-02 (0.714) |
| ACC-20 | accounts_access → software | medium → low | ACC-13 (0.718) |
| ACC-21 | accounts_access → accounts_access | medium → high | ACC-26 (0.799) |
| ACC-22 | accounts_access → accounts_access | medium → high | ACC-09 (0.704) |
| ACC-23 | accounts_access → software | high → low | NET-11 (0.712) |
| ACC-24 | accounts_access → software | high → low | SW-01 (0.697) |
| ACC-25 | accounts_access → accounts_access | high → low | ACC-18 (0.726) |
| ACC-27 | accounts_access → accounts_access | high → medium | ACC-03 (0.809) |
| ACC-28 | accounts_access → accounts_access | high → low | ACC-04 (0.799) |
| ACC-29 | accounts_access → software | critical → critical | SW-29 (0.788) |
| HW-11 | hardware → network | low → low | NET-01 (0.836) |
| HW-12 | hardware → network | low → low | ACC-02 (0.747) |
| HW-13 | hardware → hardware | low → high | HW-07 (0.594) |
| HW-15 | hardware → accounts_access | medium → low | ACC-11 (0.637) |
| HW-18 | hardware → hardware | medium → high | HW-27 (0.783) |
| HW-19 | hardware → software | medium → low | SW-01 (0.776) |
| HW-22 | hardware → network | medium → low | NET-01 (0.789) |
| HW-23 | hardware → hardware | high → low | HW-14 (0.709) |
| HW-24 | hardware → accounts_access | high → medium | ACC-09 (0.763) |
| HW-25 | hardware → network | high → critical | HW-30 (0.628) |
| HW-26 | hardware → hardware | high → medium | HW-03 (0.720) |
| HW-27 | hardware → hardware | high → critical | HW-18 (0.783) |
| HW-28 | hardware → hardware | high → medium | HW-18 (0.684) |
| NET-11 | network → network | low → medium | ACC-05 (0.777) |
| NET-13 | network → network | low → high | NET-09 (0.782) |
| NET-15 | network → hardware | medium → low | HW-12 (0.690) |
| NET-16 | network → software | medium → low | SW-01 (0.724) |
| NET-17 | network → network | medium → low | NET-29 (0.782) |
| NET-18 | network → network | medium → critical | NET-29 (0.753) |
| NET-19 | network → network | medium → high | NET-24 (0.844) |
| NET-20 | network → network | medium → high | NET-07 (0.875) |
| NET-21 | network → network | medium → high | NET-14 (0.788) |
| NET-22 | network → hardware | medium → low | HW-07 (0.743) |
| NET-23 | network → hardware | high → critical | HW-29 (0.845) |
| NET-24 | network → network | high → medium | NET-19 (0.844) |
| NET-26 | network → software | high → high | SW-23 (0.716) |
| NET-27 | network → network | high → medium | NET-21 (0.767) |
| NET-28 | network → accounts_access | high → high | ACC-09 (0.792) |
| NET-29 | network → network | critical → medium | SW-29 (0.788) |
| SW-13 | software → software | low → critical | SW-30 (0.782) |
| SW-16 | software → software | medium → critical | SW-04 (0.728) |
| SW-17 | software → software | medium → high | SW-23 (0.690) |
| SW-19 | software → software | medium → low | SW-13 (0.750) |
| SW-21 | software → software | medium → high | SW-23 (0.779) |
| SW-22 | software → software | medium → low | SW-01 (0.746) |
| SW-23 | software → software | high → critical | SW-07 (0.830) |
| SW-24 | software → network | high → medium | NET-21 (0.783) |
| SW-27 | software → accounts_access | high → high | ACC-26 (0.724) |
| SW-28 | software → software | high → medium | SW-04 (0.671) |
| SW-29 | software → network | critical → critical | NET-30 (0.814) |
| SW-30 | software → software | critical → high | SW-23 (0.829) |
| WEAK-01 | accounts_access → accounts_access | None → high | ACC-07 (0.602) |
| WEAK-02 | accounts_access → accounts_access | None → medium | ACC-27 (0.636) |
| WEAK-03 | accounts_access → accounts_access | None → medium | ACC-05 (0.640) |
| WEAK-04 | accounts_access → software | None → low | ACC-02 (0.739) |
| WEAK-05 | accounts_access → accounts_access | None → critical | SW-10 (0.596) |
| WEAK-06 | accounts_access → accounts_access | None → medium | ACC-05 (0.751) |
| WEAK-07 | accounts_access → accounts_access | low → medium | ACC-05 (0.743) |
| WEAK-08 | accounts_access → hardware | medium → medium | HW-04 (0.674) |
| WEAK-09 | hardware → network | None → low | NET-16 (0.670) |
| WEAK-10 | hardware → hardware | None → low | HW-23 (0.600) |
| WEAK-11 | hardware → hardware | None → low | HW-02 (0.482) |
| WEAK-12 | hardware → accounts_access | None → low | ACC-18 (0.473) |
| WEAK-13 | hardware → hardware | None → critical | HW-27 (0.626) |
| WEAK-15 | hardware → accounts_access | medium → low | ACC-02 (0.752) |
| WEAK-16 | hardware → hardware | high → medium | HW-20 (0.703) |
| WEAK-17 | network → network | None → medium | NET-05 (0.538) |
| WEAK-18 | network → network | None → high | NET-07 (0.554) |
| WEAK-19 | network → network | None → medium | NET-17 (0.747) |
| WEAK-20 | network → accounts_access | None → low | ACC-02 (0.678) |
| WEAK-21 | network → network | medium → low | NET-11 (0.745) |
| WEAK-22 | network → network | high → critical | NET-10 (0.728) |
| WEAK-24 | software → software | None → high | SW-07 (0.785) |
| WEAK-25 | software → software | None → medium | SW-15 (0.722) |
| WEAK-26 | software → hardware | None → medium | HW-20 (0.690) |
| WEAK-27 | software → software | None → medium | SW-19 (0.744) |
| WEAK-28 | software → software | high → low | SW-11 (0.688) |
| WEAK-30 | software → software | None → high | NET-08 (0.625) |
| WEAK-31 | None → accounts_access | None → low | ACC-02 (0.666) |
| WEAK-32 | None → network | None → medium | NET-04 (0.441) |
| WEAK-33 | None → software | None → medium | SW-06 (0.304) |
| WEAK-34 | None → accounts_access | None → low | ACC-02 (0.645) |
| WEAK-35 | None → network | None → low | NET-12 (0.588) |
| WEAK-36 | None → accounts_access | None → medium | ACC-17 (0.534) |
| WEAK-37 | None → accounts_access | None → critical | ACC-30 (0.644) |
| WEAK-38 | None → accounts_access | None → medium | NET-17 (0.595) |
| WEAK-39 | None → software | None → medium | SW-06 (0.522) |
| WEAK-40 | None → accounts_access | None → high | ACC-09 (0.510) |
| WEAK-41 | None → hardware | None → medium | HW-21 (0.570) |
| WEAK-42 | None → accounts_access | None → low | ACC-02 (0.692) |
| WEAK-43 | None → hardware | None → high | HW-03 (0.414) |
| WEAK-44 | None → accounts_access | None → low | ACC-13 (0.604) |
| WEAK-45 | None → network | None → low | ACC-17 (0.431) |
| WEAK-46 | None → network | None → critical | NET-30 (0.544) |
| WEAK-47 | None → hardware | None → low | HW-13 (0.409) |
| WEAK-48 | None → accounts_access | None → low | ACC-02 (0.666) |
| WEAK-49 | None → hardware | None → medium | NET-22 (0.644) |
| WEAK-50 | None → software | None → low | SW-13 (0.715) |

Pełne przewidywania, sąsiedzi, rozkłady etykiet, wersje bibliotek i metadane znajdują się w `report.json`.
Każda grupa jest wykluczana w całości z referencji. Nie ma oddzielnego testu końcowego.
Obecna aplikacja i jej baza nie są zmieniane przez ten skrypt.
