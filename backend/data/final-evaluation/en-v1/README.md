# Niezależny test klasyfikacji EN — przygotowanie v1

Stan na 2026-11-07: **100/100 zatwierdzonych przypadków — 70 pełniejszych
i 30 słabych**. Zamrożono referencje, konfigurację i test, a następnie wykonano
końcowy pomiar klasyfikacji. E4.4 i E10.3 są ukończone w tym zakresie.
[Raport wyników](results/report.md), [notatka do pracy i analiza ograniczeń](results/interpretation.md),
[cały zatwierdzony zbiór](review.md), [słabe opisy osobno](review-weak.md).

Na 70 pełniejszych opisach raw accuracy wynosi 88,6% kategorii i 75,7% priorytetu.
Łącznie na ustalalnych etykietach: 78/88 = 88,6% kategorii i 61/82 = 74,4%
priorytetu. Po progach, z odmowami jako FN, odpowiednio 85,2% i 73,2%.
Wśród nieustalalnych etykiet skierowano do weryfikacji tylko 2/12 kategorii
i 1/18 priorytetów — istotne ograniczenie działania. Po teście nie zmieniano
progów ani modeli. Wynik nie jest skutecznością na rzeczywistych ticketach.

## Zatwierdzenie całości i zamrożenie testu

Użytkownik zatwierdził pozostałe 92 przypadki wiadomością
**„Dobra, akceptuj te przypadki i lecimy”**. [Zdarzenie zatwierdzenia](reviews/final-approval-100.json)
zapisuje ID, treść instrukcji, autora, czas i hashe snapshotów przed/po.
Pierwsze 8 decyzji zachowano bez zmian. Zatwierdzono również jawne null
dla etykiet, których nie można ustalić ze słabego opisu.

[sealed/test.en.json](sealed/test.en.json) jest wejściem końcowego pomiaru,
a [sealed/manifest.json](sealed/manifest.json) wiąże go z protokołem,
kodem oceny, walidatorem, zdarzeniem zatwierdzenia i snapshotem referencji.
Test SHA-256: `7a21d23718c49444107d3c05c8b0f5497c724b999697c7b492189eb704e1c846`.
Status zapisany wewnątrz tego pliku opisuje chwilę zatwierdzenia przed seal;
nie zmieniamy metadanych zamrożonego wejścia po pomiarze.

## Aktualny projekt: 100 przypadków w proporcji 70/30

Po prośbie o rozszerzenie do 100 użytkownik ustalił proporcję 70 pełniejszych
i 30 słabych opisów. Zachowano wszystkie dotychczasowe 60 rekordów wraz z ich
ID, treścią i przeglądami; dodano 30 pełniejszych i 10 słabych jako
FINAL-EN-081–120, początkowo wszystkie pending, później zatwierdzone osobno. Wśród pełniejszych propozycji jest 18
accounts_access, 18 hardware, 17 network i 17 software (70 nie dzieli się równo
przez cztery). Brakujące etykiety słabej części nadal są null.

[Zdarzenie rozszerzenia](reviews/design-change-100-70-30.json) zawiera obie
instrukcje użytkownika, listy ID oraz hashe [wersji sprzed rozszerzenia](reviews/candidates-before-100.json)
i [nowej wersji propozycji](reviews/candidates-after-100.proposed.json).
[Nowa partia źródłowa](batches/expansion-100.proposed.json) ma 40 rekordów.
Modele, progi i 120 referencji pozostają z tego samego snapshotu. Nie wykonano
przewidywań przed rozszerzeniem; rozszerzenie nie służyło poprawianiu wyniku.

## Historia: wcześniejszy projekt 40 pełniejszych + 20 słabych

