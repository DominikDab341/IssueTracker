# Końcowa partia pilotażu: 50 słabo opisanych zgłoszeń

Data: 2026-11-01. Zbiory: `pilot-pl-v3-170` i `pilot-en-v3-170`.

## Zakres i zatwierdzenie

Na prośbę użytkownika rozszerzanie bieżącego pilotażu kończymy na 170
przypadkach w każdym języku: 120 przykładów referencyjnych i 50 nowych
opisów testujących zachowanie przy małej ilości informacji. Wstępny rozmiar
300 z planu zastępujemy tym zakresem pilotażu. Jest to decyzja o zakresie;
93,3% na poprzednich syntetycznych danych nie dowodzi wystarczalności próby
ani jakości na rzeczywistych zgłoszeniach. Dane RAG i podział końcowej
ewaluacji pozostają osobnymi zadaniami.

Użytkownik napisał: „tamte tez moga byc potwierdzone”. Zatwierdzenie pozostałych
80 przykładów zapisano z czasem odnotowania `2026-11-01T14:35:52+01:00`.
Wszystkie wcześniejsze 120 jest approved, z niezmienionymi etykietami.
Nowe 50 par pozostaje pending, ponieważ nie było dostępne przy tej decyzji.

Zachowane stany:

- `snapshots/tickets.pl.120.v2.json` i `tickets.en.120.v2.json`: źródła poprzedniego pomiaru, przed zatwierdzeniem ostatnich 80.
- `snapshots/tickets.pl.120.approved.v2.json` i `tickets.en.120.approved.v2.json`: same 120 referencji po zapisaniu zatwierdzenia.
- `snapshots/tickets.pl.170.v3.json` i `tickets.en.170.v3.json`: pełny stan bieżącego pomiaru.

## Przygotowanie partii

Opisy i tłumaczenia przygotował asystent Codex; nie są to dane organizacji.
Dokładny identyfikator modelu generującego i parametry próbkowania nie są
dostępne. Przygotowano jedną wersję przed pomiarem, bez poprawiania przykładów
na podstawie przewidywań. Instrukcja: utworzyć 50 krótkich, potocznych i
niepełnych opisów po polsku oraz wierne odpowiedniki angielskie; zachować
negacje, objawy i podany wpływ na pracę. Gdzie informacji nie wystarcza,
nie wymyślać kategorii, przyczyny, obejścia ani priorytetu.

- 30 opisów pozwala zaproponować kategorię: 8 Konta i uprawnienia, 8 Sprzęt, 7 Sieć i łączność, 7 Oprogramowanie.
- 20 opisów jest zbyt ogólnych do ustalenia kategorii, np. „Nie działa”, „Znowu to samo”, „Pilne!!!”.
- 10 opisów pozwala zaproponować priorytet: 2 low, 3 medium, 3 high, 2 critical.
- 40 opisów nie zawiera wystarczających danych o wpływie lub obejściu do ustalenia priorytetu.

Brak etykiety zapisano jako null. Tak samo null w `work_blocked` oznacza brak
tej informacji w opisie. Jest to format danych eksperymentu, nie rozszerzenie
kontraktu formularza API. Każdy nowy przykład ma `description_quality=weak`
i `reference_eligible=false`. Pary językowe mają te same ID `WEAK-01`–`WEAK-50`,
grupy i adnotacje. Każdy opis ma własną grupę; łącznie jest 158 grup.

## Protokół pomiaru

KNN nadal ma k=3, kosinus, głosowanie większościowe i snapshot MiniLM
`c9745ed1d9f207416be6d2e6f8de32d1f16199bf`. Nie zmieniano modelu ani progów.
MiniLM dostaje tylko text. Dla referencji 120 nadal wyklucza się całą grupę
ocenianego incydentu. Nowe 50 jest oceniane względem stałych 120; nie trafia
do sąsiadów ani innych nowych zgłoszeń, ani poprzednich przykładów.

Dokładność liczymy osobno dla każdej etykiety, wyłącznie gdy da się ją
zaproponować na podstawie tekstu. Null nie jest błędem, sukcesem ani nową
klasą. Podajemy liczbę ocenionych i pominiętych przypadków, aby nie przedstawiać
wyników podzbioru jako accuracy na wszystkich 170.

Osobno raportujemy, ile etykiet model wymusił przy braku wystarczających
informacji. Obecny klasyfikator zawsze głosuje i nie ma progu odmowy;
to pomiar ograniczenia, bez strojenia mechanizmu na tej partii.

## Wyniki

| Zakres | Zadanie | Ocenione | Accuracy PL | Accuracy EN | Macro-F1 PL | Macro-F1 EN |
|---|---|---:|---:|---:|---:|---:|
| Nowe 50 | Kategoria | 30/50 | 76,7% | 96,7% | 0,772 | 0,966 |
| Nowe 50 | Priorytet bazowy | 10/50 | 40,0% | 90,0% | 0,367 | 0,914 |
| Całe 170 | Kategoria | 150/170 | 78,7% | 94,0% | 0,786 | 0,939 |
| Całe 170 | Priorytet bazowy | 130/170 | 40,8% | 52,3% | 0,428 | 0,529 |

Na dotychczasowych 120 odtworzono dokładnie wcześniejsze metryki: kategoria
PL 79,2%, EN 93,3%; priorytet PL 40,8%, EN 49,2%. Nowe opisy nie zmieniły
referencji. Bazowe stałe medium dla 130 ustalalnych priorytetów daje 39,2%
accuracy, macro-F1 0,141.

W obu językach klasyfikator nadał kategorię wszystkim 20 nieoznaczalnym
opisom i priorytet wszystkim 40 opisom z niewystarczającym wpływem. Tych
odpowiedzi nie można uznać za poprawne rozpoznania. Wynik 96,7% na 30 krótkich
opisach z rozpoznawalnym objawem nie obejmuje 20 opisów bez wystarczającej
informacji. Priorytet 90% pochodzi tylko z 10 takich przykładów.

Jest to ostatni przebieg tej serii pilotażu, nie niezależny końcowy test.
Tłumaczenia i nowe adnotacje oczekują na przegląd. Wnioski są ograniczone
syntetycznym pochodzeniem, niewielkimi podzbiorami i doborem słów.

## Pliki wyników i odtwarzanie

Wyniki dopisano na dole tych samych `comparison/pl/report.md`,
`comparison/en/report.md`, `comparison/report.md` i `results/report.md`.
Stare sekcje zachowano; JSON-y przebiegów są w `runs/` z odnośnikami w Markdown.

```powershell
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/pl
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.en.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/en
.venv/Scripts/python.exe backend/scripts/compare_pilot_languages.py
```
