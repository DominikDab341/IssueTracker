# Porównanie RAG na 22 osobnych pytaniach — 2026-11-16

Zestaw 30 pytań EN obejmuje [8 pytań walidacyjnych](validation-en-v1-report.md) i [22 pytania testowe](test-en-v1.json). Część testowa ma własny korpus 28 syntetycznych zgłoszeń. Przed uruchomieniem zapisano oczekiwane źródła, wymagane fakty i warunki zaliczenia. Zbiór testowy ma SHA-256 `cc2c156cdf1b814037d24efe26553cdd3d5922961010103dcacad7d30d68bbc3`.

Oba warianty korzystały z tego samego korpusu, modelu Qwen3 4B Instruct, promptu `rag-en-v2` i limitu pięciu źródeł. Zmieniano metodę wyszukiwania. W dwóch dopytaniach przekazywano historię z rzeczywistej wcześniejszej odpowiedzi danego wariantu. Pomiar wykonano na osobnym PostgreSQL/pgvector przez funkcję obsługi czatu przy użyciu konta Staff. [Surowe odpowiedzi, źródła, czasy i metadane](test-en-v1-results.json).

## Wyniki

| Wariant | Recall@5 | MRR@5 | Pytania z odpowiedzią | Pytania bez odpowiedzi | Razem |
|---|---:|---:|---:|---:|---:|
| Semantyczny | 1,00 | 1,00 | 13/16 | 6/6 | 19/22 |
| Pełnotekstowy | 1,00 | 1,00 | 13/16 | 6/6 | 19/22 |

Metryki wyszukiwania dotyczą 14 samodzielnych pytań z oczekiwanymi źródłami. W obu wariantach wszystkie wymagane zgłoszenia znalazły się w pierwszej piątce, a pierwsze trafne zgłoszenie było zawsze na pierwszej pozycji. Oba dopytania uzyskały pełną ocenę dzięki źródłom z historii.

Ocenę przeprowadził Codex według [rubryki](validation-rubric.md). Zaliczenie pytania z odpowiedzią wymaga wszystkich kluczowych faktów z właściwymi cytatami. Odpowiedzi częściowe dostały 1 punkt za kompletność i po 2 w pozostałych kryteriach. Przy pytaniach bez odpowiedzi oba warianty otrzymały po 2 punkty za wskazanie braku danych lub braku potwierdzonej naprawy bądź przyczyny.

| Pytanie | Semantyczne | Pełnotekstowe | Obserwacja |
|---|---|---|---|
| T01 | częściowa | zal. | Semantyka dała oba źródła. W opisie naprawy kalendarza desktopowego Qwen pominął nazwę strefy Europe/Warsaw. |
| T02 | zal. | zal. | Wskazano wyłączoną opcję w telefonie z #202. |
| T03 | zal. | częściowa | Pełny tekst zwrócił #204. Qwen opisał pobranie szablonu, pomijając otwarcie kopii lokalnie. |
| T04 | zal. | zal. | Wskazano wejście mikrofonowe nowego zestawu słuchawkowego z #206. |
| T05 | zal. | zal. | Oba warianty rozpoznały, że propozycja wymiany baterii w #208 pozostała nieprzetestowana. |
| T06 | częściowa | częściowa | Oba warianty podały osadzenie czcionek z #210 i pominęły ponowne wygenerowanie raportu. |
| T07 | zal. | zal. | Oba wskazały wymianę skrótu Findera i nowy adres SMB z #212. |
| T08 | zal. | zal. | Podano odsunięcie odbiornika na przedłużaczu USB z #213. |
| T09 | zal. | zal. | Zgłoszono brak rozwiązania dla dysku kopii zapasowych. |
| T10 | zal. | zal. | Podano wymianę podkładki z #214 i kalibrację czujnika z #215. |
| T11 | zal. | zal. | Nazwano właściwy czujnik z #215. |
| T12 | zal. | zal. | Oba warianty podały usunięcie importu i pomijanie powtórzonych identyfikatorów z #217. |
| T13 | zal. | zal. | Zgłoszono brak udokumentowanej naprawy przesyłania plików. |
| T14 | zal. | zal. | Oba wskazały nowego adresata powiadomień z #220. |
| T15 | zal. | zal. | Podano szablon 62 mm i kalibrację czujnika z #221. |
| T16 | zal. | zal. | Zgłoszono brak naprawy awarii przy uruchamianiu edytora. |
| T17 | zal. | zal. | Podano reset zapamiętanej pozycji okna z #223. |
| T18 | zal. | zal. | Podano czyszczenie danych witryny i zmianę zakładki z #224. |
| T19 | zal. | zal. | Wskazano brak ustalonej przyczyny. Restart aplikacji opisano jako przywrócenie działania z #225. |
| T20 | częściowa | częściowa | Podano format JPEG i limit 5 MB z #226. Oba warianty pominęły krok ponownego przesłania zdjęć. |
| T21 | zal. | zal. | Oba wskazały kalibrację ekranu dotykowego w ustawieniach Windows z #227. |
| T22 | zal. | zal. | Oba rozpoznały brak potwierdzonej naprawy połączeń przychodzących w sprawie telefonu w holu. |