Użytkownik poprosił o umieszczenie 20 słabo opisanych przypadków **w obrębie 60**.
Przed jakimikolwiek przewidywaniami wycofano 20 niezatwierdzonych pełnych
propozycji i zastąpiono je nowymi ID FINAL-EN-061–080. Pozostało 10 pełniejszych
opisów w każdej kategorii. Zatwierdzonych FINAL-EN-001–008 nie zmieniono.
Lista wycofanych ID, powód wyboru i sumy przed/po są w
[zdarzeniu zmiany projektu](reviews/design-change-weak20.json), a poprzednią
wersję 60 propozycji zachowano jako [snapshot historyczny](reviews/candidates-before-weak20.json).
Wycofane opisy nie wchodzą do aktualnego testu. Stary rozkład 15 pełnych na
kategorię zastąpiono wtedy układem 40/20. Obecne 70/30 to późniejsze rozszerzenie
opisane powyżej; wycofane wcześniej 20 ID nie zostało przywrócone.

## Słabe opisy w aktualnym zbiorze

Słaby opis może być krótki, potoczny lub niepełny. Nie każda krótka treść
jest niemożliwa do oznaczenia. W aktualnych propozycjach słabej partii są:

| Ustalalność etykiet z treści | Liczba |
|---|---:|
| Kategoria ustalalna, priorytet nieustalalny | 12 |
| Obie etykiety ustalalne mimo krótkiego opisu | 6 |
| Obie etykiety nieustalalne | 6 |
| Kategoria nieustalalna, priorytet ustalalny z wpływu na pracę | 6 |

Oznacza to zatwierdzone etykiety kategorii dla 18/30 i priorytetu dla 12/30.
Brak danych zapisano jako `null`; nie dopowiadamy przyczyny, wpływu ani obejścia.
`null` nie oznacza klasy `unknown`, niskiego priorytetu ani zastępczego `medium`.
Autor zatwierdza również decyzję, że etykiety nie można ustalić z treści:
`review.status=approved` i jawne `review.category=null` lub `review.base_priority=null`,
z uzasadnieniem w `review.notes`. Brak klucza nie jest zatwierdzonym brakiem danych.
Wszystkie 30 słabych opisów ma `description_quality=weak`; ich przegląd zatwierdzono przed oceną.

## Zatwierdzenie pierwszej próbki i rozszerzenie

Użytkownik zatwierdził istniejące FINAL-EN-001–008 wiadomością **„Akceptuj to”**.
Decyzję zapisano z autorem i czasem `2026-11-07T18:23:34+00:00`, bez zmian
treści lub proponowanych etykiet. [Zdarzenie zatwierdzenia](reviews/initial-sample-approval.json)
wskazuje zakres 8 ID i hashe [wersji sprzed przeglądu](reviews/initial-sample.proposed.json)
oraz [wersji zatwierdzonej](reviews/initial-sample.approved.json).

Następnie przygotowano [pierwotne 52 nowe propozycje](batches/remaining-52.proposed.json),
po 13 w każdej kategorii. Zatwierdzenie wcześniejszej próbki ich **nie obejmuje**.
Pierwotny rozkład 3 low, 5 medium, 5 high i 2 critical na kategorię jest
historyczny. Po pierwszej zmianie 40 pełniejszych przypadków miało po 2 low,
3 medium, 3 high i 2 critical na kategorię; następnie dodano 30 pełniejszych.
To celowe pokrycie klas, nie naturalny napływ
zgłoszeń. Poprawki autora należy zapisać; nie zmieniać etykiet dla zachowania proporcji.

## Co zapisano

- [frozen/manifest.json](frozen/manifest.json): rewizja Git, stan drzewa przy
  zapisie, liczebności referencji i sumy SHA-256 plików.
- [frozen/references.json](frozen/references.json): dokładnie 120 aktywnych
  referencji `pilot_en_120_v1` z bazy, z etykietami, identyfikatorami i zapisanymi
  wektorami. W chwili zapisu nie było żadnych referencji `approved_ticket`.
- [frozen/runtime.json](frozen/runtime.json): konfiguracja działającego kontenera,
  parametry TF-IDF i regresji, wersje najważniejszych bibliotek, rewizja modelu,
  sumy plików modelu w cache i rewizja migracji bazy `e5c000000001`.
- `frozen/code/`: kopie źródeł backendu, pliku polityk, wymagań, Dockerfile
  i skryptu przygotowania w chwili zapisu. Zachowano je także dlatego, że samo
  wskazanie rewizji Git nie opisuje niezatwierdzonych zmian.
