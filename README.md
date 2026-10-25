# IssueTracker

Backend prototypu klasyfikacji zgłoszeń: FastAPI, PostgreSQL/pgvector,
`all-MiniLM-L6-v2` i FastAPI `BackgroundTasks`. Zaimplementowano fundament API
etapu 1 oraz przetwarzanie, edycję i ponowienia z etapu 2. Pełne domknięcie
E1.5, E1.9, E2.8 i E2.9 wymaga ról, przypisań i ich testów z etapu 3;
E2.5 wymaga jeszcze testu ręcznej korekty kategorii z E5.13. Użytkownicy,
uwierzytelnianie, role i przypisania powstaną w etapie 3; obecne API jest
przeznaczone do lokalnego uruchamiania deweloperskiego.

## Uruchomienie przez Docker Compose

Wymagany działający Docker Desktop z kontenerami Linux. Polecenia wykonuj
z katalogu repozytorium. Nie nadpisuj istniejącego `.env.docker`:

```powershell
if (-not (Test-Path .env.docker)) { Copy-Item .env.docker.example .env.docker }
```

W nowym pliku ustaw własne hasło spójnie w `POSTGRES_PASSWORD` i
`DATABASE_URL`. Zmienne `POSTGRES_*` inicjalizują tylko pusty wolumen;
przy istniejącej bazie użyj jej dotychczasowych danych dostępu.
Dockerfile instaluje PyTorch dla CPU. Celery, Redis i Flower zostały usunięte.
Stare pole `CELERY_BROKER_URL` w lokalnym pliku jest ignorowane i można je usunąć;
istniejących plików z danymi dostępu nie nadpisujemy.

```powershell
docker compose build api
docker compose up -d postgres
docker compose run --rm api python -m alembic -c app/alembic.ini upgrade head
docker compose run --rm api python scripts/seed_db.py
docker compose up -d api --remove-orphans
```

Migracje Alembic są jedynym sposobem tworzenia i zmiany schematu.
Seed dodaje 10 dawnych angielskich przykładów do pustej tabeli zgłoszeń
oraz uzupełnia osobną tabelę referencji KNN z `data/sample_tickets.json`.
Nie tworzy schematu i nie nadpisuje istniejących zgłoszeń ani referencji. Kategorie
`bug`, `performance`, `feature` pozostają na tym etapie; polski zbiór
helpdesku IT powstanie później. Pierwsze pobranie tokenizera i modelu
wymaga dostępu do Hugging Face. Model jest ładowany leniwie w wątku procesu API.

