# Szczegółowy plan implementacji

Raport pomiaru etapu 4: [Pilotaż MiniLM — 2026-10-28](03-raport-pilotazu-minilm.md).

**Zmiana struktury (2026-10-28):** backend znajduje się w `backend/`, frontend w
`frontend/`, a pliki Compose w katalogu głównym. Historyczne ścieżki `app/`,
`data/`, `scripts/` i `tests/` poniżej odnoszą się teraz do `backend/`.
Aktualne polecenia uruchamiania znajdują się w głównym README.

Plan zaktualizowany na dzień: 2026-10-25.

Temat pracy: **System klasyfikacji zgłoszeń z wykorzystaniem embeddingów tekstowych, bazy wektorowej i asystenta konwersacyjnego opartego na RAG**.

Plan opisuje kolejność wykonania, konkretne zadania i kryteria ukończenia. Punktem wyjścia jest [stan projektu i zakres prac](01-stan-projektu-i-zakres-prac.md). W etapie 2 Celery zastąpiono przez FastAPI `BackgroundTasks`; Redis i Flower usunięto. Zależności od późniejszych etapów są oznaczone jako blockery przy zadaniach.

## Ustalenia i otwarte decyzje

- **Aktualizacja po review (2026-10-25):** użytkownik wybrał oddzielenie referencji KNN od operacyjnych zgłoszeń teraz, a eskalację po wdrożeniu kont. Dodano `classification_references` i seed przykładów demonstracyjnych z oryginalnymi kategoriami i priorytetami bazowymi. Stara eskalacja procentowa została usunięta. Wyniki automatyczne, checkbox, ręczny priorytet i zmiany statusu nie aktualizują referencji; nie kopiujemy do niej starych priorytetów. Nie oznacza to ukończenia E5.12: zatwierdzanie etykiet rozwiązanego zgłoszenia wymaga kont i kontroli uprawnień. Parametry reguły wielu różnych zgłaszających pozostają do wdrożenia w E5.6 po etapie 3.

- **Ograniczenie planowania:** czas przygotowania pracy jest ograniczony. Wybieramy możliwie prosty wariant spełniający uzgodniony zakres, koncentrując się na działającej integracji, klasyfikacji, RAG i rzetelnej ewaluacji. Dodatkowe funkcje wymagają uzasadnienia i nie są automatycznie dopisywane do podstawowego zakresu.
- **Ustalono:** zgłoszenia i pytania do asystenta będą w języku polskim. Dane referencyjne, walidacyjne i testowe należy przygotować w tym języku.
- **Ustalono:** cały interfejs użytkownika będzie po polsku, w tym formularze, przyciski, statusy, komunikaty walidacji i błędów, panel administratora oraz czat. Pytania i odpowiedzi asystenta również są po polsku.
- **Ustalono:** użytkownik sam rejestruje konto, podając e-mail i własne hasło; logowanie odbywa się adresem e-mail. Rejestracja wymaga dozwolonej domeny, początkowo `mail.com`, przechowywanej w konfiguracji. Konto oczekuje na akceptację administratora; przed akceptacją nie może zalogować się ani korzystać z chronionych funkcji.
- **Ustalono:** podczas akceptacji konta administrator musi jawnie nadać jedną z trzech ról: zgłaszający, osoba obsługująca albo administrator. Konto oczekujące nie ma nadanej roli; nie przypisujemy domyślnie roli zgłaszającego. Akceptację i nadanie roli zapisujemy razem. Rejestracja nie pozwala samodzielnie wybrać roli.
- **Poza zakresem:** resetowanie zapomnianego hasła. Nie implementujemy endpointów, tokenów i wiadomości e-mail do odzyskiwania dostępu ani resetowania hasła w panelu administratora.
- **Ustalono:** pierwsze konto administratora tworzymy jednorazową komendą podczas konfiguracji systemu, podając e-mail i hasło. Konto jest od razu aktywne i zatwierdzone, z rolą administratora. Komenda nie nadpisuje istniejących kont; kolejne konta przechodzą zwykłą rejestrację i akceptację.
- **Poza zakresem:** obsługa dezaktywacji konta wykonawcy mającego aktywne zgłoszenia. Nie dodajemy dla tego przypadku blokady dezaktywacji ani obowiązkowego przenoszenia zgłoszeń.
- **Ustalono:** historia czatu istnieje tylko w bieżącym widoku i znika po odświeżeniu strony lub wylogowaniu. Nie implementujemy listy zapisanych rozmów ani ich przywracania. Bieżąca historia może wspierać pytania uzupełniające; zapis danych potrzebnych do ewaluacji RAG pozostaje osobnym mechanizmem.
- **Ustalono:** asystent wyszukuje zgłoszenia, opisuje problemy i wcześniejsze rozwiązania oraz wskazuje źródła. Użytkownik może opisać bieżący problem, a asystent wyszuka podobne rozwiązane zgłoszenia i streści zapisane sposoby rozwiązania. Przy braku odpowiednich źródeł informuje o braku danych.
- **Poza zakresem asystenta:** pełne statystyki i zestawienia dotyczące całej bazy, np. dokładna liczba wszystkich zgłoszeń w miesiącu. Nie dodajemy w tym celu osobnego mechanizmu generowania lub wykonywania zapytań SQL przez LLM.
- **Do ponownego rozważenia:** pierwotne założenie lokalnego LLM. Sposób uruchamiania lub udostępnienia modelu, sprzęt i wybór modelu pozostają otwarte. Warianty do późniejszego porównania: komputer użytkownika, osobny serwer lub zewnętrzne API. Nie przyjęto żadnego z tych wariantów jako docelowego. Przed integracją ocenić jakość odpowiedzi po polsku, dostępne zasoby, czas odpowiedzi, koszt, sposób przekazywania danych i możliwość odtworzenia eksperymentów. Ewentualne odejście od lokalnego LLM uwzględnić również w formalnym zakresie pracy i opisie aspektu inżynierskiego. Decyzja nie zmienia ustalonego modelu embeddingów ani dostępu do asystenta według ról.
- **Ustalono:** model embeddingów `all-MiniLM-L6-v2` jest obowiązkowy i pozostaje zgodny z zakresem pracy. Należy zmierzyć jego jakość na polskich danych i opisać ograniczenia; zmiana modelu nie jest częścią planu.
- **Ustalono:** system będzie obsługiwał krótkie zgłoszenia, po kilka zdań opisujących problem. Obsługa rozbudowanych dokumentów i długich logów nie jest częścią podstawowego zakresu.
- **Konsekwencja implementacyjna:** w pierwszej wersji jedno zgłoszenie będzie reprezentowane jednym embeddingiem, bez dzielenia na fragmenty. Limit długości należy zweryfikować tokenizerem obowiązkowego modelu; zbyt długi tekst ma być odrzucany z czytelnym komunikatem zamiast cichego obcięcia.
- **Ustalono:** dziedziną systemu będzie helpdesk IT. Dane i scenariusze demonstracyjne mają dotyczyć krótkich zgłoszeń problemów informatycznych.
- **Wstępnie przyjęto:** cztery kategorie helpdesku IT: **Konta i uprawnienia**, **Sprzęt**, **Sieć i łączność**, **Oprogramowanie**. Podział należy sprawdzić na przykładowych danych; może zostać doprecyzowany przed zamrożeniem zbiorów do ewaluacji.
- **Wstępnie przyjęto:** polski zbiór zgłoszeń helpdesku IT przygotujemy samodzielnie. Plan nie zakłada dostępu do rzeczywistych zgłoszeń organizacji. Wstępny rozmiar to 300 zgłoszeń, około 75 na każdą z czterech kategorii, oraz 30 pytań do ewaluacji RAG i porównania wyszukiwania wektorowego z pełnotekstowym. Obie metody oceniamy na tych samych pytaniach; pulę 30 pytań dzielimy na walidację i test. Ręczną weryfikację treści, kategorii i priorytetu bazowego każdego przykładu wykonuje samodzielnie autor pracy. Nie planujemy drugiego oceniającego; ograniczenie to należy opisać przy interpretacji wyników. Pochodzenie i sposób przygotowania danych trzeba udokumentować; dane referencyjne, walidacyjne i testowe pozostają rozdzielone.
- **Ustalono:** przy tworzeniu przykładów możemy wspierać się LLM. Treść, kategorię i priorytet bazowy każdego przykładu sprawdzamy ręcznie przed dopuszczeniem do zbioru; propozycja generatora nie jest automatycznie etykietą wzorcową. Zapisujemy model generatora, instrukcje, ustawienia i pochodzenie danych. Jest to osobna decyzja od odłożonego wyboru LLM i sposobu udostępnienia asystenta RAG.
- **Ustalono:** cztery poziomy priorytetu: **Niski** (`low`), **Średni** (`medium`), **Wysoki** (`high`), **Krytyczny** (`critical`). Ich znaczenie opisano poniżej. KNN przewiduje priorytet bazowy na podstawie oznaczonych przykładów; reguły eskalacji opisano osobno, a szczegóły grupowania podobnych awarii wymagają doprecyzowania w etapie 5.
- **Ustalono:** formularz zawiera opis i dodatkowe pole dotyczące możliwości kontynuowania pracy. Osobą zgłaszającą jest automatycznie zalogowany użytkownik; formularz nie wymaga wybierania ani wpisywania autora.
- **Ustalono:** dodatkowym polem jest checkbox **„Nie mogę kontynuować pracy”**. Przy braku ręcznej decyzji administratora zaznaczenie oznacza blokadę pracy i nadaje najwyższy priorytet `critical`; przy niezaznaczonym polu priorytet bazowy wyznacza KNN. Reguła działa także dla pojedynczego zgłaszającego i nie wymaga awarii obejmującej wiele osób.
- **Ustalono:** administrator ma mieć endpoint umożliwiający ręczną zmianę priorytetu zgłoszenia. Decyzja administratora jest nadrzędna wobec checkboxa, KNN i automatycznej eskalacji; może obniżyć priorytet mimo zaznaczonego pola. Ponowna klasyfikacja nie nadpisuje tej decyzji.
- **Ustalono:** zgłaszający widzi historię wyłącznie własnych zgłoszeń, dodaje nowe i może sam anulować własne zgłoszenie przed przypisaniem wykonawcy. Osoba obsługująca i administrator widzą wszystkie zgłoszenia oraz mogą korzystać z asystenta LLM. Zgłaszający nie ma dostępu do asystenta.
- **Ustalono:** anulowanie przez zgłaszającego jest dostępne tylko w statusie Zgłoszony, gdy zgłoszenie nie ma wykonawcy, i nie wymaga zatwierdzenia. Po przypisaniu wykonawcy ta możliwość jest całkowicie zablokowana; nie przewidujemy mechanizmu próśb o anulowanie.
- **Ustalono:** sześć statusów procesu: **Zgłoszony**, **Przyjęty**, **W trakcie**, **Rozwiązany**, **Odrzucony**, **Anulowany**. Samodzielne anulowanie przed przypisaniem wykonawcy nadaje status Anulowany; rozwiązanie problemu nadaje status Rozwiązany. Przejście Zgłoszony → Odrzucony jest dostępne obsłudze i administratorowi; Przyjęty → Odrzucony oraz W trakcie → Odrzucony są dostępne wyłącznie administratorowi, niezależnie od przypisania wykonawcy.
- **Ustalono:** statusy **Rozwiązany**, **Odrzucony** i **Anulowany** są końcowe. Nie przewidujemy przejścia z nich do innego statusu ani ponownego otwarcia przez żadną rolę, również administratora. Zgłoszenie pozostaje dostępne w historii; powracający problem lub pomyłka przy odrzuceniu wymagają utworzenia nowego zgłoszenia.
- **Ustalono:** każde przejście na status Odrzucony wymaga krótkiego, niepustego powodu odrzucenia. Zapisujemy go z autorem i czasem decyzji; zgłaszający widzi powód w szczegółach własnego zgłoszenia. Powód nie zastępuje pierwotnego opisu problemu ani opisu rozwiązania.
- **Ustalono:** przejście na status **Rozwiązany** wymaga krótkiego, niepustego opisu rozwiązania podanego przez przypisanego wykonawcę lub administratora. Notatka zostaje zapisana przy zgłoszeniu i może stanowić kontekst odpowiedzi RAG o wcześniejszych sposobach rozwiązania problemu.
- **Ustalono:** osoba obsługująca może samodzielnie przyjąć nowe zgłoszenie; zostaje jego opiekunem, a status zmienia się ze Zgłoszony na Przyjęty. Administrator może przypisać zgłoszenie wybranej osobie obsługującej oraz później zmienić wykonawcę. Rozpoczęcie realizacji zmienia status na W trakcie.
- **Ustalono:** rozpocząć realizację i oznaczyć zgłoszenie jako Rozwiązany mogą wyłącznie aktualnie przypisany wykonawca oraz administrator. Pozostali pracownicy obsługi zachowują podgląd wszystkich zgłoszeń.
- **Ustalono:** obowiązuje kolejność realizacji **Przyjęty → W trakcie → Rozwiązany**. Przejście na Rozwiązany jest dozwolone wyłącznie ze statusu W trakcie; nie można go pominąć, również jako administrator. Nadal wymagany jest opis rozwiązania i uprawnienie aktualnego wykonawcy lub administratora.
- **Ustalono:** KNN korzysta z zatwierdzonych przykładów referencyjnych, duplikaty i eskalacja z aktywnych zgłoszeń (Zgłoszony, Przyjęty, W trakcie), a RAG również z historii z jawnym statusem. Rozwiązane sprawy można dodać do referencji po osobnym zatwierdzeniu etykiet. Zmiana statusu nie uruchamia ponownie KNN.
- **Ustalono:** etykiety rozwiązanego zgłoszenia przed dodaniem do referencji KNN mogą zatwierdzać aktualnie przypisany wykonawca oraz administrator. Zatwierdzenie dotyczy kategorii i priorytetu bazowego; nie nadaje wykonawcy prawa do zmiany priorytetu końcowego ustalonego przez administratora.
- **Ustalono:** zgłaszający może edytować opis i checkbox blokady pracy wyłącznie własnego zgłoszenia w statusie Zgłoszony. Po przyjęciu do realizacji te pola są dla niego zablokowane. Zmiana opisu uruchamia ponowną klasyfikację, a zmiana samego checkboxa nie wymaga nowego embeddingu; ręczna decyzja administratora o priorytecie pozostaje nadrzędna.
- **Ustalono:** ręczne ponowienie nieudanej lub przerwanej klasyfikacji przysługuje autorowi własnego nieprzypisanego zgłoszenia w statusie Zgłoszony, aktualnemu wykonawcy w statusach Przyjęty i W trakcie oraz administratorowi dla każdego aktywnego zgłoszenia. Nie ponawiamy zadania dla spraw końcowych ani poprawnie zakończonej klasyfikacji wyłącznie w celu wymuszenia innego wyniku. Ponowienie nie zmienia statusu obsługi i dotyczy aktualnej wersji treści.
- **Ustalono:** kategorię operacyjną zgłoszenia może ręcznie poprawić aktualnie przypisany wykonawca albo administrator. Zachowujemy pierwotne przewidywanie KNN oraz autora i czas korekty. Korekta kategorii nie zatwierdza automatycznie przykładu do referencji KNN i nie zmienia uprawnień do priorytetu końcowego.
- **Ustalono:** po przyjęciu zgłoszenia pierwotny opis pozostaje niezmienny dla wszystkich ról, również osoby obsługującej i administratora. Opis rozwiązania jest osobnym polem i nie zastępuje opisu problemu.
- **Ustalono:** kilka podobnych aktywnych zgłoszeń od różnych użytkowników stanowi podstawę automatycznego podniesienia priorytetu jako sygnał większej awarii. Reguła obejmuje wszystkie cztery kategorie: Konta i uprawnienia, Sprzęt, Sieć i łączność oraz Oprogramowanie. Liczymy różnych zgłaszających, aby wielokrotne zgłoszenie jednej osoby nie zwiększało liczby dotkniętych użytkowników. Przy spełnieniu warunków eskalacja zapewnia priorytet co najmniej Wysoki: Niski i Średni podnosi do Wysokiego, Wysoki zachowuje, a Krytycznego nie obniża. Eskalacja respektuje ręczny priorytet administratora, także niższy, i nie zmienia priorytetu bazowego przewidzianego przez KNN.
- **Ustalono:** początkowy próg eskalacji to co najmniej **3 różnych użytkowników** z podobnymi aktywnymi zgłoszeniami **utworzonymi w ostatnich 24 godzinach**. Liczba użytkowników i długość okna są konfigurowalne; sprawdzamy je na danych walidacyjnych, a przed końcową ewaluacją zamrażamy wybraną konfigurację.
- **Ustalono:** po osiągnięciu progu eskalacja obejmuje wszystkie podobne aktywne zgłoszenia utworzone w tym oknie czasowym, również wcześniejsze. Na każdym zgłoszeniu osobno respektujemy ręczną decyzję administratora i zachowujemy Krytyczny, jeśli obowiązuje.
- **Ustalono:** spadek liczby aktywnych zgłoszeń lub upływ 24 godzin nie cofają już zastosowanej eskalacji. Podniesiony w ten sposób priorytet może obniżyć administrator; automatyczne przeliczenie nie usuwa skutku eskalacji.
- **Ustalono:** warunki eskalacji sprawdzamy po udanej klasyfikacji nowego zgłoszenia, po ponownej klasyfikacji zmienionego opisu oraz po udanym ponowieniu zadania. Wynik musi dotyczyć aktualnej wersji treści, a zgłoszenia nadal należeć do aktywnych statusów.
- **Ustalono:** cofanie statusu jest zablokowane, w szczególności W trakcie → Przyjęty. Zmiana wykonawcy przez administratora zachowuje bieżący status zgłoszenia. Dozwolone przejścia zebrano w macierzy poniżej; próg podobieństwa należy dobrać na walidacji.
- **Ustalono:** przy słabym dopasowaniu KNN nie wymuszamy kategorii; wynik klasyfikacji otrzymuje oznaczenie **Do weryfikacji**. To osobna informacja od statusu obsługi zgłoszenia i stanu wykonania zadania. Ręczne uzupełnienie kategorii przysługuje aktualnie przypisanemu wykonawcy i administratorowi zgodnie z E5.13.
- **Ustalono:** przy niewiarygodnym przewidywaniu priorytetu bazowego przyjmujemy tymczasowo Średni (`medium`). Wartość zastępczą oznaczamy osobno od przewidywania KNN i zachowujemy potrzebę weryfikacji. Decyzja administratora, checkbox i zapisana eskalacja mają pierwszeństwo; wartość tymczasowa nie jest zatwierdzoną etykietą referencyjną.
- **Ustalono:** wykrywanie potencjalnych duplikatów zwraca sugestie podobnych aktywnych zgłoszeń. System nie scala ani nie odrzuca zgłoszeń automatycznie. Decyzję podejmuje obsługa lub administrator zgodnie z uprawnieniami do zmiany statusu; sugestia nie rozszerza tych uprawnień.
- **Konsekwencja implementacyjna:** obecne kategorie `bug`, `performance`, `feature` i reguły eskalacji trzeba dostosować do docelowej dziedziny. Nie zakładamy automatycznego przypisania starych przykładów do nowych kategorii.
- **Stan kodu:** istniejące przykłady zgłoszeń są angielskie; polskie dane i ich obsługa nie zostały jeszcze zaimplementowane ani zweryfikowane.

