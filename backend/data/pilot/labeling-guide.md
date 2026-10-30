# Instrukcja etykietowania pilotażu helpdesku IT

Wersja: `pilot-pl-v1`, 2026-10-28. Status: propozycja do weryfikacji przez autora pracy.

## Cel i pochodzenie

Pilotaż obejmuje 40 syntetycznych zgłoszeń po polsku, po 10 na kategorię.
Treści i proponowane etykiety przygotował asystent Codex. Nie są to zgłoszenia
rzeczywistej organizacji ani etykiety zatwierdzone przez człowieka. Dokładny
identyfikator modelu generującego i parametry próbkowania nie były dostępne;
metadane uczciwie zapisują tę informację zamiast podawać przypuszczenia.
Instrukcję generowania zapisano w `generation.md`.

Każdy rekord zachowuje propozycję generatora oraz oddzielny obiekt `review`.
Autor sprawdza **opis, kategorię, priorytet, grupę parafraz i uzasadnienia**.
Wypełnia `review.status=approved`, `review.category`, `review.base_priority`,
`review.reviewer` i `review.reviewed_at` (data ISO 8601 ze strefą czasową).
Zmiany względem propozycji opisuje w `review.notes`; propozycja pozostaje
niezmieniona. Rekord nienadający się do badania otrzymuje `excluded` z powodem,
autorem i datą. Niepewność pozostaje `pending` do rozstrzygnięcia.
Zwięzły podgląd całej próbki znajduje się w `review.md`, a źródłem jest `tickets.json`.

## Kategorie

| Kod roboczy | Kategoria | Co obejmuje |
|---|---|---|
| `accounts_access` | Konta i uprawnienia | Hasło, blokada konta, MFA, wygasłe uprawnienie, jawna odmowa dostępu. |
| `hardware` | Sprzęt | Zasilanie, ekran, klawiatura, port, mechanizm drukarki i inne fizyczne objawy. |
| `network` | Sieć i łączność | Brak połączenia, zrywanie transmisji, Wi-Fi, VPN i osiągalność usług. |
| `software` | Oprogramowanie | Błąd działania programu lub funkcji, awaria procesu, nieprawidłowy wynik. |

Klasyfikujemy objaw opisany przez zgłaszającego, bez zgadywania przyczyny.
Sama nazwa produktu nie rozstrzyga kategorii. Nie stosujemy reguły typu
„każdy VPN to sieć” lub „każda drukarka to sprzęt”.

| Przypadek graniczny | Rozstrzygnięcie |
|---|---|
| VPN odrzuca konto komunikatem o braku uprawnień. | Konta i uprawnienia. |
| VPN przyjmuje logowanie, potem połączenie kończy się timeoutem. | Sieć i łączność. |
| Aplikacja pokazuje „brak uprawnień” przy otwieraniu folderu. | Konta i uprawnienia. |
| Folder można otworzyć; program zamyka się podczas zapisu pliku. | Oprogramowanie. |
| Drukarka zacina papier także podczas własnego testu. | Sprzęt. |
| Test drukarki działa; jeden program zamyka się przy drukowaniu. | Oprogramowanie. |
| Nie działa tylko jeden serwis, bez żadnych dodatkowych objawów. | Brakuje danych; poprosić o doprecyzowanie lub wykluczyć. |

W zgłoszeniu zawierającym kilka niezależnych problemów prosimy o rozdzielenie.
Jeśli opis wskazuje jeden główny problem i jego skutki, kategorię wybieramy dla
problemu głównego. Nie rozstrzygamy niejednoznaczności arbitralną kolejnością kategorii.

## Priorytet bazowy

Priorytet wynika z **treści**, wpływu na pracę, liczby osób i dostępnego obejścia.

| Kod | Nazwa | Kryterium |
|---|---|---|
| `low` | Niski | Drobna uciążliwość; funkcje potrzebne do pracy są dostępne. |
| `medium` | Średni | Praca jest utrudniona, ale opisano działające obejście. |
| `high` | Wysoki | Ważne zadanie jest zablokowane i nie ma działającego obejścia. |
| `critical` | Krytyczny | Niedostępna kluczowa usługa blokuje pracę wielu osób. |

