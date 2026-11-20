# Pierwsza walidacja odpowiedzi RAG — 2026-11-16

[Zestaw walidacyjny](validation-en-v1.json) zawiera osiem pytań EN i 15 syntetycznych zgłoszeń. Oba warianty uruchomiono przez tę samą funkcję obsługi czatu z rzeczywistym PostgreSQL/pgvector, MiniLM i Qwen3 4B Instruct w Ollamie. Zmieniono metodę wyszukiwania. Model, prompt `rag-en-v2`, limit pięciu źródeł i ustawienia generowania pozostały wspólne. Dopytanie V02 w każdym wariancie dostało historię z jego odpowiedzi na V01. [Surowe odpowiedzi, kontekst, czasy i metadane](validation-en-v1-results.json).

## Wyniki

| Wariant | Recall@5 | MRR@5 | Pytania z odpowiedzią | Pytania bez odpowiedzi | Wszystkie zaliczone |
|---|---:|---:|---:|---:|---:|
| Semantyczny | 1,00 | 1,00 | 6/6 | 2/2 | 8/8 |
| Pełnotekstowy | 0,80 | 0,80 | 5/6 | 1/2 | 6/8 |

Metryki rankingu obejmują pięć samodzielnych pytań z oczekiwanymi źródłami. Wynik odpowiedzi obejmuje wszystkie osiem pytań. Codex porównał zapis odpowiedzi z ticketami według [rubryki](validation-rubric.md). Poniżej „zal.” oznacza maksymalną ocenę w każdym kryterium mającym zastosowanie. Ocena jest wstępna i wymaga przeglądu autora przed wykorzystaniem w pracy.

| Pytanie | Semantyczne | Pełnotekstowe | Obserwacja |
|---|---|---|---|
| V01 | zal. | zal. | Obie naprawy monitorów i dwa prawidłowe cytaty, #101 i #102. |
| V02 | zal. | zal. | Oba warianty wróciły do źródeł z historii i wskazały zmianę z #102. |
| V03 | zal. | 0 poprawność i kompletność | Pełny tekst zwrócił tylko #101. Model zgłosił brak danych, a rozwiązanie było w #104. |
| V04 | zal. | zal. | Oba warianty podały właściwą zmianę uprawnień z #106. |
| V05 | zal. | zal. | W obu kontekstach znalazły się aktywne zgłoszenie #108 i podobna sprawa #109. Czat poprawnie zgłosił brak potwierdzonej naprawy. |
| V06 | zal. | 0 za zachowanie przy braku danych | Semantyka zwróciła pusty kontekst. Po wyszukiwaniu pełnotekstowym model przytoczył ustawienie z #102, które dotyczyło monitorów, w odpowiedzi na pytanie o dźwięk po aktualizacji BIOS-u. |
| V07 | zal. | zal. | Oba warianty podały zmianę portu i restart usługi drukowania z #110. |
| V08 | zal. | zal. | Oba warianty wskazały zmianę identyfikatora logowania z #112. |

V03 pokazuje problem doboru źródeł. Odpowiedź o braku danych pasowała do kontekstu przekazanego modelowi, lecz prawidłowy ticket istniał w korpusie. W V06 obecny w kontekście cytat potwierdza przytoczoną czynność. Treść cytowanego zgłoszenia dotyczy jednak innej usterki, więc sama kontrola identyfikatora nie wystarczyła.

To jeden przebieg na małej partii walidacyjnej. Czasy w JSON-ie opisują ten przebieg. Pierwsza odpowiedź obejmowała rozruch Qwena, a pomiar rozgrzanego i zimnego potoku wymaga powtórzeń. [Wyniki osobnej części testowej](test-en-v1-report.md) przedstawiono w oddzielnym raporcie.

## Odtworzenie

W katalogu głównym repozytorium, przy działających Dockerze i lokalnej Ollamie z modelem `qwen3:4b-instruct` oraz zainstalowanych zależnościach backendu:

```powershell
docker compose -p issuetracker-rag-validation -f docker-compose.test.yml up -d --wait
$env:DATABASE_URL = 'postgresql+asyncpg://issuetracker_test:test-only@127.0.0.1:5434/issuetracker_test'
$env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
$env:OLLAMA_MODEL = 'qwen3:4b-instruct'
.venv/Scripts/python.exe -m alembic -c backend/app/alembic.ini upgrade head
.venv/Scripts/python.exe backend/scripts/evaluate_rag_validation.py --output validation-repeat.json
docker compose -p issuetracker-rag-validation -f docker-compose.test.yml down
```

Skrypt wymaga zmigrowanej bazy testowej bez zgłoszeń i użytkowników. Dane do pomiaru zapisuje w wycofywanej transakcji. Uruchamia funkcję obsługi czatu z kontem testowym Staff bez przejścia przez warstwę HTTP i logowanie. Wynik dotyczy jakości wyszukiwania, odpowiedzi i dopytania w tym scenariuszu. Testy logowania, uprawnień i interfejsu są osobną częścią weryfikacji.