## Przyjęte znaczenie priorytetów

| Priorytet | Znaczenie | Przykład |
|---|---|---|
| **Niski** (`low`) | Drobna uciążliwość, praca może być kontynuowana. | Nieprawidłowe wyświetlanie ikon w programie. |
| **Średni** (`medium`) | Utrudnienie pracy, ale istnieje obejście. | Drukarka nie działa, można użyć innej. |
| **Wysoki** (`high`) | Ważne zadanie jest zablokowane, brak obejścia. | Pracownik nie może zalogować się do systemu potrzebnego do pracy. |
| **Krytyczny** (`critical`) | Niedostępność kluczowej usługi blokuje pracę wielu osób. | Awaria sieci uniemożliwia pracę całego działu. |

Definicje opisują priorytet bazowy i służą do etykietowania danych oraz oceny przewidywań KNN. Kategorie i priorytety stanowią osobne etykiety; nie przypisujemy jednego stałego priorytetu do całej kategorii.

Przy braku ręcznej decyzji administratora reguła formularza nadaje priorytet końcowy **Krytyczny** po zaznaczeniu **„Nie mogę kontynuować pracy”**, również gdy KNN przewiduje niższy priorytet i problem dotyczy jednej osoby. Bez zaznaczenia priorytet bazowy pochodzi z KNN. Przewidywanie modelu należy zachować osobno od priorytetu końcowego.

**Pierwszeństwo:** ręczna decyzja administratora → reguła checkboxa → priorytet KNN z ewentualnymi dodatkowymi regułami eskalacji. Decyzję administratora należy przechowywać osobno od przewidywania i oznaczyć źródło priorytetu końcowego. Zmiana treści lub checkboxa oraz zakończenie trwającej albo ponowionej klasyfikacji nie mogą samodzielnie usunąć tej decyzji. Reguły eskalacji opisano poniżej; szczegóły grupowania podobnych awarii rozstrzygamy w etapie 5.

Gdy nie ma ręcznej decyzji administratora i eskalacja została zastosowana, priorytet automatyczny wynosi maksimum z priorytetu bazowego KNN i zapisanego minimum Wysoki. To minimum pozostaje zapisane po spadku liczby aktywnych spraw i po upływie okna czasowego; nie znika przy ponownej klasyfikacji ani przeliczeniu checkboxa. Checkbox nadal wymusza Krytyczny, a ręczna decyzja administratora ma pierwszeństwo także przed zapisanym minimum eskalacji. Przypadki Niski → Wysoki, Średni → Wysoki, Wysoki → Wysoki i Krytyczny → Krytyczny, trwałość eskalacji oraz zachowanie niższej decyzji administratora uwzględnić w scenariuszach E4.6 i weryfikacji E5.10.

Jeśli priorytet bazowy KNN jest niewiarygodny, do wyznaczenia priorytetu końcowego używamy wartości zastępczej Średni. Bez innych reguł daje to Średni; zapisana eskalacja podnosi go do Wysokiego, checkbox wymusza Krytyczny, a decyzja administratora pozostaje nadrzędna. Źródło wartości zastępczej i potrzeba weryfikacji pozostają widoczne niezależnie od końcowego poziomu priorytetu. W ewaluacji nie zaliczamy wartości zastępczej jako poprawnego przewidywania KNN; raportujemy skierowanie do weryfikacji.

Warunki początkowe: minimum 3 różnych zgłaszających, podobieństwo spełniające próg dobrany na walidacji, aktywny status oraz data utworzenia zgłoszenia w ostatnich 24 godzinach. Okno dotyczy utworzenia, a nie ostatniej edycji lub zmiany statusu. W scenariuszach E4.6 uwzględnić 2, 3 i 4 różnych użytkowników, wielokrotne zgłoszenia jednej osoby oraz rekordy na granicy 24 godzin. Do odtworzenia eksperymentów zapisywać czas odniesienia dla okna.

Eskalacja obejmuje wszystkie podobne aktywne zgłoszenia z kwalifikującego się okna, także wcześniejsze; nie ogranicza się do nowo przetwarzanego zgłoszenia. Sprawdzić scenariusz, w którym trzecia osoba powoduje podniesienie priorytetu także dwóch wcześniejszych spraw. Zgłoszenie z ręcznym priorytetem administratora pozostaje objęte oceną liczby różnych użytkowników, lecz jego priorytet nie jest nadpisywany. Przy aktualizacji każdej sprawy ponownie sprawdzać aktywny status i brak ręcznej decyzji, aby równoległe rozwiązanie lub zmiana priorytetu nie zostały pominięte.

## Przyjęte role i obsługa zgłoszeń

| Rola | Widoczność | Ustalone uprawnienia |
|---|---|---|
| **Zgłaszający** | Historia i szczegóły własnych zgłoszeń, niezależnie od ich statusu. | Dodawanie zgłoszeń, edycja własnego opisu i checkboxa tylko w statusie Zgłoszony oraz samodzielne anulowanie własnego nieprzypisanego zgłoszenia w tym statusie. Po przypisaniu wykonawcy anulowanie jest zablokowane. Brak dostępu do asystenta LLM i nadawania statusu Odrzucony. |
| **Osoba obsługująca** | Wszystkie zgłoszenia. | Samodzielne przyjmowanie nowych zgłoszeń jako opiekun, rozpoczęcie i zakończenie realizacji, korekta kategorii oraz zatwierdzanie etykiet referencyjnych tylko własnych przypisanych spraw, korzystanie z asystenta LLM i odrzucanie zgłoszeń wyłącznie w statusie Zgłoszony. |
| **Administrator** | Wszystkie zgłoszenia. | Przypisywanie zgłoszeń i zmiana wykonawcy, rozpoczęcie i zakończenie realizacji, korekta kategorii oraz zatwierdzanie etykiet referencyjnych niezależnie od przypisania, korzystanie z asystenta LLM, zarządzanie kontami, ręczna zmiana priorytetu i odrzucanie zgłoszeń w statusach Zgłoszony, Przyjęty i W trakcie. |

Anulowanie to bezpośrednie przejście **Zgłoszony → Anulowany** wykonywane przez autora, wyłącznie gdy nie przypisano wykonawcy. Po przypisaniu wykonawcy zgłaszający nie może ani anulować sprawy, ani wysłać prośby o anulowanie. Nie tworzymy osobnego modelu prośby i procesu zatwierdzania. Anulowanie i przyjęcie lub przypisanie muszą być zabezpieczone przed wyścigiem: zatwierdzenie jednej operacji uniemożliwia wykonanie sprzecznej operacji.

Status procesu zgłoszenia, stan wykonania zadania klasyfikacji i oznaczenie wyniku **Do weryfikacji** są odrębnymi informacjami. Klasyfikacja nie oznacza automatycznie przyjęcia zgłoszenia do obsługi. Zadanie może zakończyć się technicznie poprawnie, a mimo to skierować wynik do ręcznej weryfikacji; słabe dopasowanie nie powinno być przedstawiane jako błąd modelu lub bazy.

Przycisk **„Przyjmij zgłoszenie”** przypisuje aktualnie zalogowaną osobę obsługującą jako opiekuna i zmienia status **Zgłoszony → Przyjęty**. Przydzielenie nowego zgłoszenia przez administratora również wskazuje wykonawcę i przyjmuje je do realizacji. Rozpoczęcie pracy daje przejście **Przyjęty → W trakcie**.

Zakończenie realizacji daje wyłącznie przejście **W trakcie → Rozwiązany**, z obowiązkowym opisem rozwiązania. Bezpośrednie Zgłoszony → Rozwiązany i Przyjęty → Rozwiązany są zabronione dla wszystkich ról, również administratora. Interfejs udostępnia akcję rozwiązania dopiero w statusie W trakcie, a backend niezależnie sprawdza status źródłowy i uprawnienia.

Administrator może zmienić wykonawcę już przypisanego zgłoszenia, zachowując jego bieżący status. Zmiana wykonawcy nie cofa W trakcie do Przyjęty. Należy zachować historię przypisań oraz pierwotnego zgłaszającego; sama zmiana opiekuna nie oznacza rozpoczęcia nowego zgłoszenia ani ponownego otwarcia rozwiązanego. W implementacji trzeba zabezpieczyć przyjęcie tego samego zgłoszenia jednocześnie przez dwie osoby. Rozpoczęcie i zakończenie realizacji przysługuje aktualnie przypisanemu wykonawcy oraz administratorowi; po zmianie opiekuna poprzedni wykonawca traci to uprawnienie do danej sprawy.

### Przyjęte statusy zgłoszenia

| Status | Znaczenie |
|---|---|
| **Zgłoszony** | Oczekuje na rozpatrzenie. |
| **Przyjęty** | Został zaakceptowany do realizacji. |
| **W trakcie** | Trwa obsługa zgłoszenia. |
| **Rozwiązany** | Problem został rozwiązany; zapisano obowiązkowy krótki opis rozwiązania. |
| **Odrzucony** | Obsługa lub administrator odrzucili nowe zgłoszenie; po przyjęciu albo rozpoczęciu pracy odrzucenia może dokonać wyłącznie administrator. Wymagany jest krótki powód odrzucenia, widoczny dla zgłaszającego. |
| **Anulowany** | Zgłaszający sam anulował własne zgłoszenie przed przypisaniem wykonawcy. |

Lista statusów jest ustalona. **Rozwiązany, Odrzucony i Anulowany** są stanami końcowymi bez przejść do innych statusów i bez możliwości ponownego otwarcia, również przez obsługę lub administratora. Końcowość dotyczy statusu procesu; zachowujemy osobno uzgodnione operacje, takie jak zatwierdzanie etykiet rozwiązanego zgłoszenia do referencji KNN. Cofanie statusu, w szczególności W trakcie → Przyjęty, jest zablokowane dla wszystkich ról. Zmiana wykonawcy zachowuje bieżący status. Dozwolone przejścia przedstawia poniższa macierz. Obecne `open`, `resolved`, `closed` opisują stan kodu i wymagają migracji po ustaleniu pełnego procesu.

| Przejście | Uprawniony użytkownik i warunki |
|---|---|
| Zgłoszony → Przyjęty | Obsługa przyjmuje na siebie albo administrator przypisuje wykonawcę; zapis statusu i przypisania razem. |
| Przyjęty → W trakcie | Aktualnie przypisany wykonawca albo administrator. |
| W trakcie → Rozwiązany | Aktualnie przypisany wykonawca albo administrator; wymagany opis rozwiązania. |
| Zgłoszony → Odrzucony | Obsługa albo administrator; wymagany powód odrzucenia. |
| Przyjęty → Odrzucony | Wyłącznie administrator; wymagany powód odrzucenia. |
| W trakcie → Odrzucony | Wyłącznie administrator; wymagany powód odrzucenia. |
| Zgłoszony → Anulowany | Autor własnego zgłoszenia, wyłącznie bez przypisanego wykonawcy. |

Pozostałe przejścia są niedozwolone. Zmiana wykonawcy jest osobną operacją bez zmiany statusu.

## Przyjęty wpływ statusów na klasyfikację

Poniższe zasady zostały przyjęte do planu i wymagają dalszej implementacji. Kod KNN nadal pobiera sąsiadów bez filtra referencji. W etapie 1 dostosowano dotychczasowe duplikaty i eskalację z `open` do trzech nowych aktywnych statusów; docelowe rozdzielenie zbiorów, zatwierdzanie referencji i reguły eskalacji pozostają w etapie 5.

