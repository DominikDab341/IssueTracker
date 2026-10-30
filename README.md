# IssueTracker

## Struktura projektu

```text
IssueTracker/
├── frontend/                 # React, TypeScript, Vite i Nginx
├── backend/
│   ├── app/                  # FastAPI, modele, serwisy i migracje Alembic
│   ├── data/                 # Dane demonstracyjne
│   ├── scripts/              # Administrator, import i seed
│   ├── tests/                # Testy backendu
│   ├── .env.example          # Wzór konfiguracji lokalnej
│   ├── .env.docker.example   # Wzór konfiguracji Compose
│   ├── Dockerfile
│   └── requirements*.txt
├── docker-compose.yml
├── docker-compose.test.yml
└── README.md
```

Polecenia poniżej wykonuj z katalogu głównego projektu, chyba że blok
jawnie zmienia katalog. Lokalne środowisko Pythona `.venv/` pozostaje
w katalogu głównym; frontend ma własne zależności w `frontend/node_modules/`.
Konfiguracja backendu znajduje się w `backend/.env` i `backend/.env.docker`.
Dotychczasowe pliki konfiguracji przeniesiono razem z backendem.

Prototyp klasyfikacji zgłoszeń: React, FastAPI, PostgreSQL/pgvector,
`all-MiniLM-L6-v2` i FastAPI `BackgroundTasks`. Zaimplementowano fundament API
etapu 1, przetwarzanie z etapu 2 oraz użytkowników, JWT, role i przypisania
z etapu 3. E1.5, E1.9, E2.8 i E2.9 obejmują już kontrolę osób i uprawnień.
E2.5 domknięto przez rozdzielenie przewidywania KNN i ręcznej korekty kategorii
oraz testy jej zapisu podczas klasyfikacji.
Etap 6 dodaje polski frontend React z obsługą kont i procesu zgłoszeń.
Endpoint LLM powstanie w kolejnych etapach.

## Polski pilotaż danych (etap 4)

W `backend/data/pilot/` znajduje się 40 syntetycznych zgłoszeń, po 10 na
docelową kategorię, [instrukcja etykietowania](backend/data/pilot/labeling-guide.md)
i [podgląd do ręcznego przeglądu](backend/data/pilot/review.md).
Etykiety są propozycjami generatora, wszystkie rekordy oczekują na przegląd autora.
Pochodzenie, instrukcje generowania i brakujące metadane opisano w `generation.md`.

```powershell
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --validate-only
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py
```

Skrypt korzysta domyślnie z lokalnego cache modelu; `--allow-download` pozwala
go pobrać. Nie wymaga PostgreSQL. Ocena wyklucza całą grupę parafraz badanego
przykładu, używa dotychczasowego `k=3` i nie stroi parametrów. Raporty znajdują
się w [backend/data/pilot/results/](backend/data/pilot/results/report.md).
Pierwszy przebieg na propozycjach: accuracy kategorii **60%**, priorytetu bazowego
**37,5%** (stałe `medium`: **40%**). To diagnostyka małej syntetycznej próbki,
nie końcowy wynik badawczy ani potwierdzenie poprawności etykiet.
Słownik pilotażu i jego wyniki nie zmieniają aplikacji ani danych demonstracyjnych.
Po ręcznym przeglądzie tryb `--labels reviewed` używa zatwierdzonych etykiet
i odmawia oceny, jeśli jakiś rekord pozostaje `pending`.

Testy pilotażu, bez bazy i modelu:

```powershell
Push-Location backend
../.venv/Scripts/python.exe -m unittest tests.test_pilot_dataset -v
Pop-Location
```

## Aplikacja React (etap 6)

Frontend w `frontend/` obejmuje rejestrację, logowanie, listę z filtrami
i paginacją, tworzenie i edycję, szczegóły, sugestie duplikatów oraz działania
zależne od roli. Obsługa przyjmuje sprawę, rozpoczyna i kończy realizację
z notatką, koryguje kategorię; administrator przypisuje wykonawcę i priorytet.
Panel „Użytkownicy” pozwala akceptować konta z jawną rolą i zarządzać ich
aktywnością. Autorzy i wykonawcy w szczegółach mają identyfikatory kont;
wybór wykonawcy przez administratora pokazuje też e-mail.