- [frozen/known-pilot.en.json](frozen/known-pilot.en.json): wszystkie 170 znanych
  wcześniej opisów, w tym 50 słabych. Żaden z nich nie może stać się nowym testem.
- [candidates.json](candidates.json): 100 nowych przypadków i osobne decyzje
  przeglądu (100 approved). `reference_eligible=false` dla każdego rekordu.
- [review.md](review.md): czytelna wersja całości z uzasadnieniami i stanem
  przeglądu; [review-new.md](review-new.md) zawiera tylko oczekujące propozycje.
- [review-weak.md](review-weak.md): wydzielone 30 słabych opisów, z wyjaśnieniem
  brakujących informacji; [pierwsza partia](batches/weak-20.proposed.json)
  oraz 10 nowych w [rozszerzeniu](batches/expansion-100.proposed.json).
- [token-checks.json](token-checks.json): kontrola długości wszystkich 100 opisów
  przypiętym tokenizerem, bez przewidywań klasyfikatora.
- `sealed/`: zatwierdzony test, protokół oraz kopie skryptów oceny i walidacji.
- `results/`: JSON/Markdown, wektory 100 zapytań, wyuczony na 120 referencjach
  model priorytetu oraz manifest hashy. Notatkę interpretacyjną zapisano osobno.
- [checks/pgvector-parity.json](checks/pgvector-parity.json): zgodność sąsiadów
  i decyzji kategorii z operatorem pgvector dla 100/100 przypadków, bez odczytu
  tabel ticketów lub referencji, wyłącznie na przekazanych wektorach snapshotu.

Manifest SHA-256 przy zapisie:
`66b9ff93a214514d613d02b51f47bb067122e8df277ffb335924f4fa709ce0b2`.
Nie nadpisujemy tego snapshotu. `.gitattributes` zachowuje jego dokładne bajty
przy pobraniu repozytorium na Windows, aby konwersja LF/CRLF nie psuła sum.

To zamrożenie **eksperymentu**, nie blokada rozwoju aplikacji. Późniejsze
zatwierdzenia ticketów i zmiany bazy nie mogą wejść do tego pomiaru.
Eksport wykonano w transakcji tylko do odczytu; nie dodano ticketów i nie
zmieniono referencji ani konfiguracji usług.

## Ustalona konfiguracja