### Kiedy wykonywać klasyfikację

- Nowe zgłoszenie otrzymuje status Zgłoszony i zadanie wyznaczające embedding, kategorię oraz priorytet bazowy. Sam wynik nie zmienia biznesowego statusu zgłoszenia.
- Samo przejście Przyjęty → W trakcie → Rozwiązany ani zmiana wykonawcy nie uruchamia ponownie KNN i nie zmienia kategorii.
- Zmiana opisu przez zgłaszającego jest dozwolona tylko we własnym zgłoszeniu w statusie Zgłoszony i uruchamia nowe zadanie klasyfikacji. Jawne ponowienie po błędzie również może uruchamiać zadanie. Nadal obowiązują wersjonowanie treści i pierwszeństwo priorytetu administratora.
- Ręczne ponowienie po błędzie lub przerwaniu respektuje rolę i aktualne przypisanie: autor przed przypisaniem, bieżący wykonawca podczas obsługi oraz administrator dla aktywnych spraw. Wynik Do weryfikacji po poprawnym wykonaniu nie jest błędem uprawniającym do ponowienia; wymaga oceny człowieka.
- Zmiana checkboxa wpływa na priorytet końcowy według przyjętych zasad; sama nie wymaga nowego embeddingu, jeśli tekst pozostał bez zmian.
- Zakończenie zadania klasyfikacji nie może przywrócić aktywnego statusu po rozwiązaniu, odrzuceniu lub anulowaniu. Proponuje się zachować ewentualny spóźniony wynik osobno bez zmiany priorytetu końcowego zakończonej sprawy.

### Zbiory wykorzystywane przez poszczególne mechanizmy

| Status zgłoszenia operacyjnego | Przykład referencyjny KNN | Kandydat na duplikat bieżącej awarii i udział w eskalacji | Kontekst RAG dla obsługi i administratora |
|---|---|---|---|
| **Zgłoszony** | Nie; etykiety mogą być jeszcze niezweryfikowane. | Tak, przy aktualnym embeddingu i spełnieniu pozostałych warunków. | Tak, ze wskazaniem statusu. |
| **Przyjęty** | Nie; przyjęcie do realizacji nie zatwierdza automatycznie etykiet. | Tak, przy aktualnym embeddingu i spełnieniu pozostałych warunków. | Tak. |
| **W trakcie** | Nie; obsługa nie została zakończona. | Tak, przy aktualnym embeddingu i spełnieniu pozostałych warunków. | Tak. |
| **Rozwiązany** | Może zostać dodany po osobnym zatwierdzeniu kategorii i priorytetu bazowego; sam status nie wystarcza. | Nie; może być znaleziony jako podobny historyczny problem, ale nie jako nadal aktywna awaria. | Tak, wraz z zapisanym opisem rozwiązania. |
| **Odrzucony** | Nie. | Nie. | Tak, jako historia z jawnym statusem; nie przedstawiać jako rozwiązanej sprawy. |
| **Anulowany** | Nie. | Nie. | Tak, jako historia z jawnym statusem; nie przedstawiać jako rozwiązanej sprawy. |

Należy oddzielić trzy zbiory: **zatwierdzone przykłady do KNN**, **aktywne zgłoszenia do duplikatów i eskalacji** oraz **dostępne zgłoszenia historyczne do RAG**. Wspólny embedding nie oznacza identycznych filtrów dla tych mechanizmów.

Klasyfikator od pierwszego uruchomienia korzysta z przygotowanego, ręcznie oznaczonego polskiego zbioru referencyjnego. Nie musi czekać na rozwiązanie pierwszych zgłoszeń w aplikacji. Rozszerzanie zbioru o zakończone sprawy jest kontrolowane i nie może zmieniać referencji podczas końcowego eksperymentu.

Priorytet końcowy wymuszony checkboxem, regułą eskalacji lub decyzją administratora nie staje się automatycznie etykietą priorytetu bazowego dla KNN. Etykiety rozwiązanego zgłoszenia zatwierdza jego aktualnie przypisany wykonawca albo administrator. Zatwierdzenie obejmuje kategorię i priorytet bazowy oraz zapis osoby zatwierdzającej, czasu i wersji treści. Nie zmienia statusu Rozwiązany ani priorytetu końcowego i nie narusza pierwszeństwa ręcznej decyzji administratora. Pozostali pracownicy obsługi i zgłaszający nie mają prawa zatwierdzić takiego przykładu.

Samodzielne anulowanie przed przypisaniem wykonawcy zmienia status na Anulowany i usuwa zgłoszenie ze zbioru aktywnych spraw. Rozwiązanie i odrzucenie również wykluczają sprawę z kolejnych ocen warunków eskalacji. Spadek liczby aktywnych spraw nie obniża już podniesionych priorytetów pozostałych zgłoszeń. Warunki eskalacji sprawdzamy po udanej klasyfikacji nowego zgłoszenia, po ponownej klasyfikacji zmienionego opisu oraz po udanym ponowieniu zadania, z kontrolą aktualnej wersji treści i bieżących statusów.

## Jak korzystać z planu

- Każdy etap kończymy sprawdzeniem kryteriów ukończenia i zapisaniem wyniku weryfikacji.
- Pole `[ ]` oznacza zadanie zaplanowane; `[x]` oznacza zadanie wykonane i zweryfikowane. Istniejący prototyp nie oznacza automatycznie ukończenia zadania.
- Identyfikatory, np. `E2.3`, pozwalają odnosić się do pojedynczych zadań w dalszej pracy.
- Migracje bazy, testy, konfigurację Compose i dokumentację aktualizujemy razem z daną funkcją.
- Decyzje wskazane w zadaniach rozstrzygamy przed implementacją zależnej funkcji i zapisujemy ich uzasadnienie.
- Poniższe nazwy endpointów są propozycją kontraktu do ustalenia w odpowiednim etapie.

## Przypomnienia dla asystenta podczas implementacji

Przed rozpoczęciem etapu przeczytać jego sekcję „Przypomnienie dla asystenta”. Zawiera ona odłożone decyzje, a nie dodatkowe funkcje ani już zaakceptowane rozwiązania. Wracać do nich przed wykonaniem zależnej części, gdy są dostępne przykłady, warianty lub wyniki pomiarów.

- Pytać krótko, zwykle o jedną rzecz naraz, przedstawiając rekomendację i jej skutek. Nie powtarzać pytań, na które użytkownik już odpowiedział; odpowiedź zapisać w ustaleniach i odpowiednich zadaniach.
- Pytać o brakujące wymagania, dane lub wybory wpływające na zakres i zachowanie systemu. Rutynowe decyzje techniczne podejmować samodzielnie i dokumentować; nie wymagać akceptacji każdego endpointu, biblioteki ani wartości parametru.
- Parametry KNN, podobieństwa, wyszukiwania i generowania dobierać na walidacji. Pokazać wyniki i kompromisy, zamiast oczekiwać od użytkownika zgadywania wartości. Nie stroić na teście.
- Kontynuować niezależne zadania, gdy odpowiedź jest potrzebna tylko do części etapu. Propozycji zapisanej poniżej nie traktować jako zgody na zmianę uzgodnionego zakresu.
- Nie pytać o terminy ani nie przywracać wyłączonych funkcji: resetowania hasła, trwałej historii czatu, próśb o anulowanie, statystyk całej bazy przez LLM i obsługi dezaktywacji wykonawcy z aktywnymi zgłoszeniami.

## Zestawienie etapów

| Etap | Zakres | Zależności | Rezultat |
|---|---|---|---|
| **1** | Stabilizacja API i sposobu uruchamiania | Obecny prototyp | Poprawne podstawowe operacje na zgłoszeniach i powtarzalne testy. |
| **2** | Migracja z Celery na BackgroundTasks | Etap 1 | Klasyfikacja w tle ze stanem zapisanym w PostgreSQL. |
| **3** | Użytkownicy, JWT i role | Etapy 1–2 | API egzekwujące uprawnienia do zgłoszeń i zadań. |
| **4** | Dane i przygotowanie ewaluacji | Etap 3; zbieranie danych można rozpocząć wcześniej | Oddzielone zbiory referencyjny, walidacyjny i testowy oraz kryteria oceny. |
| **5** | Klasyfikator i duplikaty | Etapy 2–4 | Klasyfikacja z dobranymi parametrami i sugestiami duplikatów. |
| **6** | Podstawowy frontend React | Etapy 3 i 5 | Obsługa zgłoszeń przez interfejs użytkownika. |
| **7** | Wyszukiwanie semantyczne i pełnotekstowe | Etapy 3–5 | Dwa porównywalne mechanizmy pobierania kontekstu. |
| **8** | Asystent RAG i czat | Etapy 6–7 oraz decyzja o wariancie LLM | Odpowiedzi LLM ze źródłami i kontrolą dostępu; sposób udostępnienia modelu do ustalenia. |
| **9** | Administracja i domknięcie systemu | Etapy 3, 6 i 8 | Kompletny system uruchamiany przez Docker Compose. |
| **10** | Końcowe eksperymenty i opracowanie wyników | Etapy 4–9 | Wyniki klasyfikacji, duplikatów i porównania metod RAG. |

**Aktualizacja po etapie 3 i domknięciu zaległości (2026-10-25):** E1.1–E1.9 i E2.1–E2.12 ukończone. Uzupełniono macierz odmów zmiany statusów końcowych dla wszystkich ról i aliasu DELETE, pełne ponowienie z zachowaniem decyzji administratora oraz oba porządki wyścigu edycji zgłaszającego z przyjęciem przez inną osobę obsługi. E2.5 domknięto przez wdrożenie podstawy E5.13: osobnego przewidywania i wersjonowanej korekty kategorii, jej ochrony podczas klasyfikacji i testów. Pełne E5.13 pozostaje niezaznaczone do integracji z zatwierdzonymi referencjami z E5.12 i docelowym słownikiem kategorii. **Weryfikacja:** 85/85 testów pełnej regresji na osobnym PostgreSQL/pgvector, w tym migracje, Uvicorn i restart procesu. Nie zmieniano bazy demonstracyjnej.

## Etap 1. Stabilizacja podstawowego API

**Stan aktualny (2026-10-25):** E1.1–E1.9 ukończone, łącznie z rolami, przypisaniami i pełną weryfikacją końcowości statusów dla każdej roli. Poniższe opisy historyczne dokumentują przebieg wcześniejszych weryfikacji; aktualne oznaczenia zadań uwzględniają etap 3 i uzupełnienie testów.

**Decyzja użytkownika po odczycie bazy:** 10 angielskich rekordów odpowiada `data/sample_tickets.json` i stanowi dane demonstracyjne. Zachowujemy je teraz, jawnie mapując `open → reported` (Zgłoszony). Nie dopisujemy autorów; ich obsługę należy rozstrzygnąć przed E3.3. Wszystkie rekordy miały `open`, więc nie było potrzeby decydowania o znaczeniu istniejących `closed` ani `resolved`. Migracja innych baz wymaga jawnego mapowania wszystkich występujących starych statusów.

**Decyzje techniczne etapu 1 (stan historyczny, 2026-10-11):** wartości API to `reported`, `accepted`, `in_progress`, `resolved`, `rejected`, `cancelled`; polskie odpowiedniki zapisano w README. Podstawową operacją jest `PATCH /tickets/{id}/status`. Stary `DELETE` pozostaje przestarzałym aliasem zakończenia z wymaganym jawnym statusem końcowym i tą samą macierzą przejść; nie usuwa danych ani nie pomija kolejności realizacji. Notatki rozwiązania/odrzucenia i czas są zapisywane razem ze statusem. Role, autorzy decyzji, przypisania i historia wykonawców nadal należą do etapu 3; E1.5 i E1.9 weryfikują przejścia i końcowość niezależnie od przyszłej roli. Po dodaniu autoryzacji pozostaje sprawdzenie tej macierzy dla każdej roli zgodnie z E3.9–E3.13.

**Weryfikacja:** 13 testów `unittest` przeszło na osobnym PostgreSQL/pgvector (`issuetracker_test`, port 5434, osobny projekt Compose i tmpfs). Obejmują tworzenie, odczyt, 404, walidację, filtry, stabilną paginację, wszystkie 36 par statusów, wymagane notatki, przestarzały DELETE, historię i nowe zgłoszenie tego samego problemu, równoległe przyjęcie/anulowanie, aktywne duplikaty pgvector, seed oraz migracje. Prawdziwy tokenizer potwierdza przyjęcie 256 i odrzucenie 257 tokenów z tokenami specjalnymi. W testach API wysyłanie Celery jest zastąpione atrapą; jakość KNN i pełny potok zadania nie były przedmiotem tej weryfikacji.

Sprawdzono tworzenie schematu od zera, odmowę migracji starych danych bez decyzji, migrację z jawnym mapowaniem, zachowanie rekordów, blokadę utraty danych przy downgrade oraz zgodność metadanych ORM z bazą. Baza demonstracyjna jest na `e1a000000002`; zachowano 10 rekordów z ich dotychczasowymi treściami, kategoriami, priorytetami i wektorami 384. Ponowne seedowanie pominęło niepustą bazę. Po zbudowaniu aktualnych obrazów uruchomiono usługi Compose; działające API potwierdziło 200 dla listy i szczegółów, 404 dla brakującego rekordu i 422 dla starego statusu. Instrukcja i przykładowe zmienne bez sekretów znajdują się w README i `.env*.example`.

**Historyczny wynik audytu kompletności (2026-10-11):** ponowiono 13 testów na nowej, osobnej bazie PostgreSQL/pgvector — wszystkie przeszły. Niezależnie porównano macierz przejść z wymaganiami. Działające API zwróciło 200 dla listy, szczegółów i OpenAPI, 404 dla brakującego zgłoszenia oraz 422 dla starego statusu; w bazie demonstracyjnej nadal jest 10 rekordów reported. Docker obecnie działa. Wcześniejsze zaznaczenie całych E1.5 i E1.9 jako wykonanych było zbyt szerokie. W E1.5 gotowe są modele odpowiedzi, sześć statusów, macierz przejść, końcowość, migracje i ukrywanie wektorów. Pozostają uprawnienia ról oraz zachowanie statusu przy zmianie wykonawcy, które wymagają użytkowników i przypisań z E3.1, E3.6 i E3.11–E3.13. W E1.9 gotowe są testy podstawowego API i przejść; pozostaje jawnie zaplanowana weryfikacja dla wszystkich ról po autoryzacji (E3.9). Pola tych dwóch zadań pozostawiono niezaznaczone do pełnego domknięcia ich treści. Nie zmieniono zakresu ani kolejności etapów.

**Przypomnienie odnotowane:** formalny opis pracy należy ujednolicić z zaakceptowaną zmianą Celery na BackgroundTasks. W aktualnym kodzie nie ma Celery, Redis ani Flower.

**Stan początkowy:** jest tworzenie i lista zgłoszeń oraz zmiana statusu. Pobieranie pojedynczego zgłoszenia jest puste, a zamykanie zgłoszenia odwołuje się do niezdefiniowanego `db`.

**Cel:** uzyskać działający, sprawdzalny fundament przed zmianą sposobu przetwarzania.

### Przypomnienie dla asystenta