Po przygotowaniu bazy, migracji i pierwszego administratora zgodnie z dalszą
instrukcją uruchom API, a w drugim terminalu (Node.js 22.12+):

```powershell
cd frontend
npm ci
npm run dev
```

Aplikacja: [React lokalnie](http://127.0.0.1:5173). Domyślny adres API to
`http://localhost:8000`; opcjonalnie ustaw `VITE_API_URL` w `frontend/.env`
według `frontend/.env.example`, następnie uruchom ponownie Vite.
Pierwszy administrator nadal powstaje komendą `backend/scripts/create_admin.py`.
Rejestracja pobiera wymaganą domenę z publicznego `GET /auth/config`;
nie wymaga osobnej kopii tej konfiguracji we frontendzie.

W Compose, po migracjach i konfiguracji kont:

```powershell
docker compose up -d --build api frontend
```

Aplikacja: [React w Compose](http://localhost:3000). Frontend jest zbudowanym
pakietem statycznym serwowanym przez Nginx. Żądania `/api/` są przekazywane do
usługi `api:8000`, a bezpośrednie wejście na adres szczegółów obsługuje routing
SPA. Przeglądarka nie musi rozwiązywać kontenerowej nazwy `api`.
Dozwolone originy backendu są jawne: localhost i 127.0.0.1 na portach 5173
oraz 3000. Inne adresy podaj w `CORS_ORIGINS` jako tablicę JSON; konfiguracja
nie wymaga migracji ani zmiany istniejących danych.

Token i dane sesji są przechowywane wyłącznie w pamięci. Wylogowanie,
wygaśnięcie i odświeżenie strony wymagają ponownego logowania. Odpowiedź 401
kończy sesję; 403, 404, 409, walidacja i niedostępność API mają polskie komunikaty.
Bieżące konto odświeżamy przy powrocie do okna i co 30 sekund. Backend nadal
sprawdza uprawnienia przy każdym żądaniu. Szczegóły aktywnego zadania są
odpytywane co 3 sekundy, bez nakładających się żądań. Odpytywanie kończy się
po zakończeniu, błędzie API lub opuszczeniu widoku; odświeżenie jest jawne.

Rozszerzenia API dla frontendu:

- `GET /tickets/{id}/duplicates`: sugestie bez zmiany sprawy, z dotychczasową
  polityką widoczności i wykluczeniem nieaktualnych embeddingów.
- `GET /admin/assignees?limit=100&offset=0`: tylko aktywna, zaakceptowana obsługa;
  dostęp administratora, odpowiedź zawiera wyłącznie `id` i `email`.
- `GET /tickets/?needs_review=true|false`: filtr dla obsługi i administratora.
- Odczyty zgłoszeń zawierają `needs_review` i `current_task_state`. Zgłoszenie
  i stan zadania są odczytywane jednym zapytaniem, aby zakończone zadanie nie
  było pokazywane ze starszym wynikiem klasyfikacji.

**Pominięte zależności etapów 4–5:** docelowy słownik kategorii, próg pewności
KNN, zatwierdzanie referencji, strojenie i eskalacja. Interfejs używa obecnych
`bug`/`performance`/`feature`, wyświetlanych jako Błąd/Wydajność/Nowa funkcja.
„Do weryfikacji” oznacza obecnie kategorię `unknown`, również podczas oczekiwania
na obliczenia. Stan zadania i status sprawy są prezentowane osobno. Nie jest to
jeszcze ocena pewności oparta na walidacji. Duplikaty zachowują dotychczasowe
obliczenia i są sugestiami z odnośnikami, bez automatycznej decyzji.

Weryfikacja frontendu:

```powershell
cd frontend
npm run build
npm test
```

Testy obejmują macierz działań, ochronę sesji i wygasanie, polskie błędy,
odpytywanie oraz przerwanie żądań po opuszczeniu widoku. Testy integracyjne
kontraktu React znajdują się w `backend/tests/test_frontend_contract.py` i uruchamiają
się z pozostałymi testami backendu na `issuetracker_test`.
Weryfikacja etapu 6: **91/91 testów backendu, 11/11 testów React**, build
TypeScript/Vite i obrazu Docker frontendu; `npm audit` bez zgłoszonych podatności.

Powtarzalny test w przeglądarce, **wyłącznie na tymczasowej bazie testowej**:
uruchom kontener z `docker-compose.test.yml` jak w sekcji testów, ustaw
`TEST_DATABASE_URL`, a następnie:

```powershell
Push-Location backend
../.venv/Scripts/python.exe -m tests.frontend_server
Pop-Location
# W drugim terminalu uruchom frontend: cd frontend; npm run dev
```

Ten pomocnik zeruje wyłącznie `issuetracker_test`, zakłada konta
`reporter@mail.com`, `staff@mail.com`, `admin@mail.com` z testowym hasłem
`test-password-for-browser` i korzysta z kontrolowanego encodera.
Nie uruchamiaj go równolegle z unittest ani zwykłym API na porcie 8000.
W przeglądarce sprawdzono utworzenie, edycję checkboxa, sugestie i odnośniki
duplikatów, przyjęcie przez obsługę, korektę kategorii, rozpoczęcie i rozwiązanie
z notatką oraz odczyt rozwiązania przez autora bez możliwości edycji/anulowania.
Ten test sprawdza integrację aplikacji; nie ocenia jakości MiniLM.

## Konta, logowanie i uprawnienia (etap 3)

W `backend/.env` (lokalnie) lub `backend/.env.docker` (Compose) dodaj:

```dotenv
ALLOWED_EMAIL_DOMAIN=mail.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_SECRET_KEY=
```

Wygeneruj własny sekret poleceniem
`python -c "import secrets; print(secrets.token_urlsafe(48))"` i zapisz go
jako `JWT_SECRET_KEY`. API odmawia startu bez sekretu o długości co najmniej
32 bajtów. Nie używaj sekretów testowych. Nie nadpisuj istniejących plików
środowiska. Po zmianie zależności zainstaluj `backend/requirements-dev.txt` albo
przebuduj obraz API.

Po migracjach utwórz pierwszego administratora:

```powershell
.venv/Scripts/python.exe backend/scripts/create_admin.py --email admin@mail.com
# W Compose (interaktywny terminal):
docker compose run --rm api python scripts/create_admin.py --email admin@mail.com
```

Wybierz jeden wariant zgodny ze sposobem uruchomienia. Komenda dwukrotnie pyta
o hasło bez wyświetlania go; hasło ma mieć 12–128 znaków i jest zapisywane jako
hash Argon2id. Komenda nie przyjmuje hasła w argumentach, nie nadpisuje kont
i odmawia utworzenia kolejnego pierwszego administratora, również gdy istniejący
administrator jest nieaktywny. Nowe konta przechodzą rejestrację i akceptację.

| Endpoint | Działanie |
|---|---|
| `POST /auth/register` | JSON `email`, `password`; 201, konto aktywne, oczekujące, bez roli |
| `POST /auth/token` | Formularz OAuth2: `username` zawiera e-mail, `password` hasło; JWT tylko dla zaakceptowanych, aktywnych kont |
| `GET /users/me` | Bieżące konto, bez hasha hasła |
| `GET /admin/users?pending=true` | Lista oczekujących; filtr opcjonalny, `limit` 1–100 i `offset` od 0 |
| `POST /admin/users/{id}/approve` | JSON `role`: obowiązkowo `reporter`, `staff` albo `admin`; atomowa akceptacja z autorem i czasem |
| `PATCH /admin/users/{id}/role` | Osobna późniejsza zmiana roli zatwierdzonego konta |
| `PATCH /admin/users/{id}/active` | JSON `is_active`: aktywacja/dezaktywacja; nie zmienia akceptacji |
| `PATCH /tickets/{id}/assignee` | Administrator wskazuje `assignee_id` aktywnego, zaakceptowanego konta `staff` |
| `GET /tickets/{id}/assignments` | Historia przypisań dla obsługi i administratora |
| `PATCH /tickets/{id}/priority` | Administrator podaje `priority`: `low`, `medium`, `high`, `critical` |
| `PATCH /tickets/{id}/category` | Aktualny wykonawca lub administrator podaje `category` (`bug`, `performance`, `feature`) i wymagane `expected_content_version` z odczytanego zgłoszenia |

Adres jest walidowany składniowo i normalizowany do małych liter. Domena
rejestracji musi być dokładnie zgodna z konfiguracją; subdomeny i nazwy
zawierające `mail.com` nie wystarczają. Nie weryfikujemy własności skrzynki
e-mailem. Zmiana dozwolonej domeny dotyczy nowych rejestracji; dotychczasowe
konta zachowują możliwość logowania. Rejestracja zabrania pól roli, akceptacji
i aktywności. Akceptacja wymaga jawnej roli, a druga równoległa decyzja zwraca
409 i nie zmienia pierwszej. Reset hasła pozostaje poza zakresem.

Token używa HS256, ma `sub` z identyfikatorem konta, `iat`, `exp`, wystawcę
i odbiorcę. Nie zawiera hasła ani roli. Każde chronione żądanie odczytuje
rolę, aktywność i akceptację z bazy. Brak lub błędny/wygasły token daje 401
z `WWW-Authenticate: Bearer`; nieaktywne i niezaakceptowane konto oraz
niedozwolona operacja dają 403. Cudze zgłoszenie dla zgłaszającego daje 404,
również przy odczycie zadania.

Kontrakt dla przyszłego frontendu: logowanie formularzem OAuth2, następnie
`Authorization: Bearer <access_token>`; token przechowywany w pamięci aplikacji,
usuwany przy wylogowaniu. Wygaśnięcie i odświeżenie strony wymagają ponownego
logowania. Nie ma refresh tokenów ani endpointu wylogowania. Token wygasa po
30 minutach (konfigurowalne), a zmiany roli i dezaktywacja obowiązują również
wcześniej wydane tokeny. Ponowna aktywacja przywraca możliwość korzystania
z niewygasłego tokenu.

| Operacja | Zgłaszający (`reporter`) | Obsługa (`staff`) | Administrator (`admin`) |
|---|---|---|---|
| Lista, szczegóły i stan zadania | Własne | Wszystkie | Wszystkie |
| Utworzenie zgłoszenia | Jako zalogowany autor | Jako zalogowany autor | Jako zalogowany autor |
| Edycja opisu i checkboxa | Własne, tylko `reported` | Własne, tylko `reported` | Własne, tylko `reported` |
| Anulowanie | Własne, `reported`, bez wykonawcy | Takie same zasady autora | Takie same zasady autora |
| Samodzielne przyjęcie | Brak | `reported` → `accepted`, sam zostaje wykonawcą | Wskazuje osobę obsługującą przez `/assignee` |
| Przypisanie i zmiana wykonawcy | Brak | Brak | Aktywne zgłoszenia, historia poprzedniego i nowego wykonawcy |
| Rozpoczęcie i rozwiązanie | Brak | Aktualny wykonawca | Każde zgłoszenie, z zachowaniem kolejności statusów |
| Odrzucenie | Brak | Tylko z `reported` | Z każdego aktywnego statusu |
| Ponowienie błędnej klasyfikacji | Własne `reported`, bez wykonawcy | Jako autor przed przyjęciem lub aktualny wykonawca w `accepted`/`in_progress` | Każde aktywne zgłoszenie |
| Ręczny priorytet i konta | Brak | Brak | Dozwolone |
| Korekta kategorii | Brak | Aktualnie przypisany wykonawca | Niezależnie od przypisania |
| Dostęp do przyszłego asystenta | Brak | Dozwolony | Dozwolony |

Zmiana przypisania w `accepted` i `in_progress` zachowuje status, autora
i bieżące zadanie. Przypisanie nowego zgłoszenia od razu nadaje `accepted`.
Autorzy decyzji statusu oraz rozwiązania i odrzucenia mają osobne pola;
wszystkie decyzje zapisują się w transakcji z blokadą zgłoszenia. Po przyjęciu
opis i checkbox są zablokowane dla każdej roli. Notatki pozostają osobno.
Dezaktywacja/zmiana roli wykonawcy nie przenosi jego aktywnych zgłoszeń;
administrator może je potem przypisać innej osobie.

Wspólna reguła `available_tickets()` w `backend/app/services/access.py` filtruje listę,
odczyty i sugestie duplikatów, również przez alias DELETE. Przyszłe wyszukiwanie
i RAG powinny korzystać z tej samej reguły. Dependency `get_assistant_user`
sprawdza dostęp obsługi i administratora; rzeczywisty endpoint LLM nadal
pozostaje do implementacji. Priorytet ręczny ma autora i czas ostatniej decyzji.
Korekta kategorii jest dostępna; jej integracja z zatwierdzaniem rozwiązanego
zgłoszenia do referencji pozostaje w E5.12–E5.13.

Korekta zapisuje osobno `manual_category`, `manual_category_version`,
`manual_category_by_id` i `manual_category_at`. Pole `category` jest kategorią
operacyjną, a `predicted_category` i `predicted_category_version` wskazują
ostatnie zapisane przewidywanie modelu i jego wersję treści. Wynik zadania
`result.category` zawsze zawiera wynik modelu, również gdy kategorią operacyjną
jest korekta ręczna. Korekta nie zmienia priorytetu, statusu, zadań, embeddingu
ani referencji KNN. Dla tej samej wersji tekstu zadanie zachowuje korektę.

Żądanie korekty zawiera kategorię i wersję opisu widzianą przez użytkownika,
np. `{"category":"performance","expected_content_version":1}`. Wersja jest
wymaganą dodatnią liczbą całkowitą. Serwer porównuje ją z aktualną wersją po
zablokowaniu zgłoszenia. Niezgodność zwraca 409 bez zapisania korekty; klient
musi odczytać nowy opis i ponownie ocenić kategorię. Chroni to również przed
spóźnioną korektą, która czekała na równoległy zapis zmienionej treści.

Inny opis zwiększa wersję treści, ustawia kategorię operacyjną na `unknown`
i unieważnia dotychczasową korektę (`manual_category_current=false`). Metadane
ostatniej korekty i ostatniego przewidywania pozostają ze starszą wersją;
nowa klasyfikacja może zapisać nową kategorię. Taki sam opis i zmiana samego
checkboxa zachowują korektę. Dawne wyniki modelu są też dostępne w zadaniach
danej wersji. Docelowy polski słownik helpdesku i sprawdzenie zatwierdzonych
referencji nadal należą do późniejszych prac; dawnych kategorii nie mapujemy
automatycznie na nowe.

## Uruchomienie przez Docker Compose

Wymagany działający Docker Desktop z kontenerami Linux. Polecenia wykonuj
z katalogu repozytorium. Nie nadpisuj istniejącego `backend/.env.docker`:

```powershell
if (-not (Test-Path backend/.env.docker)) { Copy-Item backend/.env.docker.example backend/.env.docker }
```

W nowym pliku ustaw własne hasło spójnie w `POSTGRES_PASSWORD` i
`DATABASE_URL`. Zmienne `POSTGRES_*` inicjalizują tylko pusty wolumen;
przy istniejącej bazie użyj jej dotychczasowych danych dostępu.
`backend/Dockerfile` instaluje PyTorch dla CPU. Celery, Redis i Flower zostały usunięte.
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
Seed uzupełnia osobną tabelę referencji KNN z 10 dawnymi angielskimi przykładami
z `backend/data/sample_tickets.json`. Opcjonalne `--author-email konto@mail.com` dodaje
także zgłoszenia demonstracyjne do pustej tabeli, z jawnym zaakceptowanym autorem.
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
zachowane. Rekordy bez dat zatrzymują migrację zamiast otrzymywać
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
Po migracji uruchom ponownie `backend/scripts/seed_db.py`: uzupełni demonstracyjną
referencję bez zmiany dotychczasowych zgłoszeń. Każdy przykład zachowuje
tekst, kategorię, priorytet bazowy, embedding oraz źródło i klucz w zbiorze.
Bez referencji klasyfikacja kończy się poprawnie wynikiem `unknown` i
tymczasowym priorytetem `medium`, z zachowaniem checkboxa i decyzji ręcznej.

Migracja `e3a000000001` dodaje konta i przypisania. Dawne rekordy zachowują
`author_id=null` i jawne `legacy_unowned=true`; dostęp do nich mają obsługa
i administrator. Nie dopisujemy autorów ani historycznych wykonawców i decyzji.
Nowe zgłoszenie musi mieć autora. Jeśli znasz autorów dawnych zgłoszeń,
przygotuj sprawdzone mapowanie JSON, np. `{"1":"autor@mail.com"}`, i uruchom:

```powershell
.venv/Scripts/python.exe backend/scripts/import_ticket_authors.py backend/authors.json
# Lub w Compose:
docker compose run --rm api python scripts/import_ticket_authors.py authors.json
```

Plik `authors.json` w wariancie Compose umieść w `backend/`, montowanym do `/app`.
Import wymaga istniejących, zaakceptowanych kont i wyłącznie dawnych rekordów
bez autora; sprawdza całe mapowanie przed zapisem w jednej transakcji.
Nie nadpisuje znanego autora. Bez wiarygodnego mapowania pozostaw dawne dane
jako `legacy_unowned`. Cofnięcie migracji kont z danymi jest blokowane.

Migracja `e2b000000001` dodaje metadane przewidywania i korekty kategorii.
Zachowuje istniejące pola bez zmian; nowe pola są puste, ponieważ dawna kategoria
operacyjna nie dowodzi pochodzenia z KNN. Nie tworzy fikcyjnych korekt ani
przewidywań. Wymaga standardowego `alembic upgrade head` przed startem API.
Downgrade odmawia usunięcia zapisanych przewidywań lub korekt.

## Uruchomienie lokalne i testy

Wymagany Python 3.12 lub 3.13. Utwórz środowisko i zainstaluj zależności:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
```

Ustaw w `backend/.env` dostęp do bazy na `localhost:5433`, zgodny z konfiguracją
kontenera PostgreSQL. Migracje i seed:

```powershell
.venv/Scripts/python.exe -m alembic -c backend/app/alembic.ini upgrade head
.venv/Scripts/python.exe backend/scripts/seed_db.py
.venv/Scripts/python.exe -m uvicorn app.api.main:app --app-dir backend
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
Push-Location backend
../.venv/Scripts/python.exe -c "from app.services.text_validation import get_tokenizer; get_tokenizer()"
$env:HF_HUB_OFFLINE='1'
../.venv/Scripts/python.exe -m unittest discover -s tests -v
Pop-Location
docker compose -p issuetracker-tests -f docker-compose.test.yml down
Remove-Item Env:HF_HUB_OFFLINE
Remove-Item Env:TEST_DATABASE_URL
```

Testy odmawiają uruchomienia bez `TEST_DATABASE_URL` lub przy nazwie bazy
innej niż `issuetracker_test`. Czyszczą wyłącznie jawnie wskazaną bazę
testową. Sprawdzają API na prawdziwym PostgreSQL/pgvector oraz tokenizer
modelu. Etap 3 rozszerza je o rejestrację, domeny, hasła, JWT, bieżące role
i aktywność kont, atomową akceptację, widoczność danych i zadań, macierz
obsługi zgłoszeń, historię przypisań, wyścigi decyzji i jawny import autorów.
Komenda administratora ma testy ukrytego wejścia hasła i odmowy bez takiego
terminala. Po domknięciu zaległości etapów 1–2 pełna regresja przeszła
85/85 testów na osobnym PostgreSQL/pgvector. Obejmuje wszystkie role przy
próbach zmiany statusów końcowych przez PATCH i DELETE, oba porządki wyścigu
edycji zgłaszającego z przyjęciem przez obsługę oraz pełne ponowienie
klasyfikacji z zachowaniem statusu i decyzji administratora. Korekta kategorii
ma testy uprawnień, walidacji, zapisu podczas klasyfikacji, wyniku `unknown`,
ponowienia błędu i unieważnienia po zmianie treści. Migracja zachowuje stare
dane i odmawia cofnięcia powodującego utratę metadanych kategorii.
Testy obejmują także pełny potok zadania z kontrolowanym wynikiem
modelu, rzeczywiste zapytania pgvector, błędy obliczeń i zapisu, ponowienia,
wyścigi edycji/statusu, wersjonowanie i brak blokowania pętli API. Test procesu
uruchamia prawdziwy Uvicorn z powolnym testowym encoderem, odbiera HTTP przed
ukończeniem obliczeń, zabija proces, uruchamia go ponownie i ponawia zadanie.
Oddzielnie sprawdzono dwa kolejne zadania z rzeczywistym MiniLM i embeddingami
384. To weryfikacja integracji, bez oceny jakości klasyfikatora.

Osobne testy regresji nie wymagają PostgreSQL ani pobierania modelu:

```powershell
Push-Location backend
../.venv/Scripts/python.exe -m unittest tests.test_migration_isolation tests.test_request_validation tests.test_processing_diagnostics -v
Pop-Location
```

Sprawdzają cel migracji niezależnie od kolejności importów, brak blokowania
API podczas tokenizacji oraz diagnostykę błędów bez ujawniania danych.
Migracje testowe otrzymują jawny adres bazy i przed zmianą schematu
potwierdzają przez PostgreSQL, że połączono się z `issuetracker_test`.

## Kontrakt zgłoszeń po etapach 1–3

Wszystkie poniższe operacje wymagają Bearer JWT i podlegają powyższej macierzy.

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
  zapisują się razem ze statusem i autorem decyzji.
- `DELETE /tickets/{id}` pozostaje oznaczonym jako przestarzały aliasem
  zakończenia sprawy. Wymaga jawnego ciała z końcowym `status` i notatką,
  gdy jest wymagana; korzysta z tej samej macierzy i sesji bazy co PATCH.
  Nie usuwa rekordu. Wywołanie bez ciała daje 422. Zachowuje odpowiedź
  `ticket`, `status`, `suggested_duplicates`; bez aktualnego embeddingu sugestie są puste.
- `GET /tickets/{id}/task/{task_id}` zachowuje adres, a stan odczytuje z PostgreSQL.
  Odpowiedź: `task_id`, `state` (`pending`, `running`, `succeeded`, `failed`),
  `content_version`, `current`, `created_at`, `started_at`, `finished_at`,
  `result`, `error`, `error_code`. Brak zadania lub inne zgłoszenie daje 404.
  `result` zawiera przewidywaną kategorię i priorytety bazowy/automatyczny, bez wektora;
  kategorię operacyjną po korekcie odczytuj ze szczegółów zgłoszenia;
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
decyzji jest chronione przed zadaniem; endpoint administratora zapisuje autora
i czas. Korekta kategorii ma osobną wersję treści, autora i czas. Zatwierdzanie
etykiet rozwiązanego zgłoszenia do referencji nadal należy do etapu 5.

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
zgłoszenia. Reguły ról i przypisań są egzekwowane także
przez przestarzały alias DELETE. Zmiana statusu nie uruchamia klasyfikacji.
Duplikaty uwzględniają trzy aktywne statusy. Stara eskalacja procentowa
została usunięta. Eskalację podobnych aktywnych zgłoszeń w oknie czasowym
dołączymy w etapie 5, aby liczyć różne osoby zamiast liczby rekordów.
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

- `backend/app/api/main.py` składa aplikację, zarządza jej cyklem życia i tłumaczy błędy na HTTP.
- `backend/app/api/schemas.py` definiuje kontrakt żądań i odpowiedzi, a `backend/app/api/tickets.py` endpointy.
- `backend/app/services/tickets.py` zawiera operacje na zgłoszeniach i granice transakcji; nie zależy od FastAPI ani modeli żądań.
- `backend/app/services/tasks.py` współdzieli zapis zadań i blokady z wykonawcą `ProcessingRuntime`.
- `backend/app/domain.py` definiuje priorytety, źródła, stany zadań i typowany wynik klasyfikacji.
- `determine_priority()` w `backend/app/services/priorities.py` jest czystą funkcją. Osobna funkcja zapisuje jej decyzję na zgłoszeniu.

`ProcessingRuntime` otrzymuje asynchroniczną funkcję klasyfikującą w konstruktorze.
Pozwala to testować wykonawcę z kontrolowanym klasyfikatorem bez podmieniania
importów modułu. Testy reguł priorytetu nie wymagają bazy ani modelu:

```powershell
Push-Location backend
../.venv/Scripts/python.exe -m unittest tests.test_priorities -v
Pop-Location
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