Kategoria: `all-MiniLM-L6-v2`, rewizja
`c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, KNN `k=3`, minimalny kosinus
`0.22`, minimalny udział głosów `2/3`. Ranking referencji: odległość, następnie
ID referencji; remis głosowania rozstrzyga najbliższa kategoria.

Priorytet bazowy: TF-IDF słów i dwugramów, `sublinear_tf=True`, regresja
logistyczna `C=100`, `max_iter=2000`, `random_state=20261107`. Próg wyniku `0.38`;
brak znanych terminów również oznacza weryfikację. Słownik, IDF i regresja będą
uczone wyłącznie na zamrożonych referencjach; nie na nowych opisach testowych.
Wynik `predict_proba` nie jest skalibrowaną gwarancją poprawności.

Duplikaty: próg `>0.75`, filtr tej samej kategorii. Eskalacja: 3 różnych autorów
w 24 h, podobieństwo `>0.85`. Parametry zapisano dla pełnego kontekstu;
próbka klasyfikacji nie jest zbiorem par duplikatów ani pomiarem jakości
grupowania awarii. Checkbox i reguły priorytetu mają odrębne testy.

**Różnica środowisk:** wcześniejsze raporty pilotażowe powstały w lokalnym
środowisku, natomiast snapshot pochodzi z działającego Dockera. Na przykład
scikit-learn w pilotażu miał wersję `1.8.0`, a w kontenerze `1.9.1`;
sentence-transformers odpowiednio `5.3.0` i `6.2.0`. Wersje zapisano jawnie.
Planowany test ma oceniać zamrożony wariant działającej aplikacji. Różnicy
wyników względem pilotażu nie wolno przypisać wyłącznie zmianie zbioru.
Przed pomiarem trzeba sprawdzić zgodność środowiska z `runtime.json`;
nie aktualizować bibliotek ani parametrów na podstawie wyników testowych.

## Protokół nowych przypadków

1. Docelowo 100 nowych angielskich opisów: 70 pełniejszych i 30 słabych.
   Dla nieustalalnych kategorii nie wymagamy fikcyjnej równowagi
   klas. To celowe pokrycie przypadków, nie naturalny rozkład zgłoszeń organizacji.
   Pierwsze 8 zatwierdzono osobno, następnie pozostałe 62 pełniejsze i 30 słabych.
2. Każdy opis ma własny incydent; brak kopii i bliskich parafraz znanego
   pilotażu oraz zamrożonych referencji. Walidator wykrywa identyczne teksty
   po normalizacji i kolizje grup, ale **nie udowadnia braku parafraz**.
   Odrębność incydentu trzeba sprawdzić podczas przeglądu treści.
3. Autor sprawdza treść, wpływ, obejście, kategorię i priorytet bazowy,
   zanim zobaczy wynik klasyfikatora. Propozycje generatora zostają zachowane;
   decyzje trafiają do `review` z autorem, datą ze strefą i uzasadnieniem korekt.
   Wykluczenie wymaga powodu. Nie wykluczamy słabych przypadków wyłącznie dlatego,
   że ich etykieta jest nieustalalna: do tego służy jawnie zatwierdzone `null`.
   Pozostałe wykluczone przypadki zastąpić przed testem, zachowując historię;
   nie wybierać przypadków według przewidywań.
4. Przed oceną utrwalić kompletny zatwierdzony JSON i jego SHA-256. Obecny
   `candidates.json` jest roboczy; nie jest jeszcze zamrożonym zbiorem testowym.
5. Dopiero potem przygotować/uruchomić ocenę zgodną z zamrożonym kodem i
   środowiskiem. Klasyfikować nowe opisy względem snapshotu referencji,
   bez odczytu zmieniającej się bazy aplikacji. Nie dodawać ich do treningu.
6. Wyniki pokazać osobno dla 70 pełniejszych i 30 słabych opisów. Dla każdej
   etykiety accuracy i macro-F1 liczyć tylko tam, gdzie jest ustalalna, z jawnym
   mianownikiem i liczbą nieustalalnych przypadków. Według zatwierdzonych etykiet
   oznacza to 70+18=88 ocenialnych kategorii i 70+12=82 priorytety, a nie accuracy
   na wszystkich 100. Te mianowniki utrwalono w raporcie.
7. Dla ustalalnych etykiet raportować surowe przewidywania, decyzje po progach,
   accuracy, macro-F1, wyniki per klasa, macierze pomyłek, zaniżenia pilnych spraw,
   pokrycie i poprawność zaakceptowanych wyników. Odmowę liczyć jako brak trafienia
   w całościowej metryce tego ocenialnego podzbioru; nie ukrywać trudnych przykładów.
8. Dla nieustalalnych etykiet osobno mierzyć liczbę i odsetek skierowań do
   weryfikacji oraz bezpodstawnie przyjętych automatycznych decyzji. Oceniać
   kategorię i priorytet niezależnie: brak priorytetu nie wyklucza oceny kategorii
   i odwrotnie. Nie liczyć `null` jako poprawnej lub błędnej klasyfikacji ani
   podstawiać `medium` do etykiety wzorcowej. Sam fallback w aplikacji nie jest
   trafnym przewidywaniem priorytetu. Nie stroić na obejrzanych wynikach.

## Pochodzenie i ograniczenia do opisania w pracy

Treść i propozycje etykiet przygotowuje asystent Codex w tej rozmowie,
bez danych rzeczywistej organizacji. Dokładny identyfikator generatora i jego
parametry próbkowania nie są udostępnione; braków nie uzupełniamy domysłami.

Zastosowana instrukcja: przygotować nowe krótkie angielskie zgłoszenia helpdesku
IT w czterech ustalonych kategoriach; opisać objaw, wpływ na pracę i obejście
wystarczające do zaproponowania priorytetu; używać nowych incydentów,
nie przerabiać znanych zdań, podać uzasadnienia i oznaczyć wszystko `pending`.
Na początku powstało po dwa przykłady na kategorię, obejmujące cztery priorytety.
Po zatwierdzeniu tej próbki przygotowano pozostałe 52, bez sprawdzania ich
przewidywań. Oryginalne propozycje drugiej partii zapisano osobno w `batches/`.
Następnie, na wniosek użytkownika i nadal przed pomiarem, dodano 20 nowych
krótkich i niepełnych opisów **w miejsce** 20 niezatwierdzonych pełnych.
Instrukcja tej partii: zachować różną ustalalność kategorii i priorytetu,
nie dopowiadać brakujących informacji, podać uzasadnienie każdego `null`,
nie kopiować znanych 50 słabych opisów pilotażu i wszystko oznaczyć pending.
Kolejne rozszerzenie na wniosek użytkownika dodało 30 pełniejszych i 10 słabych
opisów według tych samych reguł, bez zmiany wcześniejszych przypadków i bez
sprawdzania przewidywań. Nowo dopisane rekordy były pending do późniejszej,
jawnej akceptacji całego zbioru przez użytkownika; dopiero potem uruchomiono test.

Asystent przygotowujący dane zna pilotaż. Oddzielenie incydentów od treningu
nie usuwa podobieństwa stylu generatora ani ryzyka łatwych wskazówek językowych.
Przegląd jednego autora nie jest oceną przez dwóch niezależnych anotatorów.
100 przypadków, w szczególności małe podzbiory priorytetów, to nadal niewielka próba.
Wynik opisujemy jako test na nowych zatwierdzonych **danych syntetycznych**,
nie jako skuteczność na rzeczywistych ticketach użytkowników.

## Polecenia (katalog główny repozytorium)

```powershell
# Kontrola integralności; bez bazy, uczenia i przewidywań.
.venv/Scripts/python.exe backend/scripts/prepare_final_evaluation.py verify