- Przed migracją istniejących rekordów sprawdzić ich zawartość i zapytać, czy są to wyłącznie dane demonstracyjne do zastąpienia, czy dane wymagające zachowania. Pokazać proponowane postępowanie ze starymi statusami i brakującymi autorami; nie zgadywać ich znaczenia ani nie usuwać danych bez ustalenia.
- Przypomnieć o ujednoliceniu formalnego opisu pracy ze zmianą Celery na BackgroundTasks. Sama zmiana technologii jest już zaakceptowana i nie wymaga ponownego pytania.

### Zadania

- [x] **E1.1** Uruchomić PostgreSQL/pgvector i obecne API; zapisać wymagane zmienne środowiskowe w pliku przykładowym bez sekretów.
- [x] **E1.2** Uporządkować inicjalizację bazy: migracje Alembic jako sposób tworzenia schematu, osobny skrypt danych początkowych. Wyeliminować rozbieżności między migracjami i `create_all` w skrypcie seedującym.
- [x] **E1.3** Zaimplementować `GET /tickets/{ticket_id}` wraz z odpowiedzią 404 dla nieistniejącego zgłoszenia.
- [x] **E1.4** Naprawić przekazywanie sesji bazy do zamykania zgłoszenia. Ustalić jeden spójny sposób zamykania i zachowanie istniejącego endpointu `DELETE`, który obecnie nie usuwa rekordu.
- [x] **E1.5** Ujednolicić modele odpowiedzi i błędy. Wdrożyć sześć ustalonych statusów: Zgłoszony, Przyjęty, W trakcie, Rozwiązany, Odrzucony, Anulowany. Zablokować przejścia ze stanów Rozwiązany, Odrzucony i Anulowany dla wszystkich ról; wdrożyć przyjętą macierz przejść w aktywnej obsłudze i zablokować cofanie statusu, również W trakcie → Przyjęty. Zmiana wykonawcy zachowuje bieżący status. Przygotować migrację obecnych `open`, `resolved`, `closed` bez arbitralnego przypisywania istniejących rekordów do nieznanych etapów obsługi. Nie zwracać przypadkowo wektora embeddingu w odpowiedziach operacji na zgłoszeniach. **Wykonane:** reguły ról i zachowanie statusu przy zmianie wykonawcy wdrożono w etapie 3 i potwierdzono testami.
- [x] **E1.6** Dodać walidację treści dla krótkich zgłoszeń: odrzucenie tekstu pustego i samych białych znaków oraz ustalenie limitu długości zgodnego z wejściem modelu `all-MiniLM-L6-v2`. Sprawdzić długość za pomocą jego tokenizera i zwracać czytelny błąd dla zbyt długiego tekstu; nie polegać na cichym obcinaniu przez model.
- [x] **E1.7** Dodać paginację listy, stabilne sortowanie oraz filtry kategorii i priorytetu obok istniejącego filtra statusu.
- [x] **E1.8** Przygotować konfigurację testów z oddzielną bazą PostgreSQL/pgvector. Testy nie mogą modyfikować danych używanych do demonstracji lub eksperymentów.
- [x] **E1.9** Dodać testy tworzenia, pobierania, filtrowania, paginacji i przejść statusów, w tym przypadki 404, niepoprawne dane i odmowę zmiany statusu oraz ponownego otwarcia zgłoszenia Rozwiązany, Odrzucony lub Anulowany. Po dodaniu autoryzacji potwierdzić tę odmowę dla wszystkich ról, również administratora. Sprawdzić zachowanie historii i możliwość utworzenia nowego zgłoszenia dotyczącego powracającego problemu. **Wykonane:** uzupełniono wszystkie 3 statusy końcowe × 6 statusów docelowych × zgłaszający/aktualna obsługa/inna obsługa/administrator, dla PATCH i DELETE, z zachowaniem danych i historii.

### Kryteria ukończenia

- Można utworzyć zgłoszenie, znaleźć je na liście, pobrać szczegóły i zmienić status.
- Niepoprawne dane oraz niedozwolone przejścia statusów dają przewidywalne odpowiedzi.
- Baza może zostać utworzona od zera przez migracje, a testy podstawowego przepływu przechodzą.

**Obszary kodu:** `app/api/main.py`, `app/models/`, `app/database/`, `app/alembic/`, `scripts/seed_db.py`, konfiguracja środowiska i nowy katalog testów.

## Etap 2. Zamiana Celery na FastAPI BackgroundTasks

**Stan początkowy:** zgłoszenie jest zapisywane w bazie, a klasyfikację uruchamia zadanie Celery. Status zadania pochodzi z Redis i nie jest sprawdzany pod kątem związku ze zgłoszeniem.

**Cel:** uruchamiać klasyfikację po wysłaniu odpowiedzi HTTP i zachować możliwość sprawdzania jej wyniku.

**Stan aktualny (2026-10-25):** E2.1–E2.12 ukończone. Użytkownicy, własność, role i przypisania z etapu 3 usunęły dawne blokady E2.8–E2.9. Podstawowy mechanizm korekty kategorii z E5.13 oraz testy obu porządków zakończenia klasyfikacji i korekty domknęły E2.5. Integracja z zatwierdzaniem referencji pozostaje osobnym zadaniem E5.12–E5.13.

**Decyzje i kontrakt etapu 2 (stan historyczny, 2026-10-11):** zachowano `POST /tickets/` → 201 (`ticket`, UUID `task_id`) oraz adres `GET /tickets/{id}/task/{task_id}`. Stan pochodzi wyłącznie z PostgreSQL: pending/running/succeeded/failed, wersja, aktualność, daty, wynik bez wektora i bezpieczny błąd. Niezgodna para zadanie–zgłoszenie daje 404. Dodano `POST /tickets/{id}/classification/retry` → 202 i `PATCH /tickets/{id}` dla opisu/checkboxa wyłącznie w reported. Zmiana tekstu zwiększa wersję i zastępuje zadanie; sam checkbox nie tworzy embeddingu. Ręczny priorytet ma pierwszeństwo przed checkboxem, potem automatyczny i zastępczy medium; pole ręcznej decyzji jest chronione przed wejściem formularza, a endpoint i historia decyzji pozostają E5.9.

**Uruchomienie i restart:** jeden proces API bez workers/reload, semafor jednej klasyfikacji, ładowanie i wykonanie modelu w wątku z blokadą. Sesyjna blokada PostgreSQL na dedykowanym połączeniu nie pozwala wystartować drugiemu API dla tej samej bazy. Dopiero po uzyskaniu blokady startup oznacza osierocone pending/running jako failed/interrupted. Brak automatycznego ponawiania; BackgroundTasks i zapis rekordu nie stanowią trwałej kolejki. Wynik i succeeded są atomowe; stare wyniki oraz wyniki zakończonych spraw są odrzucane. Nieaktualne embeddingi nie uczestniczą w prototypowych zapytaniach KNN/eskalacji/duplikatów; docelowy algorytm pozostaje etapem 5.

**Migracja i zachowanie danych:** `e2a000000001` dodaje zadania, work_blocked=false, content_version=1, embedding_version oraz oddzielne źródła priorytetu. Zachowano wszystkie dawne pola 10 demonstracyjnych zgłoszeń, w tym daty i wektory (zgodna suma SHA256 przed/po). Nie dopisano autorów, fikcyjnych zadań ani przewidywań bazowych; stare priorytety mają źródło legacy. Wcześniejsze zmiany użytkownika zachowano.

**Weryfikacja:** 26 testów unittest przeszło lokalnie i w nowym obrazie Docker na oddzielnym PostgreSQL/pgvector. Zakres: dotychczasowe API/migracje oraz zapis pending przed wykonaniem i rollback tworzenia, sukces, bezpieczny błąd modelu, rollback nieudanego zapisu wyniku, równoległe ponowienia, odmowy ponowienia sukcesu/trwającego/końcowego zadania, powiązanie zadanie–zgłoszenie, edycja podczas running i odrzucenie starego wyniku, checkbox bez embeddingu, zachowanie ręcznej decyzji także podczas obliczeń, walidacja edycji, wyścig przyjęcie–edycja, pomijanie nieaktualnych wektorów, brak blokowania żądań i jedna równoległa klasyfikacja. Test prawdziwego procesu Uvicorn odbiera odpowiedź HTTP podczas powolnego embeddingu, zabija proces, uruchamia go ponownie, sprawdza failed/interrupted i jawne ponowienie do succeeded. Test drugiego procesu potwierdza odmowę startu bez naruszenia aktywnych zadań pierwszego. Osobno dwa kolejne zadania z rzeczywistym MiniLM osiągnęły succeeded i aktualne embeddingi 384. Zbudowane API działa w Compose bez dawnych usług; sprawdzono 200/404/422 i zachowanie 10 rekordów. Jakość KNN, uprawnienia ról i ręczna korekta kategorii nie są objęte wynikiem tych testów.

**Przypomnienie odnotowane:** formalny opis pracy wymaga ujednolicenia z wdrożonym BackgroundTasks i ograniczeniami jednego procesu. Wczesna próba LLM z E8.1 nie jest wymagana do tej migracji; wybór sprzętu/dostawcy pozostaje otwarty i nie został przyjęty przy okazji etapu 2.

### Przypomnienie dla asystenta

- Przy E2.10 przedstawić prosty wariant uruchomienia z jednym procesem API i ograniczoną równoległością obliczeń. Zapytać o środowisko lub wymagania skali tylko wtedy, gdy dostępne informacje nie pozwalają ocenić, czy ten wariant wystarczy. Nie rozbudowywać mechanizmu do własnej kolejki rozproszonej.
- Nie pytać ponownie o ręczne ponawianie ani zastąpienie Celery. Sposób wykrywania przerwanych zadań dobrać do rzeczywiście wspieranego uruchomienia i sprawdzić restartem.

### Zadania

- [x] **E2.1** Ustalić kontrakt tworzenia zgłoszenia i odpytywania o klasyfikację: identyfikator zadania, dostępne stany, wynik i bezpieczny komunikat błędu. Rozstrzygnąć zachowanie dotychczasowego adresu `/tickets/{ticket_id}/task/{task_id}`.
- [x] **E2.2** Dodać model zadania klasyfikacji i migrację: identyfikator, powiązanie ze zgłoszeniem, wersja przetwarzanej treści, stan, znaczniki czasu i informacja o błędzie. Stan zadania oddzielić od biznesowego statusu zgłoszenia.
- [x] **E2.3** Dodać do modelu zgłoszenia i kontraktu API pole logiczne odpowiadające checkboxowi „Nie mogę kontynuować pracy”, z migracją dla istniejących danych. Zapisywać zgłoszenie, wartość pola i rekord oczekującego zadania w jednej transakcji; przy zaznaczeniu i braku ręcznej decyzji administratora od razu ustawić priorytet końcowy `critical`. Po zatwierdzeniu dodawać wykonanie przez `BackgroundTasks.add_task`.
- [x] **E2.4** Przenieść logikę wykonania z `app/celery_app.py` do serwisu przetwarzania. Zadanie ma otrzymywać identyfikatory i otwierać własną sesję bazy, niezależną od sesji żądania HTTP.
- [x] **E2.5** Zapewnić przejścia pending → running → succeeded albo failed, atomowy zapis wyniku i stanu zadania oraz pierwszeństwo ręcznego priorytetu przed checkboxem i wynikiem automatycznym. **Wykonane:** przewidywanie kategorii i jego wersja są zapisywane osobno od ręcznej korekty z autorem, czasem i wersją treści. Zadanie dla tej samej wersji nie nadpisuje korekty, ale wynik zadania zachowuje rzeczywiste przewidywanie KNN. Sprawdzono oba porządki zapisu, wynik unknown, ponowienie błędu, unieważnienie korekty po zmianie opisu i zachowanie przy checkboxie. Endpoint administratora do priorytetu zapisuje autora i czas; zatwierdzanie etykiet do referencji pozostaje osobnym E5.12.
- [x] **E2.6** Przenieść ładowanie modelu i obliczanie embeddingów poza pętlę obsługującą żądania. Ustalić ograniczenie równoległych obliczeń i bezpieczne współdzielenie modelu.
- [x] **E2.7** Zaimplementować odczyt statusu z PostgreSQL; sprawdzać zgodność identyfikatora zadania i zgłoszenia. Nieistniejące zadanie ma dawać 404.
- [x] **E2.8** Dodać możliwość ręcznego ponowienia nieudanej lub przerwanej klasyfikacji aktualnej wersji opisu. Uprawnienia egzekwować zgodnie z etapem 3: autor własnego nieprzypisanego zgłoszenia w statusie Zgłoszony, bieżący wykonawca w statusach Przyjęty i W trakcie oraz administrator dla każdego aktywnego zgłoszenia. Odmówić ponowienia dla statusów końcowych, trwającego zadania, nieuprawnionej osoby i poprawnie zakończonej klasyfikacji, także z wynikiem Do weryfikacji. Zabezpieczyć przed równoległym uruchomieniem dwóch zadań dla tej samej wersji zgłoszenia i zapisem wyniku zadania dotyczącego starszej treści. Sprawdzić utratę uprawnienia przez autora po przypisaniu i poprzedniego wykonawcę po zmianie opiekuna, nie zmieniać statusu sprawy ani ręcznego priorytetu administratora. **Wykonane:** role i aktualne przypisanie są egzekwowane; test pełnego błędu i ponowienia dla wszystkich aktywnych statusów potwierdza zachowanie ręcznego priorytetu, autora i czasu decyzji oraz statusu obsługi.
- [x] **E2.9** Dodać edycję opisu i checkboxa własnego zgłoszenia przez zgłaszającego wyłącznie w statusie Zgłoszony. Zmiana opisu zwiększa wersję treści i uruchamia nową klasyfikację; poprzedni wynik oznaczyć jako nieaktualny. Zmiana samego checkboxa przelicza priorytet końcowy bez regenerowania embeddingu i bez nadpisania decyzji administratora. W etapie 3 egzekwować własność i rolę oraz niezmienność pierwotnego opisu po przyjęciu dla wszystkich ról, także administratora. Sprawdzić równoczesną edycję oraz przyjęcie przez obsługę, aby zapis nie ominął blokady po zmianie statusu. Opis rozwiązania zapisywać w osobnym polu. **Wykonane:** role i własność są egzekwowane; deterministyczny test sprawdza oba porządki blokowania między edycją zgłaszającego a przyjęciem przez innego użytkownika obsługi, z zachowaniem autora, wersji i niezmienności po przyjęciu.
- [x] **E2.10** Ustalić wspierany sposób uruchamiania API oraz obsługę restartu: rozpoznawanie osieroconych zadań `pending`/`running` i jawne ponowienie. Nie oznaczać aktywnych zadań innego procesu jako przerwanych. Udokumentować, że zapis zadania w bazie nie zapewnia samodzielnie jego wykonania.
- [x] **E2.11** Usunąć moduł Celery, importy, zależności i wymóg `CELERY_BROKER_URL`. Usunąć Redis, worker i Flower z Compose; zaktualizować przykładową konfigurację i instrukcję uruchomienia.
- [x] **E2.12** Sprawdzić sukces, błąd modelu, błąd zapisu, ponowienie, edycję podczas klasyfikacji i przerwanie procesu. Sprawdzić obsługę innych żądań podczas generowania embeddingu oraz działanie na kilku kolejnych zgłoszeniach.

### Kryteria ukończenia

- System uruchamia się bez Celery, Redis i Flower.
- Utworzenie zgłoszenia zwraca odpowiedź przed ukończeniem klasyfikacji; przetwarzanie i jego wynik można obserwować przez API.
- Niepowodzenie jest zapisane w bazie i możliwe do ponowienia, a wynik starszej treści nie nadpisuje nowszego.
- Zachowanie po restarcie jest przetestowane i opisane; nie zakładamy trwałej kolejki ani automatycznych ponowień dostarczanych przez `BackgroundTasks`.

