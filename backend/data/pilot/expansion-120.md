Yeah, prevention program is concerned alpha in another day spread Alice new one to kickoff# Rozszerzenie pilotażu do 120 zgłoszeń PL i EN

Data: 2026-11-01. Zbiory: `pilot-pl-v2-120` i `pilot-en-v2-120`.

## Zatwierdzenie i zachowane źródła

Użytkownik napisał w rozmowie: „zatwierdzam te przyklady”. Zapisano to jako
zatwierdzenie 40 istniejących przykładów w obu językach, z niezmienionymi
etykietami. Pole `review.reviewer` wskazuje autora pracy jako użytkownika;
czas zapisania decyzji to `2026-11-01T14:19:12+01:00`.
Nowe 80 par nie było wtedy dostępne i pozostaje `pending`.
Pomiar 120 przypadków używa `--labels proposed`, tak jak wcześniejszy pomiar
40 przypadków. Zatwierdzone etykiety tych 40 są zgodne z propozycjami.
Tryb `reviewed` nadal odmawia oceny wszystkich 120 do zakończenia przeglądu.

Kopie oryginalnych zbiorów przed zapisaniem zatwierdzenia i rozszerzeniem:

- `snapshots/tickets.pl.40.v1.json`, SHA-256 `b6f1137290e7a95cd0ad79cdac8ccff553049851958acfe98fc5120686a3b542`.
- `snapshots/tickets.en.40.v1.json`, SHA-256 `f4ed3f066ab8549781946f85c0f1794565332b16402b5b8cb6b60aa29763ecf0`.

Treści, ID, grupy, proponowane etykiety i checkboxy oryginalnych 40 przykładów
zachowano w aktualnych danych. Zmieniły się tylko ich metadane przeglądu.
Kopie stanu 120 przypadków dla tego pomiaru zapisano w
`snapshots/tickets.pl.120.v2.json` i `snapshots/tickets.en.120.v2.json`.

## Przygotowanie nowych przykładów

Nowe opisy i angielskie tłumaczenia przygotował asystent Codex, bez danych
rzeczywistej organizacji i bez osobnej zewnętrznej usługi generowania.
Dokładny identyfikator modelu i parametry próbkowania są niedostępne.
Nie należy deklarować powtarzalności generacji; odtwarzalne są zapisane pliki.

Instrukcja przygotowania: dodać po 20 krótkich, zróżnicowanych problemów IT do
każdej z czterech kategorii. W każdej nowej partii kategorii umieścić 4 low,
8 medium, 6 high i 2 critical. Opis ma sam zawierać objawy, wpływ na pracę
i informację o obejściu, bez dopisywania nazwy etykiety. Priorytet wynika
z definicji w `labeling-guide.md`. Utworzyć po dwie nowe pary opisujące ten
sam incydent w każdej kategorii, nadając wspólne `group_id`. Pozostałe rekordy
opisywać jako odrębne przypadki. Zachować jedną wierną wersję angielską każdego
opisu, bez zmiany etykiet, osób dotkniętych problemem i dostępnych obejść.
Wszystkie nowe decyzje przeglądu pozostawić niewypełnione.

Przygotowano jedną wersję danych przed oceną. Nie poprawiano tekstów na
podstawie uzyskanych przewidywań. Uzasadnienia etykiet zapisano osobno;
model otrzymuje wyłącznie pole `text`.

## Liczebności

- 120 rekordów na język, po 30 w kategorii.
- 108 grup incydentów: 12 par parafraz i 96 pojedynczych przypadków.
- Priorytety: 24 low, 48 medium, 36 high i 12 critical.
- Przegląd: 40 approved i 80 pending w każdym języku.
- Pary PL/EN mają identyczne ID, grupy, etykiety i checkboxy.

Stałe proporcje służą pokryciu scenariuszy i nie odzwierciedlają naturalnego
rozkładu zgłoszeń. Podobne objawy nie oznaczają automatycznie jednego incydentu;
grupy są częścią propozycji danych i także wymagają przeglądu autora.

## Pomiar i historia wyników

Zachowano snapshot MiniLM `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, k=3,
kosinus, głosowanie większościowe, CPU i wykluczenie całej grupy badanego
przykładu. Nie strojono parametrów ani progu. Języki mają osobne referencje.
Zarówno oceniana próbka, jak i pula referencyjna są większe niż poprzednio;
różnica 40/120 nie jest poprawą zmierzoną na stałym, niezależnym teście.

Kolejne wyniki są dopisywane na dole istniejących plików `report.md`.
`report.json` zawiera najnowszy pomiar; katalog `runs/` zachowuje pełne JSON-y
poprzednich i nowych przebiegów. W każdej dopisanej sekcji jest link do
właściwego JSON-u, aby starszy wynik nie był mylony z najnowszym.

```powershell
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/pl
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --dataset backend/data/pilot/tickets.en.json --revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf --output backend/data/pilot/comparison/en
.venv/Scripts/python.exe backend/scripts/compare_pilot_languages.py
```

Trzecie polecenie sprawdza zgodność źródeł i warunków, przelicza metryki
z przewidywań i dopisuje porównanie do `comparison/report.md`. Pokazuje też
osobno pierwotne 40 i nowe 80 przypadków przy puli sąsiadów bieżącego pomiaru.

---

## Późniejsze zatwierdzenie i ostatnia partia — 2026-11-01

Użytkownik następnie zatwierdził także nowe 80 przykładów opisane powyżej. Stan approved wszystkich 120 zapisano w snapshots/tickets.pl.120.approved.v2.json oraz snapshots/tickets.en.120.approved.v2.json. Historyczne pliki 120 przed tym zatwierdzeniem zachowano.

Zlecono ostatnią partię 50 słabo opisanych zapytań w obu językach. Aktualne pliki tickets.json i tickets.en.json zawierają 170 opisów, ale referencja nadal ma tylko 120. Nowe 50 pozostaje pending i nie podpowiada sobie nawzajem. Protokół, brakujące etykiety i wyniki znajdują się w [weak-170.md](weak-170.md).