# Sprawdzenie formatu i identycznych tekstów, dopuszcza pending.
.venv/Scripts/python.exe backend/scripts/prepare_final_evaluation.py validate

# Czytelne pliki całości, oczekujących i 30 słabych z aktualnymi decyzjami przeglądu.
.venv/Scripts/python.exe backend/scripts/prepare_final_evaluation.py review

# Bramka gotowości: obecnie przechodzi dla 100 approved.
.venv/Scripts/python.exe backend/scripts/prepare_final_evaluation.py validate --require-approved

# Wykonane jednorazowo przed pomiarem; istniejącego sealed nie nadpisuje.
# .venv/Scripts/python.exe backend/scripts/evaluate_final_classification.py seal

# Wykonane w zamrożonym środowisku Dockera; istniejących wyników nie nadpisuje.
# docker compose exec -T api python scripts/evaluate_final_classification.py evaluate

# Dodatkowa kontrola pgvector tylko do odczytu; zapisany wynik nie jest nadpisywany.
# docker compose exec -T api python scripts/check_final_pgvector.py

# Nowy eksport tylko do osobnego, jawnie wybranego eksperymentu:
# ... prepare_final_evaluation.py freeze --directory <nowy-katalog>
```

Polecenia `verify`, `validate` i `review` nie uruchamiają klasyfikatora. Ocena
została wykonana osobnym skryptem. Przeszło 18 testów w
`tests.test_final_evaluation_preparation` i `tests.test_final_classification_evaluation`;
wszystkie 100 opisów
mieści się w limicie 256 tokenów przypiętego tokenizera (maksymalnie 76).

Aby odtworzyć pomiar, skopiować `frozen/` i `sealed/` do osobnego katalogu
`data/final-evaluation/en-v1/replay-2/`, bez kopiowania `results/`, i uruchomić
zapisany skrypt z tego samego środowiska Dockera:

```powershell
docker compose exec -T api python data/final-evaluation/en-v1/sealed/evaluation-script.py evaluate --directory data/final-evaluation/en-v1/replay-2
```

Zgodność bibliotek,
modelu i skryptów jest sprawdzana; przy późniejszych zmianach źródeł potrzebny
jest osobny checkout z zapisanymi wersjami skryptów. Nie uruchamiać oceny
w lokalnym venv o innych wersjach bibliotek. Powtórzenie techniczne na tym
samym teście nie jest nowym niezależnym eksperymentem.