**Obszary kodu:** API, nowy serwis zadań, modele i migracje, `app/services/classifier.py`, `app/settings.py`, `requirements.txt`, `docker-compose.yml`.

## Etap 3. Użytkownicy, uwierzytelnianie i autoryzacja

**Stan początkowy:** brak kont użytkowników, tokenów i ograniczeń dostępu.

**Cel:** ustalić, kto może wykonywać operacje i jakie dane może zobaczyć, zanim powstaną wyszukiwanie i RAG.

**Stan po implementacji (2026-10-25):** wykonano backend E3.1–E3.13. Dodano użytkowników, Argon2id, OAuth2/Bearer JWT (30 minut), rejestrację wyłącznie w skonfigurowanej domenie, atomową akceptację z obowiązkowym wyborem roli, zarządzanie rolą i aktywnością, wspólne filtrowanie dostępnych zgłoszeń, autorów decyzji, przypisania i ich historię. Każde chronione żądanie ponownie odczytuje aktualną rolę i stan konta z bazy. Autor może tworzyć, edytować i anulować własne zgłoszenia zgodnie z ograniczeniami także wtedy, gdy jego konto ma rolę obsługi lub administratora. Administrator przypisuje aktywne konto obsługi przez osobny endpoint; samodzielne przyjęcie przez PATCH statusu jest operacją obsługi.

**Dawne dane:** migracja e3a000000001 zachowuje wszystkie dawne pola i jawnie oznacza rekordy bez autora jako legacy_unowned. Są dostępne wyłącznie obsłudze i administratorowi. Skrypt scripts/import_ticket_authors.py wykonuje atomowy import jawnego mapowania identyfikator → e-mail istniejącego zaakceptowanego konta, bez nadpisywania autora. Nie przypisano fikcyjnych autorów ani historycznych decyzji. Nowe API wymaga autora wynikającego z tokenu; seed domyślnie uzupełnia referencje, a utworzenie zgłoszeń demonstracyjnych wymaga --author-email.

**Granice etapu:** przygotowano dependency dostępu do przyszłego LLM. W późniejszym domknięciu E2.5 wdrożono podstawową korektę kategorii z E5.13. Zatwierdzanie referencji, pełna integracja korekt z tym zatwierdzaniem i eskalacja pozostają w etapie 5. Podstawowy endpoint priorytetu administratora ma autora i czas decyzji; nie oznacza to ukończenia całego E5.9 z przyszłą eskalacją. Frontend użyje Bearer JWT w pamięci, bez refresh tokenów.

### Przypomnienie dla asystenta

Rejestracja, domena, akceptacja z wyborem roli, pierwszy administrator i macierz uprawnień są ustalone. Nie rozpoczynać kolejnej rundy pytań o te zasady. Sposób obsługi JWT uzgodnić technicznie z frontendem; pytać użytkownika dopiero, jeśli proponowany wariant wymaga nowej funkcji lub zmienia oczekiwane zachowanie logowania.

### Zadania

- [x] **E3.1** Wdrożyć ustaloną macierz ról: zgłaszający widzi własne zgłoszenia, dodaje je, edytuje opis i checkbox tylko w statusie Zgłoszony oraz sam anuluje własne nieprzypisane zgłoszenie w tym statusie; po przypisaniu wykonawcy anulowanie jest całkowicie zablokowane. Obsługa i administrator widzą wszystkie zgłoszenia i korzystają z LLM. Odrzucenie w statusie Zgłoszony przysługuje obsłudze i administratorowi, a w statusach Przyjęty i W trakcie wyłącznie administratorowi. Obsługa samodzielnie przyjmuje nowe zgłoszenie, a administrator może przypisać i zmienić wykonawcę. Rozpocząć realizację i oznaczyć sprawę jako Rozwiązany mogą wyłącznie aktualny wykonawca oraz administrator. Po przyjęciu żadna rola nie może zmieniać pierwotnego opisu; rozwiązanie zapisuje się osobno. Zgłaszający nie może korzystać z czatu ani nadawać statusu Odrzucony. Korektę kategorii realizować zgodnie z E5.13. Egzekwować przyjętą macierz przejść, blokadę cofania statusu oraz ustalone uprawnienia do ponowienia zgodnie z E2.8.
- [x] **E3.2** Dodać model użytkownika i migrację: identyfikator, unikalny adres e-mail używany do logowania, hash hasła, opcjonalna rola przed akceptacją, stan akceptacji, aktywność i znaczniki czasu. Konto oczekujące ma pozostawać bez roli, a konto zaakceptowane musi mieć jedną z trzech ustalonych ról. Odróżnić oczekiwanie na zatwierdzenie od dezaktywacji wcześniej zaakceptowanego konta; zapisywać administratora i czas akceptacji.
- [x] **E3.3** Dodać autora i opcjonalnego opiekuna zgłoszenia. Przygotować migrację lub kontrolowany import dla istniejących rekordów bez autora.
- [x] **E3.4** Dodać samodzielną rejestrację e-mailem i własnym hasłem oraz hashowanie i weryfikację haseł. Walidować adres, unikalność i dokładną zgodność jego domeny z konfiguracją, początkowo `mail.com`; nie akceptować innej domeny przez samo częściowe dopasowanie nazwy. Nowe konto ma oczekiwać na zatwierdzenie i nie może samodzielnie wybrać uprzywilejowanej roli. Zaimplementować logowanie adresem e-mail w ramach OAuth2, wydawanie JWT wyłącznie zaakceptowanym aktywnym kontom oraz odczyt bieżącego użytkownika. Ustalić czas ważności tokenu i sposób jego używania przez frontend. Sprawdzić rejestrację z dozwoloną i niedozwoloną domeną, niepoprawny adres, powtórzony e-mail i próbę nadania sobie roli przez żądanie API.
- [x] **E3.5** Utworzyć endpoint bieżącego użytkownika, obsłużyć tokeny niepoprawne i wygasłe oraz zablokować dostęp kont niezaakceptowanych i nieaktywnych. Rola, stan akceptacji i aktywność w bazie mają być respektowane po zmianie konta. Sprawdzić odmowę logowania i brak dostępu do chronionych funkcji przed akceptacją, poprawne logowanie po akceptacji oraz odmowę dostępu po dezaktywacji także przy wcześniej wydanym tokenie.
- [x] **E3.6** Zastosować macierz uprawnień do wszystkich operacji na zgłoszeniach i zadaniach. Autor ma wynikać z zalogowanego użytkownika; klient nie może podszyć się pod innego zgłaszającego przez przesłanie identyfikatora autora. Uwzględnić uprawnienie administratora do ręcznej zmiany priorytetu.
- [x] **E3.7** Dodać backend administracji: lista kont z filtrem oczekujących na akceptację, zatwierdzanie rejestracji z obowiązkowym wyborem roli, późniejsza zmiana roli, aktywacja/dezaktywacja oraz przypisywanie i zmiana osoby obsługującej zgłoszenie. Akceptację udostępnić wyłącznie administratorowi; nadanie wybranej roli, zatwierdzenie konta oraz zapis autora i czasu decyzji wykonać w jednej transakcji. Sprawdzić brak roli, wartość spoza słownika i żądanie nieuprawnionego użytkownika; błąd nie może pozostawić zaakceptowanego konta bez roli. Sprawdzić równoległe próby akceptacji z różnymi rolami, aby druga decyzja nie nadpisała pierwszej; późniejsza zmiana roli pozostaje osobną operacją. Dodać jednorazową komendę konfiguracji tworzącą pierwsze konto administratora z podanym e-mailem i hasłem, od razu aktywne i zatwierdzone. Hasło pobierać bez wyświetlania, przechowywać jako hash i nie zapisywać w kodzie ani logach. Nie nadpisywać istniejących kont ani nie zmieniać ich ról; odmówić ponownego tworzenia pierwszego administratora, gdy takie konto już istnieje. Udokumentować użycie komendy podczas konfiguracji i sprawdzić jej poprawne wykonanie oraz odmowę przy konflikcie konta. Kolejne konta przechodzą zwykłą rejestrację i akceptację. Resetowanie zapomnianego hasła pozostaje poza zakresem backendu.
- [x] **E3.8** Wyodrębnić wspólne reguły filtrowania dostępnych zgłoszeń, które będą używane również przez duplikaty, wyszukiwanie i RAG.
- [x] **E3.9** Przetestować dozwolone i zabronione operacje każdej roli, w tym odczyt cudzego zgłoszenia przez bezpośredni identyfikator, statusu cudzego zadania, wywołanie LLM przez zgłaszającego, anulowanie cudzego lub przypisanego zgłoszenia i próbę nadania statusu Odrzucony przez zgłaszającego. Sprawdzić odmowę edycji pierwotnego opisu po przyjęciu dla każdej roli, również administratora, oraz zachowanie osobnego opisu rozwiązania.
- [x] **E3.10** Dodać samodzielne anulowanie własnego zgłoszenia przez zgłaszającego: w jednej transakcji zweryfikować autora, status Zgłoszony i brak wykonawcy, następnie nadać status Anulowany i zapisać autora oraz czas zmiany. Po przypisaniu odmówić anulowania; nie implementować próśb ani ich zatwierdzania. Zabezpieczyć anulowanie równoległe do przyjęcia przez obsługę, przypisania przez administratora i odrzucenia zgłoszenia. Sprawdzić, że spóźnione zadanie klasyfikacji nie przywraca aktywnego statusu, a anulowana sprawa pozostaje w historii i nie może zostać przyjęta do realizacji.
- [x] **E3.11** Dodać przyjęcie nowego zgłoszenia przez osobę obsługującą oraz przypisanie i zmianę wykonawcy przez administratora. Opiekunem może być aktywne konto z rolą osoby obsługującej. Przyjęcie zapisuje opiekuna i status Przyjęty w jednej transakcji; równoległa próba przyjęcia nie może nadpisać pierwszego przypisania. Zmiana wykonawcy zachowuje bieżący status oraz historię poprzedniego i nowego opiekuna, autora decyzji i czas. Sprawdzić, że ponowne przypisanie w statusach Przyjęty i W trakcie nie zmienia statusu ani nie uruchamia KNN. Sprawdzić odmowę zmiany wykonawcy przez nieuprawnione role oraz brak zmiany pierwotnego zgłaszającego.
- [x] **E3.12** Ograniczyć rozpoczęcie i zakończenie realizacji do aktualnie przypisanego wykonawcy oraz administratora. Egzekwować kolejność Przyjęty → W trakcie → Rozwiązany: rozpoczęcie tylko ze statusu Przyjęty, rozwiązanie tylko ze statusu W trakcie. Zablokować cofanie statusu dla wszystkich ról, również W trakcie → Przyjęty, i sprawdzić odmowę także dla administratora. Dodać pole opisu rozwiązania z autorem i czasem zapisu; wymagać krótkiej, niepustej notatki przy przejściu na Rozwiązany i zapisywać ją ze statusem w jednej transakcji. Sprawdzić odmowę przy braku opisu, tekście z samych białych znaków, próbie pominięcia W trakcie także przez administratora oraz żądaniu zgłaszającego, nieprzypisanego pracownika obsługi lub poprzedniego wykonawcy po zmianie przypisania. Zachować niezależne uprawnienie do podglądu wszystkich zgłoszeń dla obsługi. W E6.7 udostępnić rozpoczęcie tylko dla Przyjęty, a rozwiązanie tylko dla W trakcie; backend ma odrzucać niedozwolone przejścia także przy bezpośrednim żądaniu API.
- [x] **E3.13** Dodać odrzucanie zgłoszeń: Zgłoszony → Odrzucony dla obsługi i administratora, Przyjęty → Odrzucony oraz W trakcie → Odrzucony wyłącznie dla administratora. Dodać osobne pole krótkiego powodu odrzucenia i wymagać niepustej wartości; zapisywać powód, autora, czas i status w jednej transakcji. Udostępnić powód w szczegółach zgłoszenia z zachowaniem reguł widoczności, także jego zgłaszającemu. Sprawdzić odmowę przy braku powodu lub samych białych znakach bez częściowej zmiany statusu, odmowę dla zgłaszającego oraz odmowę odrzucenia przyjętej lub rozpoczętej sprawy przez obsługę, także aktualnego wykonawcę. Zabezpieczyć odrzucenie równoległe do przyjęcia, anulowania lub rozwiązania i respektować brak przejść ze statusu Rozwiązany. Odrzucenie nie uruchamia KNN i wyklucza sprawę z aktywnych duplikatów oraz eskalacji.

### Kryteria ukończenia

- Każda chroniona operacja wymaga poprawnego uwierzytelnienia i sprawdzenia uprawnień.
- Administrator może zarządzać kontami przez API, a autor i opiekun są zapisani przy zgłoszeniu.
- Testy potwierdzają brak dostępu do danych spoza przyjętej macierzy uprawnień.

## Etap 4. Dane referencyjne i projekt ewaluacji

**Pilotaż (2026-10-28):** wykonano pierwszą część E4.1–E4.3 i walidację
formatu próbki z E4.10: 40 propozycji, instrukcja etykietowania i pochodzenie,
stan przeglądu autora oraz odtwarzalny skrypt `backend/scripts/evaluate_pilot.py`.
Diagnostyka k=3 bez całej grupy parafraz: accuracy kategorii 60% i priorytetu
bazowego 37,5% (stałe medium: 40%). Raport JSON/Markdown zapisuje snapshot
modelu, hashe danych i skryptu, wersje bibliotek, sąsiadów i pomyłki.
Wszystkie rekordy pozostają pending; etykiet nie przedstawiamy jako wzorcowych.
Żadnego pełnego zadania etapu 4 nie zaznaczono jako ukończonego: pozostaje
ręczny przegląd, docelowy zbiór 300, podział danych i pytania RAG.

**Stan początkowy:** jest 10 przykładowych zgłoszeń w języku angielskim. Brak wydzielonych zbiorów i scenariuszy badawczych.

**Cel:** przygotować dane i protokół badań przed doborem parametrów.

### Przypomnienie dla asystenta

- Przed przygotowaniem całego zbioru pokazać małą próbkę zgłoszeń, w tym przypadki graniczne kategorii i priorytetów. Zapytać o niejednoznaczności, które wpływają na instrukcję etykietowania. Liczebność 300, cztery kategorie, wsparcie LLM i samodzielna weryfikacja przez autora są już przyjęte.
- Przed zamrożeniem danych przedstawić konkretny podział referencja/walidacja/test oraz podział 30 pytań RAG na walidację i test. Zachować grupy parafraz i jednego incydentu w jednej części; oddzielić protokół klasyfikacji od par duplikatów i pytań RAG.
- Przy E4.8–E4.9 pokazać prostą rubrykę oceny odpowiedzi i zapytać, czy autor samodzielnie oceni również odpowiedzi RAG. Samodzielna weryfikacja etykiet danych nie rozstrzyga automatycznie sposobu oceny odpowiedzi asystenta.

### Zadania