API: [Swagger](http://localhost:8000/docs). PostgreSQL jest dostępny lokalnie
na porcie 5433. `docker compose stop` zatrzymuje usługi, zachowując dane.

## Istniejące dane i migracja statusów

Migracja zatrzymuje się przed zmianami, jeśli istnieją rekordy i nie
podano jawnego mapowania wszystkich występujących starych statusów.
Najpierw sprawdź rekordy i ustal znaczenie `open`, `resolved`, `closed`.
Nie zakładamy, że `closed` oznacza rozwiązanie, odrzucenie lub anulowanie.

Dla sprawdzonych 10 rekordów demonstracyjnych użytkownik zatwierdził
zachowanie danych i `open → reported`. Dla takiej bazy zamiast zwykłego
`upgrade head` użyj:

```powershell
docker compose run --rm api python -m alembic -c app/alembic.ini -x 'legacy_status_map={"open":"reported"}' upgrade head
```

Identyfikatory, treści, kategorie, priorytety, daty i embeddingi pozostają
zachowane. Autorów nie dopisujemy; ich migracja wymaga decyzji przed
etapem 3. Rekordy bez dat zatrzymują migrację zamiast otrzymywać
zmyślone daty. Cofnięcie migracji statusów z niepustą tabelą jest
blokowane, aby nie utracić informacji o procesie i notatek.

Migracja `e2a000000001` dodaje zadania, checkbox (domyślnie `false`), wersję
treści (1) oraz źródła priorytetu. Istniejący embedding otrzymuje wersję 1;
nie tworzymy fikcyjnych dawnych zadań ani bazowego przewidywania KNN.
Dotychczasowy priorytet ma źródło `legacy`. Zachowanie wszystkich starych
pól 10 rekordów, w tym dat i wektorów, zweryfikowano sumą kontrolną.
Cofnięcie tej migracji z niepustą tabelą również wymaga osobnego planu danych.

Migracja `e5a000000001` tworzy osobną tabelę `classification_references`.
Nie kopiuje do niej istniejących spraw ani ich końcowych priorytetów.
Po migracji uruchom ponownie `scripts/seed_db.py`: uzupełni demonstracyjną
referencję bez zmiany dotychczasowych zgłoszeń. Każdy przykład zachowuje
tekst, kategorię, priorytet bazowy, embedding oraz źródło i klucz w zbiorze.
Bez referencji klasyfikacja kończy się poprawnie wynikiem `unknown` i
tymczasowym priorytetem `medium`, z zachowaniem checkboxa i decyzji ręcznej.

## Uruchomienie lokalne i testy

Wymagany Python 3.12 lub 3.13. Utwórz środowisko i zainstaluj zależności:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Ustaw w `.env` dostęp do bazy na `localhost:5433`, zgodny z konfiguracją
kontenera PostgreSQL. Migracje i seed:

```powershell
.venv/Scripts/python.exe -m alembic -c app/alembic.ini upgrade head
.venv/Scripts/python.exe scripts/seed_db.py
.venv/Scripts/python.exe -m uvicorn app.api.main:app
```

Dla starej bazy dodaj zatwierdzone `-x legacy_status_map` jak wyżej.
Wspierany jest jeden proces API bez `--workers` i bez `--reload`.
Przed lokalnym uruchomieniem zatrzymaj API Compose, jeśli korzysta z tej samej bazy.

Testy używają standardowego `unittest` i klienta `httpx`. Uruchamiaj je
na osobnym kontenerze, który korzysta z tymczasowego systemu plików,
bez wolumenu `pgdata`. Dane testowe znikają po zatrzymaniu kontenera:

```powershell
docker compose -p issuetracker-tests -f docker-compose.test.yml up -d --wait
$env:TEST_DATABASE_URL='postgresql+asyncpg://issuetracker_test:test-only@127.0.0.1:5434/issuetracker_test'
.venv/Scripts/python.exe -c "from app.services.text_validation import get_tokenizer; get_tokenizer()"
$env:HF_HUB_OFFLINE='1'
.venv/Scripts/python.exe -m unittest discover -s tests -v
docker compose -p issuetracker-tests -f docker-compose.test.yml down
Remove-Item Env:HF_HUB_OFFLINE
Remove-Item Env:TEST_DATABASE_URL
```

Testy odmawiają uruchomienia bez `TEST_DATABASE_URL` lub przy nazwie bazy
innej niż `issuetracker_test`. Czyszczą wyłącznie jawnie wskazaną bazę
testową. Sprawdzają API na prawdziwym PostgreSQL/pgvector oraz tokenizer
modelu. Testy obejmują także pełny potok zadania z kontrolowanym wynikiem
modelu, rzeczywiste zapytania pgvector, błędy obliczeń i zapisu, ponowienia,
wyścigi edycji/statusu, wersjonowanie i brak blokowania pętli API. Test procesu
uruchamia prawdziwy Uvicorn z powolnym testowym encoderem, odbiera HTTP przed
ukończeniem obliczeń, zabija proces, uruchamia go ponownie i ponawia zadanie.
Oddzielnie sprawdzono dwa kolejne zadania z rzeczywistym MiniLM i embeddingami
384. To weryfikacja integracji, bez oceny jakości klasyfikatora.

Osobne testy regresji nie wymagają PostgreSQL ani pobierania modelu:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_migration_isolation tests.test_request_validation tests.test_processing_diagnostics -v
```

Sprawdzają cel migracji niezależnie od kolejności importów, brak blokowania
API podczas tokenizacji oraz diagnostykę błędów bez ujawniania danych.
Migracje testowe otrzymują jawny adres bazy i przed zmianą schematu
potwierdzają przez PostgreSQL, że połączono się z `issuetracker_test`.

## Kontrakt API po etapach 1–2

- `POST /tickets/`: `{"text":"Nie działa drukarka.","work_blocked":true}`,
  odpowiedź 201 z polami `ticket` i `task_id` (UUID). Checkbox jest opcjonalny,
  domyślnie `false`; `true` od razu nadaje `critical`. Zgłoszenie i zadanie
  `pending` zapisują się w jednej transakcji przed dodaniem `BackgroundTasks`.
- `GET /tickets/{id}`: szczegóły lub 404.
- `GET /tickets/`: lista z `limit` (1–100, domyślnie 20), `offset`
  (od 0), opcjonalnymi `status`, `category`, `priority`. Sortowanie
  `created_at DESC, id DESC` rozstrzyga jednakowe daty. Odpowiedź pozostaje
  listą. Kategoria jest dokładnym dopasowaniem; priorytety to `low`,
  `medium`, `high`, `critical` oraz prototypowe `unknown`.
- `PATCH /tickets/{id}/status`: jedno miejsce zmiany statusu.
  `resolved` wymaga `resolution_note`, `rejected` wymaga
  `rejection_reason` (niepuste, do 2000 znaków). Notatki i czas decyzji
  zapisują się razem ze statusem. Autorzy decyzji powstaną w etapie 3.
- `DELETE /tickets/{id}` pozostaje oznaczonym jako przestarzały aliasem
  zakończenia sprawy. Wymaga jawnego ciała z końcowym `status` i notatką,
  gdy jest wymagana; korzysta z tej samej macierzy i sesji bazy co PATCH.
  Nie usuwa rekordu. Wywołanie bez ciała daje 422. Zachowuje odpowiedź
  `ticket`, `status`, `suggested_duplicates`; bez aktualnego embeddingu sugestie są puste.
- `GET /tickets/{id}/task/{task_id}` zachowuje adres, a stan odczytuje z PostgreSQL.
  Odpowiedź: `task_id`, `state` (`pending`, `running`, `succeeded`, `failed`),
  `content_version`, `current`, `created_at`, `started_at`, `finished_at`,
  `result`, `error`, `error_code`. Brak zadania lub inne zgłoszenie daje 404.
  `result` zawiera kategorię i priorytety bazowy/automatyczny, bez wektora;
  końcowy priorytet odczytuj ze szczegółów zgłoszenia (checkbox może się zmienić).
  Błąd jest bezpiecznym polskim komunikatem, bez tekstu zgłoszenia i surowego wyjątku.
- `POST /tickets/{id}/classification/retry`: 202, `ticket` i nowy `task_id`.
  Dozwolone wyłącznie dla aktualnej wersji aktywnego zgłoszenia z zadaniem
  `failed` o kodzie `processing_failed` albo `interrupted`. Pozostałe przypadki
  dają 409, w tym poprawnie zakończone zadanie z pustą referencją i wynik `unknown`.
  Równoległe ponowienia tworzą jedno zadanie. Status sprawy pozostaje bez zmian.
- `PATCH /tickets/{id}`: opis `text` i/lub logiczne `work_blocked`, odpowiedź
  `ticket` i `task_id`. Wyłącznie status `reported`, inaczej 409. Inny opis
  zwiększa `content_version` i tworzy nowe zadanie; taki sam opis nie uruchamia
  klasyfikacji. Poprzedni wektor pozostaje historycznie, ale `classification_current`
  jest `false`, dopóki embedding nie odpowiada bieżącej wersji. Nieaktualne
  wektory są wykluczone z duplikatów. KNN korzysta z osobnej referencji. Sam checkbox
  przelicza priorytet bez nowego zadania i embeddingu. Puste żądanie i `null` dają 422.

Priorytet końcowy respektuje kolejność: zapisane `manual_priority`, checkbox,
`automatic_priority`, tymczasowe `medium`. API ujawnia `priority_source` i
`base_priority`; formularz nie pozwala zmieniać ręcznej decyzji. Pole ręcznej
decyzji jest przygotowane i chronione przed zadaniem, ale endpoint administratora,
historia decyzji i korekta kategorii należą do etapu 5. Kontrola ról i własności
edycji/ponowień pozostaje blockerem etapu 3; obecnie API nie ma autoryzacji.

KNN przewiduje kategorię i priorytet bazowy wyłącznie z `classification_references`.
Nowe zgłoszenia, wyniki klasyfikacji, checkbox, zmiany priorytetu i statusu
nie rozszerzają ani nie zmieniają referencji. Priorytet bazowy `critical`
pozostaje prawidłową etykietą; końcowe `critical` nadane checkboxem innej
sprawy nie staje się etykietą bazową kolejnych zgłoszeń. Zbiór demonstracyjny
nie ma jeszcze oceny jakości; docelowe zatwierdzanie etykiet rozwiązanego
zgłoszenia przez uprawnioną osobę pozostaje w etapie 5.

| Wartość API | Nazwa polska | Dozwolone następne statusy |
|---|---|---|
| `reported` | Zgłoszony | `accepted`, `rejected`, `cancelled` |
| `accepted` | Przyjęty | `in_progress`, `rejected` |
| `in_progress` | W trakcie | `resolved`, `rejected` |
| `resolved` | Rozwiązany | Brak |
| `rejected` | Odrzucony | Brak |
| `cancelled` | Anulowany | Brak |

Blokada wiersza w transakcji zabezpiecza równoległe zmiany statusu.
Końcowe zgłoszenia pozostają w historii; powrót problemu wymaga nowego
zgłoszenia. Reguły ról i przypisań będą egzekwowane w etapie 3, także
przez przestarzały alias DELETE. Zmiana statusu nie uruchamia klasyfikacji.
Duplikaty uwzględniają trzy aktywne statusy. Stara eskalacja procentowa
została usunięta. Eskalację podobnych aktywnych zgłoszeń w oknie czasowym
dołączymy po wdrożeniu kont, aby liczyć różne osoby zamiast liczby rekordów.
Strojenie KNN i docelowa eskalacja nadal wymagają etapu 5.

Opis zgłoszenia nie może być pusty i ma limit **256 tokenów z tokenami
specjalnymi**, sprawdzany tokenizerem `sentence-transformers/all-MiniLM-L6-v2`
bez obcinania. To limit z `sentence_bert_config.json`; tokenizer BERT podaje
512, co przekracza wejście używane przez SentenceTransformer. Skrajne białe
znaki są usuwane. Techniczna granica 10000 znaków ogranicza rozmiar wejścia.
Operacje na zgłoszeniach nie zwracają embeddingów. Błędy: 404 — brak
zgłoszenia, 409 — niedozwolone przejście, 422 — walidacja danych,
503 — niedostępny tokenizer. Komunikaty są po polsku.
Ładowanie tokenizera i sprawdzanie limitu tokenów odbywają się w wątku,
przed operacjami zapisu; nie blokują pętli obsługującej żądania API.

## Organizacja kodu

- `app/api/main.py` składa aplikację, zarządza jej cyklem życia i tłumaczy błędy na HTTP.
- `app/api/schemas.py` definiuje kontrakt żądań i odpowiedzi, a `app/api/tickets.py` endpointy.
- `app/services/tickets.py` zawiera operacje na zgłoszeniach i granice transakcji; nie zależy od FastAPI ani modeli żądań.
- `app/services/tasks.py` współdzieli zapis zadań i blokady z wykonawcą `ProcessingRuntime`.
- `app/domain.py` definiuje priorytety, źródła, stany zadań i typowany wynik klasyfikacji.
- `determine_priority()` w `app/services/priorities.py` jest czystą funkcją. Osobna funkcja zapisuje jej decyzję na zgłoszeniu.

`ProcessingRuntime` otrzymuje asynchroniczną funkcję klasyfikującą w konstruktorze.
Pozwala to testować wykonawcę z kontrolowanym klasyfikatorem bez podmieniania
importów modułu. Testy reguł priorytetu nie wymagają bazy ani modelu:

```powershell
.venv/Scripts/python.exe -m unittest tests.test_priorities -v
```

Refaktoryzacja zachowuje reguły biznesowe i format odpowiedzi API; nie wymaga
nowej migracji schematu. Historyczne migracje zachowują własne, stałe wartości.

## Proces API i przerwane zadania

Jeden proces obsługuje żądania i zadania, z semaforem ograniczającym klasyfikację
do jednego zadania naraz. Model jest ładowany i wykonuje embedding w wątku,
z blokadą współdzielenia; zadania mają własne sesje bazy. Błędy modelu/zapisu
zapisują `failed`; wynik i `succeeded` zatwierdzane są razem. Wynik starszej
wersji, zastąpionego zadania lub zakończonej sprawy nie nadpisuje zgłoszenia.
Log błędu zawiera identyfikator zadania, etap, typ wyjątku i miejsca wywołań.
Nie zawiera komunikatu wyjątku, parametrów SQL ani wartości zmiennych lokalnych.

Dedykowane połączenie PostgreSQL utrzymuje sesyjną blokadę doradczą procesu.
Drugi proces dla tej samej bazy odmawia startu przed zmianą stanów zadań.
Po uzyskaniu blokady nowy proces oznacza pozostałe `pending`/`running` jako
`failed` z kodem `interrupted`. Użytkownik ponawia je jawnie przez API.
Utrata połączenia z blokadą uniemożliwia rozpoczęcie kolejnych obliczeń;
po awarii bazy, która uniemożliwi także zapis błędu, stan rozpozna następny start.

`BackgroundTasks` nie jest trwałą kolejką: zapis rekordu sam nie uruchamia
wykonania, nie ma automatycznych ponowień ani wznawiania po restarcie.
Przy normalnym zatrzymaniu Uvicorn czeka na zadania; wymuszone przerwanie
pozostawia stan do rozpoznania przy kolejnym starcie. Cache/pobieranie modelu
nie ma jeszcze osobnego wolumenu ani przypiętej wersji (E9.5).

Formalny opis pracy należy ujednolicić z wdrożoną, zatwierdzoną zmianą
Celery na FastAPI `BackgroundTasks` i powyższymi ograniczeniami.
