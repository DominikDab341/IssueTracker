# Notatka do pracy — końcowy test klasyfikacji EN

Data: 2026-11-07. Źródło liczb: [raport pomiaru](report.md) i [pełny JSON](report.json).
To jednorazowy test zamrożonego wariantu, nie kolejne strojenie parametrów.

## Co oceniono

100 nowych syntetycznych opisów EN: 70 pełniejszych i 30 słabych. Autor pracy
zatwierdził treści oraz proponowane etykiety przed uruchomieniem przewidywań.
W słabej części zatwierdził również brak informacji do ustalenia kategorii
lub priorytetu. Osobny snapshot zawierał 120 referencji. Żadne z 100 zapytań
nie weszło do uczenia słownika TF-IDF, IDF ani regresji.

Kategoria: MiniLM + KNN k=3. Priorytet bazowy: TF-IDF + regresja logistyczna
C=100. Progi i referencje pozostały niezmienione po obejrzeniu wyniku.
Checkbox, decyzje administratora i eskalacja mają odrębne testy i nie były
zaliczane jako trafne przewidywania modelu.

## Najważniejsze wyniki

| Część | Kategoria przed progami | Priorytet przed progami |
|---|---:|---:|
| 70 pełniejszych opisów | 62/70 = 88,6% | 53/70 = 75,7% |
| 30 słabych — tylko ustalalne etykiety | 16/18 = 88,9% | 8/12 = 66,7% |
| Łącznie — tylko ustalalne etykiety | 78/88 = 88,6% | 61/82 = 74,4% |

Macro-F1 przed progami dla całego ocenialnego podzbioru wyniosło 0,885 dla
kategorii i 0,699 dla priorytetu. Baseline zawsze medium uzyskał 23/82 = 28,0%
accuracy priorytetu. Baseline jest punktem odniesienia, a nie oceną przydatności
systemu w organizacji.

Po zastosowaniu progów, z odmowami liczonymi jako brak trafienia, wyniki to
75/88 = 85,2% kategorii i 60/82 = 73,2% priorytetów. System przyjął automatycznie
81/88 ustalalnych kategorii i 78/82 priorytetów. Poprawność wśród tych przyjętych
wyniosła odpowiednio 92,6% i 76,9%; tych wartości nie należy podawać bez
pokrycia, ponieważ pomijają odmowy.

## Wykryte ograniczenie: niepewność nie oznacza braku informacji

Wśród nieustalalnych kategorii skierowano do weryfikacji tylko 2/12 = 16,7%.
Pozostałe 10 automatycznych etykiet nie mają wystarczającego oparcia w treści.
Przy nieustalalnym priorytecie było to tylko 1/18 = 5,6%; 17 przyjęto
automatycznie mimo braku potrzebnych informacji.

Nie doliczamy tych przypadków jako trafień lub pomyłek klasyfikacji, ponieważ
brakuje etykiety wzorcowej. Osobno pokazują słabość mechanizmu kierowania do
człowieka: wysoki wynik modelu może wystąpić także dla niepełnego opisu.
Przykładowo jawny objaw uprawnieniowy nie mówi jeszcze, jak pilne jest zadanie,
a informacja o blokadzie całego zespołu nie ujawnia technicznej kategorii.

Spośród 42 ustalalnych high/critical model zaniżył 3 do low/medium; wszystkie
te trzy odpowiedzi przeszły progi. Z 15 krytycznych opisów 9 otrzymało niższy
priorytet w surowym wyniku. Dla FINAL-EN-021 model wybrał medium zamiast
critical, a dla FINAL-EN-004 high zamiast critical; drugi przypadek został
skierowany do weryfikacji. Pomyłki i odmowy po ID są w raporcie.

## Jak odnieść to do pilotażu

Wcześniejsze 86,7% accuracy priorytetu jest wynikiem walidacji procedury doboru
na pilotażu. Obecne 74,4% pochodzi z osobnego, wcześniej nieocenianego zbioru
i nie zastępuje ani nie usuwa tamtego pomiaru. Rozdziały pracy powinny zachować
oba wyniki z właściwą nazwą protokołu.

Różnią się przypadki, ich rozkład i wersje bibliotek między lokalnym pilotażem
a zamrożonym Dockerem. Nie można przypisać spadku wyłącznie jednej przyczynie
ani na tej podstawie uznać konkretnej hipotezy o przeuczeniu za udowodnioną.
Wynik pokazuje ograniczoną skuteczność priorytetu i słabą detekcję niepełnych
opisów w tym badaniu. Dalsze poprawki należy dobierać na osobnej walidacji,
a nie przedstawiać ponownej oceny na tych 100 jako kolejnego niezależnego testu.

## Odtwarzalność i kontrola techniczna

Zapisano zatwierdzony zbiór, protokół, kod oceny, modele/progi, 120 referencji,
wektory zapytań, wyuczony model priorytetu i hashe artefaktów. Klasyfikację
wykonano zamrożonym kodem aplikacji; odpowiedź zapytania referencyjnego
odtworzono w pamięci z zapisanych wektorów. Nie czytano zmieniających się
ticketów ani referencji aplikacji.

Dodatkowy [test zgodności pgvector](../checks/pgvector-parity.json) obliczył
odległości dla wszystkich 100 zapytań wyłącznie z parametrów snapshotu w
transakcji tylko do odczytu. Sąsiedzi, kategoria przed/po progach i powody
weryfikacji były identyczne w 100/100 przypadków; największa różnica wyniku
podobieństwa wyniosła około 7,26e-8. Nie czytano tabel ticketów/referencji.

Przeszło 18 testów przygotowania i oceny, obejmujących mianowniki, null,
odmowy jako FN, normalizację kosinusa, remisy, zaniżenia priorytetu i brak
nadpisywania zamrożonego testu. Pełna końcowa ocena RAG nadal pozostaje poza
tym eksperymentem.

## Ograniczenia badania

Dane są syntetyczne, przygotowane przez asystenta znającego pilotaż i
sprawdzone przez jednego autora. Rozdzielenie od treningu nie zapewnia
niezależnego generatora ani naturalnego rozkładu przypadków. Opisy ogólne
mogą mieć podobny styl. Małe podzbiory, zwłaszcza 12 ocenialnych priorytetów
w słabej części, nie pozwalają na szerokie uogólnienia. Wynik dotyczy nowych
przypadków syntetycznych, nie rzeczywistych zgłoszeń organizacji.