- [ ] **E4.1** Przygotować własny polski zbiór zgłoszeń helpdesku IT ze wsparciem LLM i ręczną weryfikacją przykładów: przyjąć wstępnie 300 zgłoszeń, około 75 na każdą z czterech kategorii, oraz zaplanować rozkład priorytetów i realistyczne scenariusze problemów informatycznych. Sprawdzić jakość obowiązkowego modelu `all-MiniLM-L6-v2` na niewielkiej próbce polskich tekstów przed przygotowaniem całego zbioru i docelowej konfiguracji; udokumentować ograniczenia językowe.
- [ ] **E4.2** Doprecyzować wstępnie przyjęte kategorie: Konta i uprawnienia, Sprzęt, Sieć i łączność, Oprogramowanie. Przygotować instrukcję etykietowania zgodną z przyjętymi znaczeniami priorytetów Niski, Średni, Wysoki i Krytyczny, z przykładami przypadków granicznych oraz postępowaniem przy niewystarczającej informacji o wpływie problemu. Kategorię przypisywać według opisanego problemu, bez wymagania znajomości jego przyczyny technicznej; ustalić rozstrzyganie zgłoszeń pasujących do kilku kategorii. Uporządkować sposób zastąpienia obecnych kategorii `bug`, `performance`, `feature` w danych i konfiguracji.
- [ ] **E4.3** Przygotować samodzielnie zgłoszenia z etykietami zgodnie z instrukcją etykietowania, z dopuszczonym wsparciem LLM. Ręcznie sprawdzić treść, kategorię i priorytet bazowy każdego przykładu przed dopuszczeniem do danych referencyjnych, walidacyjnych lub testowych; zapisać wynik weryfikacji i ewentualne korekty względem propozycji generatora. Udokumentować pochodzenie każdego przykładu i sposób przygotowania: ręczny lub wspomagany LLM. Weryfikację wykonuje samodzielnie autor pracy; nie planujemy drugiego oceniającego. Przypadki niejednoznaczne rozstrzygać zgodnie z instrukcją etykietowania, zapisując uzasadnienie lub wykluczając przykład, jeśli informacji nie wystarcza. Brak niezależnego drugiego oceniającego opisać jako ograniczenie badania; nie przedstawiać przygotowanych danych jako rzeczywistych zgłoszeń organizacji. Przy wykorzystaniu generatora zapisać jego model, ustawienia i instrukcje tworzenia danych. Usunąć ewentualne dane osobowe i sekrety z materiału badawczego oraz opisać ograniczenia samodzielnie przygotowanego zbioru w ewaluacji.
- [ ] **E4.4** Rozdzielić dane na referencyjne, walidacyjne i testowe; utrwalić podział oraz ziarno losowania. Duplikaty i bliskie parafrazy tego samego przypadku nie mogą trafić do różnych części.
- [ ] **E4.5** Przygotować pary lub grupy duplikatów oraz podobnych, ale odrębnych zgłoszeń, umożliwiające pomiar fałszywych alarmów.
- [ ] **E4.6** Przygotować osobne scenariusze reguły checkboxa i eskalacji z kontrolowaną liczbą aktywnych zgłoszeń oraz różnych zgłaszających. Uwzględnić scenariusze eskalacji w każdej z czterech kategorii: Konta i uprawnienia, Sprzęt, Sieć i łączność oraz Oprogramowanie. Uwzględnić podobne zgłoszenia od wielu osób, wielokrotne zgłoszenia jednej osoby, podobne treści opisujące odrębne awarie, sprawy zakończone, granice okna czasowego i progu liczby użytkowników oraz ręczny priorytet administratora. Uwzględnić przypadek, w którym KNN przewiduje niższy priorytet, ale zaznaczenie „Nie mogę kontynuować pracy” nadaje `critical`. Rozdzielić jakość przewidywania priorytetu bazowego i poprawność zastosowania reguł biznesowych w ocenie.
- [ ] **E4.7** Przygotować ręcznie oznaczony zbiór startowy KNN i kontrolowane rozszerzanie go o rozwiązane zgłoszenia z osobno zatwierdzonymi etykietami. Zgłoszenia aktywne, odrzucone i anulowane nie trafiają do referencji operacyjnej. Automatyczne przewidywanie, przyjęcie do realizacji i priorytet końcowy nadany regułą nie zatwierdzają etykiety wzorcowej. Zatwierdzenie kategorii i priorytetu bazowego udostępnić aktualnie przypisanemu wykonawcy oraz administratorowi. Ustalić dostęp do referencji i zakres informacji ujawnianych użytkownikowi.
- [ ] **E4.8** Przygotować wstępnie 30 pytań do RAG, rozdzielonych na część walidacyjną i testową, z oczekiwanymi źródłami, kluczowymi faktami oraz przypadkami bez odpowiedzi i bez dostępu do źródeł. Uwzględnić opis nowego problemu wymagający wyszukania podobnych rozwiązanych spraw i streszczenia ich rozwiązań; w zbiorze kontekstu zapewnić ręcznie sprawdzone opisy rozwiązań. Dodać przypadki kilku odmiennych sposobów rozwiązania oraz braku rozwiązanych spraw mimo istnienia podobnych aktywnych zgłoszeń. Dla pytań o pełne zestawienia i liczby oczekiwać informacji o zakresie asystenta, a nie liczby wywnioskowanej z ograniczonego kontekstu. Te same pytania i oczekiwane źródła wykorzystać w porównaniu wyszukiwania wektorowego i pełnotekstowego.
- [ ] **E4.9** Zdefiniować metryki: accuracy i macro-F1 osobno dla kategorii i priorytetu, macierze pomyłek, precision/recall duplikatów, trafność wyszukiwania oraz ocenę poprawności i oparcia odpowiedzi na źródłach.
- [ ] **E4.10** Dodać walidację formatu danych, kontrolę duplikujących się identyfikatorów i skrypty importu umożliwiające odtworzenie zbioru.

### Kryteria ukończenia

- Każdy zbiór ma opis, wersję, przeznaczenie i ustalony sposób importu.
- Parametry można dobierać na walidacji bez zaglądania do testu końcowego.
- Pytania RAG, oczekiwane źródła i sposób oceny są przygotowane przed strojeniem asystenta.

## Etap 5. Dopracowanie klasyfikatora i duplikatów

**Stan początkowy:** działa prototyp KNN z `k=3`, głosowaniem większościowym i regułami eskalacji. Jest funkcja wyszukiwania potencjalnych duplikatów.

**Cel:** uzyskać kontrolowaną klasyfikację i użyteczne sugestie podobnych zgłoszeń.

### Przypomnienie dla asystenta

- Przed E5.6 pokazać przykłady wspólnej awarii i odrębnych problemów o podobnym opisie. Uzgodnić regułę grupowania, w tym możliwość łączenia zgłoszeń z różnymi kategoriami. Dopuszczenie eskalacji we wszystkich czterech kategoriach jest ustalone; nie oznacza automatycznie wspólnej grupy ponad granicami kategorii.
- Przed udostępnieniem sugestii zapytać, czy zgłaszający ma widzieć podobne własne zgłoszenia, czy sugestie mają być przeznaczone wyłącznie dla obsługi i administratora. Ustalona widoczność tylko własnych zgłoszeń wyklucza ujawnianie mu treści i identyfikatorów cudzych spraw.
- Progi i k dobierać na walidacji; zachować przyjęte reguły pierwszeństwa priorytetu, trwałość eskalacji i oznaczenie Do weryfikacji.

### Zadania

- [ ] **E5.1** Uporządkować zapis embeddingów: model i jego wersja, wymiar wektora, powiązanie z wersją tekstu oraz regeneracja po zmianie treści. Dla krótkich zgłoszeń stosować jeden embedding na zgłoszenie i sprawdzić, czy walidacja długości zapobiega obcięciu treści przez model.
- [ ] **E5.2** Ograniczyć KNN do ustalonego zbioru referencyjnego. Wykluczyć bieżące zgłoszenie, brakujące wektory i etykiety `unknown`.
- [ ] **E5.3** Zdefiniować zachowanie przy pustym zbiorze, liczbie przykładów mniejszej od `k`, remisie głosów i zbyt słabym dopasowaniu. Przy słabym dopasowaniu nie wymuszać kategorii, lecz zapisać oznaczenie wyniku Do weryfikacji wraz z przyczyną i wersją tekstu. Oddzielić je od biznesowego statusu zgłoszenia i stanu zadania; poprawnie zakończone obliczenie wymagające weryfikacji nie ma stanu failed. Próg dopasowania dobrać na walidacji. Umożliwić ręczne uzupełnienie kategorii zgodnie z E5.13, zachowując przewidywanie KNN i oddzielne zatwierdzanie referencji. Przy niewiarygodnym przewidywaniu priorytetu bazowego używać tymczasowo Średniego, zapisując źródło wartości zastępczej i potrzebę weryfikacji osobno od przewidywania KNN. Sprawdzić Średni bez innych reguł, Wysoki po eskalacji, Krytyczny z checkboxem oraz zachowanie dowolnego ręcznego priorytetu administratora. Wartości zastępczej nie traktować jako zatwierdzonej etykiety referencyjnej ani poprawnego przewidywania KNN.
- [ ] **E5.4** Przenieść `k`, próg akceptacji, próg duplikatów i parametry eskalacji do jawnej konfiguracji. Rozróżnić podobieństwo kosinusowe od odległości; opisać kierunek porównań.
- [ ] **E5.5** Przygotować skrypt do porównania konfiguracji KNN na walidacji i zapisywania wyników. Dobrać parametry kategorii i priorytetu na podstawie metryk.
- [ ] **E5.6** Dostosować eskalację do helpdesku IT zamiast obecnego ograniczenia do `bug` i `performance`: przy podobnych aktywnych zgłoszeniach od co najmniej 3 różnych użytkowników, utworzonych w ostatnich 24 godzinach, podnosić priorytet automatyczny co najmniej do Wysokiego, bez obniżania Krytycznego. Aktualizować wszystkie podobne aktywne zgłoszenia z tego okna, także wcześniejsze, respektując osobno ich ręczne priorytety administratora. Liczyć unikalnych autorów, bez zwiększania liczebności przez wielokrotne zgłoszenia tej samej osoby. Liczbę użytkowników i długość okna przenieść do konfiguracji i sprawdzić na walidacji. Objąć regułą wszystkie cztery kategorie: Konta i uprawnienia, Sprzęt, Sieć i łączność oraz Oprogramowanie. Ustalić regułę grupowania podobnych spraw i sposób uwzględnienia bieżącego zgłoszenia. Sprawdzać warunki po udanej klasyfikacji nowego zgłoszenia, po ponownej klasyfikacji zmienionego opisu oraz po udanym ponowieniu zadania. Przed eskalacją sprawdzać aktualną wersję treści i bieżące aktywne statusy; wynik nieaktualnego zadania nie uruchamia eskalacji. Wykluczyć porównanie zgłoszenia z samym sobą i dobrać próg podobieństwa na walidacji. Zapisywać osobno priorytet bazowy KNN, minimum eskalacji Wysoki, czas i przyczynę zastosowania reguły. Nie cofać eskalacji po spadku liczby aktywnych spraw, upływie okna ani automatycznym przeliczeniu; obniżenie umożliwia wyłącznie nadrzędna decyzja administratora. Nie nadpisywać ręcznego priorytetu administratora, także niższego, ani obniżać priorytetu wymuszonego checkboxem. Sprawdzić przypadki małej bazy, podniesienie priorytetów wcześniejszych spraw, trwałość eskalacji po ustaniu warunków i restarcie oraz równoległą zmianę statusu lub priorytetu administratora. Odróżnić wspólną awarię od niezależnych problemów o podobnej treści. Eskalacja nie zmienia statusu ani nie scala zgłoszeń.
- [ ] **E5.7** Uruchamiać wykrywanie duplikatów po uzyskaniu embeddingu nowego lub edytowanego zgłoszenia. Ustalić, czy filtr tej samej kategorii poprawia wyniki, czy ukrywa duplikaty błędnie sklasyfikowane. Wynik ma charakter sugestii i nie powoduje automatycznego scalenia ani odrzucenia zgłoszenia.
- [ ] **E5.8** Udostępnić sugestie duplikatów z identyfikatorem, dostępną użytkownikowi treścią i podobieństwem; egzekwować uprawnienia do każdego wyniku. Ustalić sposób odczytu sugestii przez frontend i oznaczać wyniki jako potencjalne duplikaty wymagające oceny człowieka. Decyzja o odrzuceniu pozostaje osobną operacją z obowiązkowym powodem i kontrolą roli oraz statusu zgodnie z E3.13. Samo podobieństwo nie potwierdza, że zgłoszenia dotyczą tej samej awarii. Sprawdzić, że wykrycie duplikatu nie zmienia statusu i nie usuwa ani nie scala rekordów.
- [ ] **E5.9** Dodać endpoint ręcznej zmiany priorytetu przez administratora, np. `PATCH /tickets/{ticket_id}/priority`, z walidacją jednego z czterech poziomów i kontrolą uprawnień. Zapisać decyzję administratora osobno wraz z autorem i czasem zmiany; ma ona pierwszeństwo przed checkboxem, KNN i automatyczną eskalacją. Chronić ją przed nadpisaniem przez zadanie kończące się równolegle, ponowną klasyfikację oraz zmianę treści lub checkboxa. Oddzielić przewidywanie KNN, efekt reguł oraz zmianę administratora, aby umożliwić analizę błędów i kontrolowaną aktualizację danych referencyjnych. Ręczną korektę kategorii realizować oddzielnie zgodnie z zadaniem E5.13.
- [ ] **E5.10** Sprawdzić przypadki graniczne KNN, eskalacji i duplikatów oraz cały przepływ zadania w tle. Zapisać wybraną konfigurację i wyniki walidacyjne.
- [ ] **E5.11** Wdrożyć przyjętą macierz wpływu statusów: oddzielne filtry dla zatwierdzonych przykładów KNN, aktywnych duplikatów i eskalacji (Zgłoszony, Przyjęty, W trakcie) oraz historycznego kontekstu RAG. Sprawdzić, że zmiana statusu nie uruchamia KNN, zakończone zadanie nie zmienia biznesowego statusu sprawy, a rozwiązane, odrzucone i anulowane zgłoszenia przestają uczestniczyć w mechanizmach aktywnych awarii. Oddzielić zatwierdzenie przykładu referencyjnego od rozwiązania zgłoszenia i od ręcznej zmiany priorytetu końcowego.
- [ ] **E5.12** Dodać zatwierdzanie rozwiązanego zgłoszenia jako przykładu referencyjnego przez jego aktualnie przypisanego wykonawcę lub administratora. Zapisywać osobno zatwierdzoną kategorię, priorytet bazowy, wersję treści, autora i czas zatwierdzenia; sprawdzać aktualność embeddingu i poprawność etykiet. Nie nadpisywać priorytetu końcowego ani statusu sprawy. Zabezpieczyć przed wielokrotnym dodaniem tego samego przykładu i odmówić zatwierdzenia aktywnej, odrzuconej albo anulowanej sprawy oraz żądania nieuprawnionego użytkownika. Sprawdzić utratę uprawnienia przez poprzedniego wykonawcę po zmianie przypisania.
- [ ] **E5.13** Dodać endpoint ręcznej korekty kategorii, np. `PATCH /tickets/{ticket_id}/category`, dla aktualnego wykonawcy i administratora. Sprawdzać przynależność kategorii do słownika oraz zapisywać korektę, autora, czas i wersję treści osobno od przewidywania KNN. Zabezpieczyć korektę przed przypadkowym nadpisaniem przez zadanie dla tej samej wersji tekstu. Korekta nie zatwierdza referencji ani nie zmienia statusu i ręcznie ustalonego priorytetu. Sprawdzić odmowę dla zgłaszającego, nieprzypisanej obsługi i poprzedniego wykonawcy oraz zachowanie przy późniejszej edycji treści i wcześniej zatwierdzonym przykładzie referencyjnym. **Częściowo wykonane przy domknięciu E2.5 (2026-10-25):** endpoint, uprawnienia, przewidywanie KNN, wersjonowana korekta i jej autor/czas, ochrona przed zadaniem, testy ponowień i edycji oraz niezależność od istniejącej referencji są gotowe. Obecny słownik prototypu to bug/performance/feature; nie mapujemy go automatycznie na helpdesk. Pozostają docelowy słownik z etapu 4 i scenariusz korekty po osobnym zatwierdzeniu referencji z E5.12. Nie zaznaczamy całego zadania przed ich wykonaniem.

