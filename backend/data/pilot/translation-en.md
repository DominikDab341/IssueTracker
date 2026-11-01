# Angielskie tłumaczenie pilotażu PL/EN

Data przygotowania: 2026-11-01. Zbiór: `pilot-en-v1`.

## Pliki i pochodzenie

- `tickets.json` i `review.md`: oryginalne polskie przykłady, zachowane bez zmian.
- `tickets.en.json`: angielskie tłumaczenia tych samych 40 przykładów.
- `review.en.md`: angielska wersja do czytania i sprawdzenia według ID.
- `results/`: zachowany pierwotny polski pomiar z 2026-10-28.
- `comparison/pl/` i `comparison/en/`: nowe pomiary wykonane tym samym skryptem.
- `comparison/report.md` i `comparison/report.json`: zestawienie wyników i zmian dla poszczególnych ID.

Źródłowy zbiór to `pilot-pl-v1`, SHA-256:
`b6f1137290e7a95cd0ad79cdac8ccff553049851958acfe98fc5120686a3b542`.
Pochodzenie polskich przykładów opisuje `generation.md`.

Tłumaczenie przygotował asystent Codex. Dokładny identyfikator modelu
tłumaczącego i parametry próbkowania nie są dostępne; zapisano je jako `null`.
Nie używano osobnej zewnętrznej usługi tłumaczeniowej. Tłumaczenia i etykiety
pozostają niezatwierdzone przez człowieka (`pending`).

Instrukcja tłumaczenia: przełożyć opis i uzasadnienia etykiet na angielski,
zachowując objawy, wpływ na pracę, liczbę osób, dostępne obejścia i przeczenia.
Nie dodawać nazw kategorii ani priorytetów do opisu i nie poprawiać treści pod
wyniki modelu. Zachować identyfikatory, grupy parafraz, proponowane etykiety
i checkbox. Powstała jedna wersja tłumaczenia przed sprawdzeniem jej wyników.

## Warunki porównania

Oba przebiegi używają `sentence-transformers/all-MiniLM-L6-v2`, snapshotu
`c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, CPU, kosinusa, `k=3`, głosowania
większościowego, tych samych etykiet i wykluczenia całej grupy ocenianego
incydentu (leave-one-group-out). Nie dostrajano parametrów ani progów.
Model otrzymuje wyłącznie pole `text`, bez uzasadnień, etykiet i checkboxa.

Polskie opisy są klasyfikowane względem polskich referencji, a angielskie
względem angielskich. Nie łączymy obu języków w jeden zbiór i nie dopuszczamy
tłumaczenia ocenianego przykładu ani jego parafrazy jako jego sąsiada.
To porównanie dwóch wersji językowych, nie test wyszukiwania między językami.

Wyniki pokazują zachowanie na tej konkretnej, małej próbce i jej tłumaczeniu.
Wpływu języka nie można całkowicie oddzielić od doboru słów w tłumaczeniu.
Nie jest to nowy niezależny zbiór ani końcowy test; wszystkie etykiety nadal
są propozycjami generatora. Jakość kategorii i priorytetu oceniamy osobno.
Pomiarów czasu pojedynczych przebiegów nie traktujemy jako benchmarku szybkości.

## Odtworzenie z katalogu głównego projektu

```powershell
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/pl
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.en.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/en
```

Skrypt domyślnie wymaga lokalnego cache modelu. Pobranie brakującego snapshotu
wymaga jawnego `--allow-download`. Parametr `--validate-only` sprawdza format
bez bazy i modelu. Bez `--output` angielskie raporty trafiają do `results-en/`,
a polskie do `results/` obok danych; pokazane wyżej polecenia zachowują
oryginalne raporty dzięki jawnym osobnym katalogom.

---

## Aktualizacja 2026-11-01 — 120 przypadków

Zbiory `tickets.json` i `tickets.en.json` rozszerzono do 120 odpowiadających sobie zgłoszeń, po 30 na kategorię. Użytkownik zatwierdził pierwotne 40 par; nowe 80 pozostaje `pending`. Fragmenty powyżej opisujące 40 niezatwierdzonych tłumaczeń dokumentują wcześniejszy stan.

Oryginalne pliki po 40 rekordów są w `snapshots/tickets.pl.40.v1.json` i `snapshots/tickets.en.40.v1.json`. Stan 120 rekordów tego pomiaru ma własne kopie `snapshots/tickets.pl.120.v2.json` i `snapshots/tickets.en.120.v2.json`.

Nowe wyniki dopisano do tych samych `comparison/pl/report.md`, `comparison/en/report.md` i `comparison/report.md`. Skrypty odtąd dopisują kolejne sekcje; stare JSON-y zachowują w `runs/`, a `report.json` wskazuje najnowszy przebieg. Po dwóch poleceniach pomiaru uruchom `backend/scripts/compare_pilot_languages.py`, aby dopisać porównanie.

Accuracy kategorii: PL 79,2%, EN 93,3%; macro-F1: PL 0,792, EN 0,933. Accuracy priorytetu bazowego: PL 40,8%, EN 49,2%; macro-F1: PL 0,424, EN 0,489. Protokół i pochodzenie nowej partii opisuje [expansion-120.md](expansion-120.md).

---

## Ostatnia partia: 170 opisów — 2026-11-01

Użytkownik zatwierdził również poprzednie 80 par, więc wcześniejsze 120 jest w całości approved. Dodano 50 krótkich opisów z wiernymi angielskimi odpowiednikami, z niezmienionym stopniem niejasności; nowe 50 pozostaje pending. Do obu języków stosujemy tę samą stałą referencję 120 w danym języku.

Brak etykiety zapisano jako null w obu wersjach: 20 kategorii i 40 priorytetów. Nie dopowiadano objawów ani wpływu w tłumaczeniu. Nowe opisy mają reference_eligible=false. Podstawą ich oceny jest 30 dostępnych kategorii i 10 dostępnych priorytetów, z osobną liczbą wymuszonych odpowiedzi.

Zachowano osobne kopie zatwierdzonych 120 oraz całych 170 w snapshots/. [Protokół ostatniej partii](weak-170.md) podaje wyniki i polecenia; dotychczasowe raporty uzupełniono na końcu.