Każda z niezaliczonych odpowiedzi była częściowa, mimo że właściwe źródło trafiło do kontekstu. Najczęściej brakowało ostatniego kroku naprawy. Na tym korpusie oba warianty znalazły wymagane źródła i uzyskały tyle samo zaliczeń. Zbiorów użyto w dwóch osobnych przebiegach na różnych korpusach, dlatego raport walidacji zachowuje osobne wyniki.

To jeden przebieg na syntetycznych danych. Wzorce odpowiedzi i oceny wymagają przeglądu autora przed wykorzystaniem w pracy. Scenariusze uprawnień, zapytania statystyczne i powtarzane pomiary czasów są poza zakresem tego przebiegu.

## Odtworzenie

Uruchom i zmigruj pustą bazę testową według [instrukcji walidacji](validation-en-v1-report.md#odtworzenie). Z katalogu głównego, przed zatrzymaniem bazy, uruchom:

```powershell
.venv/Scripts/python.exe backend/scripts/evaluate_rag_validation.py --dataset backend/data/rag/test-en-v1.json --output test-repeat.json
```

## Wniosek po końcowym teście 50 pytań — 2026-11-19

W pierwszym teście oba warianty zaliczyły po 19/22 pytań. W osobnym teście na 50 nowych pytaniach asystent zaliczył **46/50 (92%) z wyszukiwaniem pełnotekstowym** i **41/50 (82%) z semantycznym**. Przewaga dotyczyła jakości gotowych odpowiedzi. Na 31 samodzielnych pytaniach z udokumentowaną odpowiedzią obie metody uzyskały **Recall@5 = 1,00 i MRR@5 = 1,00**.

W pytaniu F46 obie metody zwróciły na pierwszym miejscu to samo zgłoszenie o dwóch czytelnikach o jednakowym nazwisku. Wariant pełnotekstowy poprawnie wskazał numer czytelnika jako sposób odróżnienia tych osób. Wariant semantyczny podał jako rozwiązanie wybór pierwszego pasującego nazwiska, chociaż w zgłoszeniu opisano to jako wcześniejszy błąd. [Pełny raport z ocenami 50 pytań i uzasadnieniem miar](final-en-v1-report.md).

Zachowujemy oba wyniki. **Wyszukiwanie semantyczne pozostaje domyślne w aplikacji.** Pięć dodatkowych zaliczeń w jednym przebiegu na syntetycznych pytaniach to zbyt mało, by uzasadnić zmianę konfiguracji. Przed wykorzystaniem wyników w pracy autor powinien przejrzeć wzorce odpowiedzi i oceny zgodnie z [przyjętą rubryką](validation-rubric.md).