### Kryteria ukończenia

- Zgłoszenie jest klasyfikowane lub jawnie kierowane do weryfikacji zamiast otrzymywać wymuszoną etykietę przy słabym dopasowaniu.
- Sugestie duplikatów powstają dla nowego zgłoszenia i respektują widoczność danych; nie wywołują automatycznego scalania ani odrzucania.
- Wybór parametrów ma uzasadnienie w wynikach walidacyjnych, a ręczna korekta nie ginie bez uzasadnionej reguły przy ponownym przetwarzaniu.

## Etap 6. Podstawowa aplikacja React

**Stan początkowy:** brak frontendu.

**Cel:** umożliwić wykonanie podstawowego scenariusza bez korzystania bezpośrednio z dokumentacji API.

### Przypomnienie dla asystenta

Przygotować prosty widok listy, szczegółów i formularza na podstawie ustalonych ról. Zbierać uwagi do konkretnego działającego widoku; nie uzależniać implementacji od ankiety o kolorach i układzie. Wrócić tylko do nierozstrzygniętej prezentacji duplikatów z etapu 5, jeśli nadal pozostaje otwarta.

### Zadania

- [x] **E6.1** Utworzyć aplikację React, routing, konfigurację adresu API oraz wspólną obsługę żądań i błędów. Wszystkie etykiety, formularze, przyciski, prezentowane statusy i komunikaty dla użytkownika przygotować po polsku; zapewnić czytelne polskie komunikaty także dla błędów walidacji API. Dostosować CORS backendu do ustalonych adresów aplikacji.
- [x] **E6.2** Zbudować rejestrację e-mailem i własnym hasłem, logowanie adresem e-mail, wylogowanie i odczyt bieżącego użytkownika. W formularzu rejestracji wskazywać wymaganą domenę z konfiguracji i obsługiwać błędy walidacji backendu. Po rejestracji pokazać informację o oczekiwaniu na akceptację administratora bez automatycznego logowania; obsłużyć odmowę logowania konta niezaakceptowanego lub nieaktywnego. Zaimplementować ustalony sposób używania tokenu oraz obsługę wygaśnięcia sesji.
- [ ] **E6.3** Zbudować historię własnych zgłoszeń dla zgłaszającego oraz listę wszystkich zgłoszeń dla obsługi i administratora, z filtrami i paginacją. Osobno pokazywać status procesu, stan wykonania zadania i oznaczenie klasyfikacji Do weryfikacji; nie przedstawiać niepewnej kategorii jako zatwierdzonej. Obsłudze i administratorowi umożliwić filtrowanie spraw wymagających weryfikacji i przejście do uzupełnienia kategorii zgodnie z uprawnieniami. Anulowane sprawy zachowywać w historii z ich statusem.
- [x] **E6.4** Dodać formularz tworzenia zgłoszenia z opisem oraz checkboxem „Nie mogę kontynuować pracy”. Zgłaszający może edytować oba pola wyłącznie we własnym zgłoszeniu w statusie Zgłoszony; po przyjęciu pola są zablokowane. Przy braku ręcznej decyzji administratora zaznaczenie nadaje priorytet końcowy `critical`, a brak zaznaczenia pozostawia wyznaczenie priorytetu bazowego KNN. Autor jest automatycznie przypisywany przez backend na podstawie zalogowanego konta. Zapewnić walidację i prezentację błędów API, w tym przy przyjęciu zgłoszenia przez obsługę podczas otwartego formularza edycji. Przy ręcznie nadanym priorytecie pokazywać jego źródło i zachować decyzję administratora.
- [x] **E6.5** Dodać widok szczegółów: treść, autor, opiekun, status, kategoria, priorytet i sugestie duplikatów. Po przyjęciu wyświetlać pierwotny opis tylko do odczytu dla wszystkich ról; opis rozwiązania prezentować osobno. Przy odrzucaniu udostępnić uprawnionej roli formularz obowiązkowego krótkiego powodu i obsłużyć błędy walidacji API. Zapisany powód odrzucenia wyświetlać osobno w szczegółach, także zgłaszającemu, z autorem i czasem decyzji.
- [x] **E6.6** Dodać odpytywanie o zadanie z ograniczoną częstotliwością; zatrzymywać je po zakończeniu zadania lub opuszczeniu widoku. Obsłużyć błąd i przerwanie oraz przycisk ponowienia dla autora przed przypisaniem, aktualnego wykonawcy podczas obsługi i administratora dla aktywnych zgłoszeń. Nie wyświetlać ponowienia dla statusów końcowych, poprawnie zakończonego zadania ani samego oznaczenia Do weryfikacji. Obsłużyć odmowę API, gdy przypisanie lub status zmieniły się podczas otwartego widoku.
- [x] **E6.7** Udostępnić akcje zgodne z rolą: przycisk „Anuluj zgłoszenie” dla autora wyłącznie w statusie Zgłoszony bez wykonawcy, przycisk „Przyjmij zgłoszenie” dla obsługi oraz przypisanie i zmianę wykonawcy dla administratora. Po przypisaniu nie udostępniać zgłaszającemu anulowania ani prośby o anulowanie. Odrzucenie udostępnić obsłudze i administratorowi według ustalonej macierzy przejść. Rozpoczęcie i zakończenie realizacji udostępnić wyłącznie aktualnemu wykonawcy oraz administratorowi; przy zakończeniu wymagać formularza krótkiego opisu rozwiązania i wyświetlać zapisaną notatkę w szczegółach zgłoszenia. Ręczną zmianę priorytetu udostępnić administratorowi, a korektę kategorii aktualnemu wykonawcy i administratorowi, z rozróżnieniem przewidywania modelu i korekty. Backend nadal sprawdza uprawnienia niezależnie od widoczności przycisków, również gdy wykonawca został przypisany podczas otwartego widoku zgłaszającego.
- [x] **E6.8** Obsłużyć stany ładowania, pustą listę, niedostępność API i błędy 401/403/404. Dodać kontener frontendu do Compose.
- [x] **E6.9** Sprawdzić pełny scenariusz w przeglądarce dla zgłaszającego i osoby obsługującej.

**Wynik implementacji (2026-10-25):** działa React/TypeScript/Vite, routing, polskie formularze i błędy, sesja tylko w pamięci, listy, szczegóły, akcje ról, panel akceptacji kont, odpytywanie co 3 s i kontener Nginx w Compose. Dodano publiczną konfigurację domeny, bezpieczny odczyt duplikatów i katalog aktywnej obsługi dla administratora. Test przeglądarkowy na osobnym PostgreSQL/pgvector obejmował zgłaszającego oraz obsługę: dodanie i edycja blokady pracy, sugestia duplikatu, przyjęcie, korekta kategorii, rozpoczęcie, rozwiązanie i odczyt notatki przez autora. Encoder w teście był kontrolowany; nie oceniano jakości modelu. Build lokalny i kontenerowy, 91 testów backendu oraz 11 testów React przeszły.

**E6.3 częściowo wykonane / pominięta zależność:** lista, filtry, paginacja, niezależne statusy zadania/sprawy, filtr Do weryfikacji i przejście do korekty są gotowe. Obecnie Do weryfikacji oznacza wyłącznie kategorię unknown. Próg pewności KNN i docelowy słownik zależą od niedokończonych etapów 4–5; zgodnie z poleceniem użytkownika pominięto ich implementację. Nie oznaczamy całego E6.3 jako ukończonego. Duplikaty prezentujemy doradczo z odnośnikami, na dotychczasowym kontrakcie, bez automatycznego scalania. Nie rozszerzono zakresu o LLM ani zatwierdzanie referencji.

### Kryteria ukończenia

- Użytkownik może zalogować się, dodać zgłoszenie i zobaczyć wynik klasyfikacji oraz dostępne duplikaty.
- Osoba obsługująca może wykonać przyznane operacje, a błędy nie pozostawiają interfejsu w stanie pozornego przetwarzania.

## Etap 7. Dwa mechanizmy wyszukiwania kontekstu

**Stan początkowy:** pgvector jest używany przez klasyfikator; brak wspólnego interfejsu wyszukiwania zgłoszeń i wyszukiwania pełnotekstowego.

**Cel:** przygotować porównywalne źródła kontekstu dla RAG.

### Przypomnienie dla asystenta

- Przed E7.5 pokazać wariant wyszukiwania po opisie problemu i wariant obejmujący również opis rozwiązania. Uzgodnić zakres wyszukiwanych pól dla RAG; w obu metodach musi być taki sam. Odróżnić reprezentację do wyszukiwania RAG od embeddingu pierwotnego opisu używanego przez KNN.
- Przy E7.6 sprawdzić zgodność decyzji o indeksie z formalnym opisem pracy, który wymienia indeks wektorowy. Jeśli pomiary sugerują pozostawienie wyłącznie wyszukiwania dokładnego, przed pominięciem indeksu przedstawić konsekwencje i wrócić do użytkownika. Mały zbiór sam w sobie nie rozstrzyga wymagań pracy.
- Konfigurację pełnotekstowego wyszukiwania polskich tekstów i parametry obu metod uzasadnić dokumentacją oraz wynikami walidacji; nie pytać użytkownika o szczegóły składni PostgreSQL.

### Zadania

- [ ] **E7.1** Zdefiniować wspólny kontrakt wyszukiwania: zapytanie, metoda, limit, filtry, identyfikatory zgłoszeń, tekst kontekstu i wynik dopasowania. Wyników punktowych różnych metod nie traktować jako bezpośrednio porównywalnych.
- [ ] **E7.2** Zaimplementować semantyczne wyszukiwanie zgłoszeń: embedding pytania, odległość kosinusowa, limit wyników i próg przydatności kontekstu.
- [ ] **E7.3** Zaimplementować wyszukiwanie pełnotekstowe PostgreSQL dla polskich zgłoszeń: wybrać i opisać tokenizację oraz obsługę odmiany wyrazów, przygotować reprezentację tekstu do wyszukiwania, ranking oraz indeks i migrację. Zweryfikować działanie na polskich znakach i formach fleksyjnych.
- [ ] **E7.4** Stosować filtry uprawnień przed wyborem najlepszych wyników w obu metodach. Uwzględnić aktualny status zgłoszenia i aktualność embeddingu.
- [ ] **E7.5** Ustalić sposób aktualizacji danych wyszukiwawczych po edycji zgłoszenia i dodaniu opisu rozwiązania, tak aby obie metody korzystały z odpowiadającej sobie wersji treści. Jawnie rozdzielić tekst używany do klasyfikacji od danych dołączanych do kontekstu RAG; jeśli opis rozwiązania zostanie objęty rankingiem, zapewnić ten sam zakres wyszukiwanych pól dla obu metod. Dodanie notatki o rozwiązaniu nie uruchamia ponownie klasyfikacji pierwotnego problemu.
- [ ] **E7.6** Zmierzyć czas zapytań wektorowych i ocenić potrzebę indeksu HNSW lub IVFFlat. Jeśli zostanie dodany indeks przybliżony, sprawdzić wpływ na trafność i zapisać parametry. Brak potrzeby indeksu na małym zbiorze uzasadnić pomiarem.
- [ ] **E7.7** Przygotować wspólne reguły budowy kontekstu: kolejność wyników, usuwanie powtórzeń, identyfikatory źródeł, statusy i limit długości. Dla rozwiązanych zgłoszeń dołączać zapisany opis rozwiązania, wyraźnie odróżniony od pierwotnego opisu problemu. Dla pytania o sposoby rozwiązania podobnego problemu zastosować filtr Rozwiązany przed wyborem najlepszych wyników, tak samo w wyszukiwaniu wektorowym i pełnotekstowym; do kontekstu dołączać opisy problemu i rozwiązania oraz identyfikatory źródeł. Zachować możliwość przeszukiwania innych statusów przy ogólnych pytaniach o zgłoszenia. Docelowy budżet tokenów ustalić po wyborze LLM w etapie 8.
- [ ] **E7.8** Dodać testy pytań bez wyników, niedostępnych źródeł, filtrów oraz aktualizacji treści. Przygotować skrypt oceny trafności wyszukiwania na walidacji.

### Kryteria ukończenia

- Dla tego samego pytania można pobrać kontekst obiema metodami przez wspólny interfejs.
- Wyniki nie zawierają niedostępnych zgłoszeń i wskazują ich aktualną treść.
- Istnieje sposób zmierzenia trafności i czasu wyszukiwania przed podłączeniem generowania odpowiedzi.

## Etap 8. Asystent RAG — wariant LLM do ustalenia

**Stan początkowy:** brak integracji LLM i interfejsu rozmowy.

**Otwarta decyzja:** lokalny LLM jest założeniem pierwotnego zakresu, które ma zostać ponownie rozważone. Wybór modelu i sposobu jego udostępnienia poprzedza właściwą integrację; nie zakładamy jeszcze konkretnego sprzętu ani dostawcy.

**Cel:** generować odpowiedzi oparte na znalezionych zgłoszeniach, w tym streszczenia wcześniejszych rozwiązań problemów podobnych do opisu podanego przez użytkownika, i umożliwić zadawanie pytań w React.

### Przypomnienie dla asystenta

- Przed E8.1 zapytać o dostępny sprzęt i dopuszczalne miejsce uruchamiania LLM; jeśli rozważane jest API, również o budżet i zgodę na przesyłanie zgłoszeń do wybranej usługi. Przedstawić konkretne warianty i wyniki krótkiej próby po polsku. Nie wybierać dostawcy ani nie zakładać rezygnacji z lokalnego LLM bez decyzji użytkownika.
- Wstępne sprawdzenie wykonalności LLM warto wykonać już w etapach 2–4, gdy dostępne będą informacje o środowisku. Pełna integracja pozostaje w etapie 8; wczesna próba ma ujawnić ograniczenia przed rozbudową interfejsu. Przy odejściu od założenia lokalnego modelu przypomnieć o zgodności z formalnym zakresem pracy.
- Przed E8.9 ustalić zakres zapisu wyników eksperymentów i dostęp do nich. Propozycja do omówienia: zapisywać kontrolowane przebiegi badawcze, bez archiwizowania wszystkich zwykłych rozmów. Tymczasowa historia czatu pozostaje już ustalona.

### Zadania