Słowa „pilne”, „awaria” i „nie działa” same nie stanowią dowodu wpływu.
Nie przypisujemy priorytetu na podstawie samej kategorii ani prestiżu zgłaszającego.
Przy braku informacji o wpływie/obejściu przykład pozostaje do doprecyzowania;
**nie wpisujemy automatycznie `medium` jako etykiety wzorcowej**. Tymczasowa
wartość zastępcza aplikacji jest odrębnym mechanizmem.

Pole `work_blocked` nie jest wejściem modelu i nie wyznacza etykiety bazowej.
Np. pojedynczy pracownik bez dostępu do podstawowego narzędzia otrzymuje
`high` jako priorytet bazowy, a zaznaczony checkbox może nadać `critical`
jako priorytet końcowy. Wiele zgłoszeń również nie zmienia wzorcowej etykiety
pojedynczej treści: regułę eskalacji testujemy oddzielnie.

## Protokół pilotażu

- Kody nowych kategorii dotyczą tylko pilotażu. Nie mapujemy automatycznie
  `bug`/`performance`/`feature` i nie zmieniamy bazy działającej aplikacji.
- Powiązane parafrazy i jeden incydent mają wspólne `group_id`. W próbce są
  cztery takie pary; pozostałe zgłoszenia opisują odrębne przypadki.
- Badanie wyklucza całą grupę ocenianego przykładu z jego sąsiadów (leave-one-group-out).
  Nie wyszukujemy zgłoszenia wśród niego samego ani jego bliskiej parafrazy.
- Używamy dotychczasowego `k=3`, głosowania większościowego i kosinusa;
  remisy rozstrzyga najbliższy sąsiad, kolejność jednakowych wyników identyfikator.
  Nie dobieramy progu pewności ani parametrów na tej próbce.
- Raportujemy accuracy, macro-F1, macierze pomyłek, rozkład etykiet,
  najbliższych sąsiadów, długość tekstu w tokenach i przypadki błędów.
  Dla priorytetu dodajemy punkt odniesienia, który zawsze wybiera `medium`,
  tak jak obecna wartość zastępcza aplikacji; nie korzysta on z treści.
- Wyniki z propozycji generatora są wyłącznie diagnostyką techniczną.
  Nie potwierdzają jakości na prawdziwych zgłoszeniach ani ręcznej poprawności etykiet.
  Mała liczba przykładów `critical` szczególnie ogranicza wnioski.
- Pilotaż nie jest zbiorem testowym końcowym. Jego przypadki i parafrazy nie
  powinny później trafić do niezależnego testu. Docelowy podział 300 przykładów
  i 30 pytań RAG zostanie ustalony oddzielnie przed zamrożeniem zbiorów.
- Obowiązkowy model pozostaje `all-MiniLM-L6-v2`. Jego karta oznacza język
  angielski; wyniki po polsku trzeba zmierzyć, a nie zakładać wielojęzyczność.
  Źródło: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Przypinamy w raporcie faktycznie użyty snapshot modelu, sumę SHA-256 danych,
  parametry oraz wersje bibliotek. Ten sam podział grup pozwala odtworzyć ocenę.

## Uruchomienie (z katalogu głównego repozytorium)

```powershell
# Walidacja formatu, liczebności i propozycji; bez bazy i bez ładowania modelu.
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --validate-only

# Diagnostyka na propozycjach etykiet; domyślnie tylko lokalny cache modelu.
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py

# Tylko gdy modelu nie ma lokalnie: pozwól pobrać go z Hugging Face.
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --allow-download

# Po ręcznym przeglądzie wszystkich rekordów (approved albo excluded).
.venv/Scripts/python.exe backend/scripts/evaluate_pilot.py --labels reviewed --output backend/data/pilot/results-reviewed
```

Raport JSON i jego polska wersja Markdown trafiają domyślnie do `results/`.
Nie są importowane żadne rekordy do PostgreSQL. Samodzielny przegląd przez
autora bez drugiego oceniającego pozostaje ograniczeniem przyszłego badania.