- [ ] **E8.1** Rozstrzygnąć wariant LLM po porównaniu uruchomienia na komputerze użytkownika, na osobnym serwerze i przez zewnętrzne API; uwzględnić pierwotne założenie lokalnego modelu oraz potrzebę aktualizacji zakresu pracy przy jego zmianie. Wybrać model obsługujący pytania i odpowiedzi po polsku i wykonać krótki test jakości oraz czasu odpowiedzi. Zapisać model, wersję, sposób dostępu i warunki odtwarzania eksperymentów. Dla samodzielnego uruchomienia ustalić sprzęt, wymagania pamięciowe i licencję; dla API ustalić dostęp, koszty i sposób przekazywania danych. Dopiero po decyzji dodać właściwą usługę LLM lub konfigurację połączenia z nią.
- [ ] **E8.2** Zaimplementować klienta LLM z limitem czasu, kontrolą błędów i sprawdzaniem dostępności usługi. Ustalić limity równoległych generacji.
- [ ] **E8.3** Zdefiniować kontrakt endpointu rozmowy: pytanie, ograniczona historia bieżącej rozmowy, odpowiedź, źródła i obsługiwane błędy. Historię przechowywać wyłącznie w pamięci bieżącego widoku React i przekazywać niezbędną część przy kolejnym pytaniu. Nie utrwalać rozmów w bazie ani pamięci przeglądarki i nie tworzyć endpointów listowania lub przywracania rozmów. Zapis eksperymentów realizować oddzielnie zgodnie z E8.9.
- [ ] **E8.4** Zbudować potok: weryfikacja użytkownika i roli obsługi lub administratora → wyszukiwanie dostępnych zgłoszeń → przygotowanie kontekstu → generowanie → walidacja źródeł → odpowiedź. Sprawdzać rolę przy każdym pytaniu, również uzupełniającym. Dostęp zgłaszającego do własnych zgłoszeń nie daje mu dostępu do LLM.
- [ ] **E8.5** Przygotować wersjonowany prompt: oparcie odpowiedzi na kontekście, wskazywanie identyfikatorów źródeł, przyznanie braku danych i traktowanie tekstu zgłoszeń jako danych, a nie instrukcji. Dla opisu bieżącego problemu streszczać zapisane rozwiązania podobnych zakończonych spraw i przypisywać poszczególne sposoby rozwiązania do źródeł. Wyraźnie odróżniać to, co wykonano w źródłowym zgłoszeniu, od możliwości zastosowania w nowym przypadku; nie obiecywać skuteczności na podstawie samego podobieństwa tekstów. Jeśli nie znaleziono odpowiednich rozwiązanych spraw, poinformować o braku udokumentowanego rozwiązania.
- [ ] **E8.6** Ustalić budżet tokenów dla pytania, tymczasowej historii, kontekstu i odpowiedzi. Zachować spójność źródeł przy skracaniu tekstu i ograniczyć przesyłaną historię do potrzebnych ostatnich wiadomości. Obsłużyć pytania uzupełniające w bieżącej rozmowie, ponownie pobierając kontekst i sprawdzając dostęp do źródeł; poprzednie odpowiedzi LLM nie zastępują zgłoszeń jako źródła faktów.
- [ ] **E8.7** Obsłużyć pytania wykraczające poza znaleziony kontekst. Pełne statystyki i zestawienia całej bazy pozostawić poza zakresem asystenta; dla takich pytań jasno poinformować o tym ograniczeniu. Nie wyprowadzać pełnej liczby zgłoszeń z ograniczonego zestawu podobnych wyników i nie dodawać mechanizmu generowania lub wykonywania SQL przez LLM.
- [ ] **E8.8** Sprawdzać, czy wskazane źródła należą do pobranego kontekstu i pozostają dostępne użytkownikowi. Przy wylogowaniu lub utracie dostępu do asystenta czyścić tymczasową historię widoku; nie przywracać jej po zalogowaniu na inne konto. Nie traktować historii przesłanej przez klienta jako dowodu uprawnień do wskazanych zgłoszeń.
- [ ] **E8.9** Osobno od tymczasowej historii czatu zapisywać dane potrzebne do eksperymentów: pytanie, wykorzystaną historię dla pytań uzupełniających, metodę wyszukiwania, wersje źródeł, modelu i promptu, parametry generowania, odpowiedź i czasy etapów. Ustalić dostęp do wyników badań i zakres zapisu; nie tworzyć na tej podstawie archiwum rozmów dostępnego w interfejsie użytkownika. Odświeżenie strony lub wylogowanie nie usuwa zapisanych wyników eksperymentów.
- [ ] **E8.10** Dodać czat w React wyłącznie dla obsługi i administratora: tymczasowe wiadomości w pamięci bieżącego widoku, stan oczekiwania, obsługę błędów i odnośniki do źródłowych zgłoszeń. Sprawdzić usunięcie historii po odświeżeniu strony i wylogowaniu, bez automatycznego odtwarzania. Dla zgłaszającego nie udostępniać czatu; odmowę dostępu egzekwować również przez API. Wybór metody wyszukiwania udostępnić w konfiguracji eksperymentów.
- [ ] **E8.11** Sprawdzić pytania z odpowiedzią, bez odpowiedzi, pytania uzupełniające, niedostępne źródła, instrukcje umieszczone w treści zgłoszenia oraz niedostępność LLM. Sprawdzić streszczenie wcześniejszych rozwiązań dla opisu bieżącego problemu, przypisanie każdego sposobu rozwiązania do właściwego źródła i brak wymyślonych rozwiązań przy samych aktywnych lub odrzuconych zgłoszeniach. Zweryfikować odpowiedź na pytanie o pełne statystyki poza zakresem. Prompt i parametry dopracowywać na pytaniach walidacyjnych.

### Kryteria ukończenia

- Użytkownik otrzymuje odpowiedź z odnośnikami do dostępnych źródeł albo informację o niewystarczających danych.
- Zmiana metody wyszukiwania nie wymaga zmiany pozostałej części potoku.
- Można odtworzyć warunki konkretnego wywołania, przy świadomości możliwej zmienności generowania i ograniczeń wybranego wariantu LLM.

## Etap 9. Panel administratora i kompletne uruchamianie

**Stan początkowy:** backend zarządzania użytkownikami powstaje w etapie 3; podstawowy frontend i czat w etapach 6 i 8.

**Cel:** domknąć funkcje użytkowe oraz sprawdzić wdrożenie od zera.

### Przypomnienie dla asystenta

Przed końcowym sprawdzeniem Compose ustalić docelowe środowisko demonstracji, jeśli nadal nie jest znane lub różni się od sprawdzonego środowiska. Wrócić do wariantu LLM wyłącznie w razie rzeczywistej przeszkody ujawnionej testem. Nie dodawać przy tej okazji nowych funkcji administracyjnych wyłączonych z zakresu.

### Zadania

- [ ] **E9.1** Zbudować panel administratora: lista kont, widok rejestracji oczekujących na akceptację, formularz zatwierdzania z obowiązkowym wyborem jednej z trzech ról, późniejsza zmiana ról i aktywacja/dezaktywacja. Nie wybierać roli automatycznie; obsłużyć walidację API przy próbie akceptacji bez roli. Wyświetlać stan akceptacji osobno od aktywności konta, a brak roli dla kont oczekujących jako oczekiwanie na jej nadanie. Nie dodawać resetowania zapomnianego hasła ani odnośnika do odzyskiwania dostępu na ekranie logowania.
- [ ] **E9.2** Dopracować samodzielne przyjmowanie zgłoszeń przez obsługę, przypisywanie i zmianę wykonawcy przez administratora oraz widoki dostępne poszczególnym rolom. Zweryfikować respektowanie bieżącej roli i aktywności zalogowanego użytkownika. Przypadek dezaktywacji wykonawcy mającego aktywne zgłoszenia pozostaje poza zakresem.
- [ ] **E9.3** Ujednolicić polskie komunikaty, nawigację, formularze oraz widoki na mniejszych ekranach; sprawdzić podstawową obsługę klawiaturą. Zweryfikować polskie nazwy i komunikaty w rejestracji, logowaniu, zgłoszeniach, panelu administratora i czacie, także przy błędach i pustych wynikach.
- [ ] **E9.4** Uporządkować Compose obejmujące PostgreSQL/pgvector, FastAPI i frontend. Usługę LLM umieścić w Compose albo skonfigurować połączenie z nią zgodnie z decyzją E8.1. Dodać sprawdzanie gotowości, potrzebne wolumeny i konfigurację uruchomienia bez deweloperskiego przeładowywania kodu; udokumentować zależności pozostające poza Compose.
- [ ] **E9.5** Uporządkować pobieranie i przechowywanie modelu embeddingów: wersję, cache i pierwsze uruchomienie. Dla samodzielnie uruchamianego LLM zapewnić analogiczną obsługę; dla zdalnej usługi skonfigurować adres i ewentualne dane dostępowe poza kodem. Sprawdzić zachowanie przy braku modelu, sieci lub dostępności usługi według wybranego wariantu.
- [ ] **E9.6** Przygotować instrukcję pierwszego uruchomienia: konfiguracja, migracje, pierwszy administrator, import danych i uruchomienie usług. Oddzielić dane demonstracyjne od testowych.
- [ ] **E9.7** Uruchomić system na pustej bazie według instrukcji, a następnie sprawdzić restart i zachowanie danych oraz przerwanych zadań.
- [ ] **E9.8** Wykonać scenariusze dla trzech ról: zgłaszający dodaje zgłoszenie i obserwuje historię; obsługa przyjmuje i realizuje zgłoszenie oraz pyta LLM; administrator zarządza kontami i ręcznie zmienia priorytet. Sprawdzić samodzielne anulowanie przed przypisaniem, blokadę anulowania po przypisaniu i wyścig anulowania z przyjęciem; osobno sprawdzić odrzucenie przez obsługę lub administratora, widoczność statusów i brak dostępu zgłaszającego do czatu.
- [ ] **E9.9** Sprawdzić odmowę dostępu przez bezpośrednie żądania API, awarie LLM i błędy przetwarzania; poprawić wykryte błędy przed zamrożeniem wersji do badań.

### Kryteria ukończenia

- Cały system można uruchomić na podstawie README z przygotowanej konfiguracji.
- Wszystkie trzy role wykonują swoje scenariusze przez interfejs, a backend egzekwuje uprawnienia.
- Restart zachowuje dane, a stan przerwanego przetwarzania jest rozpoznawalny i możliwy do obsłużenia.

## Etap 10. Ewaluacja i porównanie metod

**Stan początkowy:** protokół, dane i metryki przygotowano w etapie 4; parametry dobierano na walidacji w etapach 5, 7 i 8.

**Cel:** uzyskać końcowe wyniki i materiał do rozdziału badawczego.

### Przypomnienie dla asystenta

Przed końcowym uruchomieniem sprawdzić, czy podziały danych, rubryka oceny, oceniający i wariant LLM zostały rozstrzygnięte w poprzednich etapach. Pytać tylko o rzeczywiste braki. Po obejrzeniu wyników testowych nie proponować strojenia na tych samych przykładach; omówić ograniczenia i ewentualny nowy, niezależny eksperyment. Słabszy wynik obowiązkowego modelu na polskich danych nie oznacza automatycznej zgody na jego wymianę.

### Zadania

- [ ] **E10.1** Zamrozić wersję kodu, dane, podział zbiorów, konfigurację KNN, progi, indeksy, prompt i model LLM. Zapisać identyfikator rewizji kodu, wersje zależności i parametry sprzętu.
- [ ] **E10.2** Przygotować skrypty uruchamiające eksperymenty oraz format wyników i metadanych. Zapewnić odtworzenie bazy lub jej stanu dla każdego przebiegu.
- [ ] **E10.3** Ocenić kategorię i priorytet na zbiorze testowym: accuracy, macro-F1, wyniki per klasa, macierze pomyłek oraz udział zgłoszeń skierowanych do weryfikacji. Raportować pokrycie, aby odrzucanie trudnych przypadków nie zawyżało pozornie jakości.
- [ ] **E10.4** Osobno ocenić poprawność reguły checkboxa, eskalację na ustalonych scenariuszach i duplikaty na oznaczonych parach lub grupach. Nie traktować wymuszenia `critical` przez formularz jako poprawnego przewidywania KNN. Nie dodawać przewidywań z testu do zbioru referencyjnego podczas pomiaru.
- [ ] **E10.5** Porównać trafność wyszukiwania wektorowego i pełnotekstowego, np. przez Recall@k i MRR, dla tych samych pytań i dostępnych źródeł.
- [ ] **E10.6** Porównać odpowiedzi RAG przy identycznym modelu, prompcie, budżecie kontekstu i ustawieniach generowania. Parametry specyficzne dla wyszukiwania dobrać wcześniej na walidacji i ujawnić w opisie eksperymentu.
- [ ] **E10.7** Ocenić poprawność, kompletność, oparcie na źródłach, poprawność odnośników i zachowanie przy braku danych według wcześniej ustalonej rubryki. Zapisać sposób oceny, oceniających i ograniczenia subiektywności.
- [ ] **E10.8** Zmierzyć osobno czas embeddingu, wyszukiwania, generowania i całej odpowiedzi. Oddzielić pierwsze uruchomienie modelu od kolejnych wywołań; powtórzyć pomiary, aby pokazać zmienność.
- [ ] **E10.9** Przygotować tabele, wykresy i analizę reprezentatywnych błędów oraz ograniczeń: język i wielkość zbioru, etykietowanie i ręczna weryfikacja przez samego autora bez drugiego oceniającego, wybrany model i wariant udostępnienia LLM, indeksy i zadania w procesie API.
- [ ] **E10.10** Opracować rozdział ewaluacji, wnioski i scenariusz demonstracji. Uzupełnić README o odtwarzanie eksperymentów i sprawdzić powiązanie wyników z zapisanymi artefaktami.

### Kryteria ukończenia

- Wyniki mają zapisane warunki uzyskania i można ponownie uruchomić eksperymenty.
- Porównanie zmienia metodę pozyskiwania kontekstu przy kontrolowanych pozostałych warunkach.
- Wnioski wynikają z pomiarów i obejmują także niepowodzenia oraz ograniczenia systemu.

## Dokumentacja i pisanie pracy prowadzone równolegle

| Kiedy | Materiał do przygotowania |
|---|---|
| Etapy 1–3 | Wymagania, przypadki użycia, model danych, diagram architektury, macierz uprawnień i opis BackgroundTasks. |
| Etapy 4–5 | Pochodzenie danych, etykietowanie, podział zbiorów, algorytm KNN, eskalacja i dobór progów duplikatów. |
| Etapy 6–9 | Projekt interfejsu, oba mechanizmy wyszukiwania, potok RAG, wersjonowanie kontekstu i uruchamianie kontenerów. |
| Etap 10 | Protokół badań, wyniki, analiza błędów, ograniczenia i wnioski. |
| Przez cały projekt | Przegląd literatury, bibliografia, uzasadnienia decyzji i aktualizacja instrukcji uruchomienia. |

W opisie aspektu inżynierskiego należy zastąpić kolejki zadań asynchronicznych przetwarzaniem w tle przez FastAPI `BackgroundTasks`. Integracja backendu, relacyjnej bazy z wyszukiwaniem wektorowym, LLM i aplikacji webowej pozostaje podstawą projektu. Pierwotne założenie lokalnego LLM jest do ponownego rozważenia; po wyborze wariantu trzeba ujednolicić formalny zakres, opis architektury i instrukcję uruchomienia.

## Pierwszy pakiet prac

Zaczynamy od **etapów 1–2**: uruchomienia i naprawy obecnego API, a następnie zastąpienia Celery przez `BackgroundTasks`. Pozostałe etapy realizujemy po uzyskaniu i sprawdzeniu tego fundamentu.
