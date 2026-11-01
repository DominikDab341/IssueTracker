# Próbka 40 zgłoszeń do przeglądu

Wszystkie etykiety poniżej są propozycjami generatora; status: **pending**.
Źródłem danych i decyzji jest `tickets.json`. Zmiany można przekazać według ID.
Znaczenie etykiet i sposób zatwierdzania opisuje `labeling-guide.md`.

## ACC-01 — Konta i uprawnienia / low

Po zmianie nazwiska portal pokazuje dawną nazwę mojego konta. Logowanie i wszystkie uprawnienia działają poprawnie, mogę normalnie pracować.

- Kategoria: Dane profilu konta, a nie awaria funkcji aplikacji.
- Priorytet bazowy: Wyłącznie niedogodność w prezentacji nazwy.
- Grupa: `acc-01`; checkbox blokady pracy: `false`.

## ACC-02 — Konta i uprawnienia / low

Co kilka dni dostaję przypomnienie o końcu ważności hasła, choć zmieniłem je wczoraj. Hasło działa i otwieram wszystkie potrzebne systemy.

- Kategoria: Powiadomienia dotyczące ważności poświadczeń.
- Priorytet bazowy: Komunikat nie ogranicza pracy.
- Grupa: `acc-02`; checkbox blokady pracy: `false`.

## ACC-03 — Konta i uprawnienia / medium

Po przeniesieniu do zespołu rozliczeń folder zespołu otwiera się tylko do odczytu. Nie mogę wgrać zestawienia, ale na razie przekazuję je opiekunowi, który zapisuje plik za mnie.

- Kategoria: Jawne ograniczenie prawa zapisu do folderu.
- Priorytet bazowy: Zapis jest utrudniony, istnieje działające obejście.
- Grupa: `acc-folder-access`; checkbox blokady pracy: `false`.

## ACC-04 — Konta i uprawnienia / medium

W tej samej sprawie uprawnień do katalogu rozliczeń: mogę przeglądać dokumenty, lecz zapis kończy się odmową dostępu. Wysyłam zestawienia opiekunowi i on umieszcza je w folderze.

- Kategoria: Odmowa prawa zapisu, bez objawów uszkodzenia pliku.
- Priorytet bazowy: Można przekazać zapis innej osobie.
- Grupa: `acc-folder-access`; checkbox blokady pracy: `false`.

## ACC-05 — Konta i uprawnienia / medium

Nowy telefon nie otrzymuje potwierdzeń logowania do poczty. Wchodzę obecnie kodem z zapasowego klucza i odbieram wiadomości, ale chciałbym przywrócić potwierdzenia na telefonie.

- Kategoria: Problem drugiego składnika uwierzytelniania.
- Priorytet bazowy: Zapasowy klucz pozwala kontynuować pracę.
- Grupa: `acc-05`; checkbox blokady pracy: `false`.

## ACC-06 — Konta i uprawnienia / medium

Aplikacja odrzuca mój login komunikatem o wygaśnięciu hasła. Samodzielna zmiana w portalu działa i po niej odzyskuję dostęp, ale hasło wygasa ponownie następnego dnia.

- Kategoria: Cykl ważności hasła i dostęp do konta.
- Priorytet bazowy: Samodzielna zmiana pozwala odzyskać dostęp.
- Grupa: `acc-06`; checkbox blokady pracy: `false`.

## ACC-07 — Konta i uprawnienia / high

Moje konto do systemu magazynowego zostało zablokowane. Nie mogę przyjąć dzisiejszej dostawy; nie mam drugiego konta ani możliwości wykonania tego zadania poza systemem.

- Kategoria: Jawna blokada konta.
- Priorytet bazowy: Ważne zadanie jednej osoby zablokowane bez obejścia.
- Grupa: `acc-07`; checkbox blokady pracy: `true`.

## ACC-08 — Konta i uprawnienia / high

Przy logowaniu do VPN widzę komunikat: użytkownik nie ma uprawnienia do połączeń zdalnych. Nie mogę wykonać z domu pilnego rozliczenia, a dostęp jest możliwy wyłącznie przez ten VPN.

- Kategoria: VPN jawnie odmawia uprawnienia, nie zgłasza awarii połączenia.
- Priorytet bazowy: Brak dostępu do niezbędnego zadania i brak obejścia.
- Grupa: `acc-08`; checkbox blokady pracy: `true`.

## ACC-09 — Konta i uprawnienia / high

Po zmianie stanowiska zniknęło mi prawo zatwierdzania faktur. System wyświetla brak uprawnień, a dziś muszę zatwierdzić płatności; w tej zmianie nie ma drugiej upoważnionej osoby.

- Kategoria: Brak roli wymaganej do wykonania operacji.
- Priorytet bazowy: Zatwierdzanie płatności zablokowane bez zastępstwa.
- Grupa: `acc-09`; checkbox blokady pracy: `true`.

## ACC-10 — Konta i uprawnienia / critical

Od rana wszyscy pracownicy centrum obsługi dostają przy logowaniu informację, że ich konta są wyłączone. Cały dział nie może obsługiwać klientów; żadne zapasowe konto nie jest dostępne.

- Kategoria: Jawne wyłączenie kont wielu użytkowników.
- Priorytet bazowy: Kluczowy proces całego działu jest niedostępny.
- Grupa: `acc-10`; checkbox blokady pracy: `true`.

## HW-01 — Sprzęt / low

Na zewnętrznym monitorze pojawił się jeden stale świecący punkt przy dolnej krawędzi. Obraz poza tym jest czytelny i wszystkie zadania wykonuję normalnie.

- Kategoria: Fizyczny objaw na ekranie.
- Priorytet bazowy: Drobna wada bez ograniczenia pracy.
- Grupa: `hw-01`; checkbox blokady pracy: `false`.

## HW-02 — Sprzęt / low

Wentylator w komputerze zaczął głośniej pracować. Urządzenie się nie wyłącza, nie ma komunikatów o temperaturze i mogę wykonywać wszystkie zadania.

- Kategoria: Objaw działania fizycznego podzespołu.
- Priorytet bazowy: Hałas jest uciążliwością, bez blokady zadań.
- Grupa: `hw-02`; checkbox blokady pracy: `false`.

## HW-03 — Sprzęt / medium

Drukarka przy recepcji zacina papier także przy uruchomieniu strony testowej z jej panelu. Dokumenty drukuję teraz na urządzeniu w sąsiednim pokoju.

- Kategoria: Zacięcie występuje niezależnie od aplikacji i połączenia.
- Priorytet bazowy: Inna drukarka stanowi działające obejście.
- Grupa: `hw-reception-printer`; checkbox blokady pracy: `false`.

## HW-04 — Sprzęt / medium

Ta sama drukarka recepcji ponownie zatrzymuje kartkę w środku, również przy własnym teście. Korzystam z drukarki w sąsiednim pokoju i mogę wydawać dokumenty.

- Kategoria: Fizyczny mechanizm podawania papieru.
- Priorytet bazowy: Wydruk na innym urządzeniu pozwala pracować.
- Grupa: `hw-reception-printer`; checkbox blokady pracy: `false`.

## HW-05 — Sprzęt / medium

Wbudowana klawiatura laptopa nie reaguje na kilka klawiszy. Podłączyłem klawiaturę USB i mogę pisać, ale utrudnia to pracę w salach spotkań.

- Kategoria: Niesprawne klawisze urządzenia.
- Priorytet bazowy: Zewnętrzna klawiatura umożliwia pracę.
- Grupa: `hw-05`; checkbox blokady pracy: `false`.

## HW-06 — Sprzęt / medium

Kamera w laptopie pokazuje czarny obraz także w systemowym teście urządzenia. Na spotkaniach korzystam z pożyczonej kamery USB, która działa poprawnie.

- Kategoria: Objaw urządzenia potwierdzony poza programem spotkań.
- Priorytet bazowy: Pożyczona kamera jest sprawnym zastępstwem.
- Grupa: `hw-06`; checkbox blokady pracy: `false`.

## HW-07 — Sprzęt / high

Komputer nie uruchamia się po naciśnięciu przycisku, nie świecą żadne kontrolki mimo podłączenia do sprawnego gniazdka. Tylko na nim mam stanowisko do obsługi zamówień i nie ma komputera zastępczego.

- Kategoria: Brak zasilania lub reakcji urządzenia.
- Priorytet bazowy: Ważne zadanie jednej osoby nie ma zastępstwa.
- Grupa: `hw-07`; checkbox blokady pracy: `true`.

## HW-08 — Sprzęt / high

Skaner kodów na moim stanowisku nie włącza się i nie reaguje także po podpięciu do innego portu. Nie mogę rejestrować paczek; program nie pozwala wpisywać kodów ręcznie i nie mamy zapasowego skanera.

- Kategoria: Brak reakcji fizycznego urządzenia.
- Priorytet bazowy: Rejestrowanie paczek jest niemożliwe bez obejścia.
- Grupa: `hw-08`; checkbox blokady pracy: `true`.

## HW-09 — Sprzęt / high

Zasilacz laptopa przestał ładować, a bateria jest już rozładowana. Muszę dzisiaj przygotować listę płac na tym urządzeniu; innego zasilacza ani stanowiska z tym dostępem nie ma.

- Kategoria: Niedziałający zasilacz i rozładowane urządzenie.
- Priorytet bazowy: Niezbędne zadanie blokuje brak zastępczego sprzętu.
- Grupa: `hw-09`; checkbox blokady pracy: `true`.

## HW-10 — Sprzęt / critical

Główna macierz dyskowa nie włącza się, na obu zasilaczach zgasły kontrolki. Wszystkie zespoły straciły dostęp do plików potrzebnych do obsługi zamówień i nie ma dostępnej kopii roboczej.

- Kategoria: Fizyczne objawy braku zasilania macierzy.
- Priorytet bazowy: Awaria kluczowego sprzętu blokuje wiele zespołów.
- Grupa: `hw-10`; checkbox blokady pracy: `true`.

## NET-01 — Sieć i łączność / low

Po wybudzeniu laptopa połączenie z firmowym Wi-Fi pojawia się dopiero po kilku sekundach. Potem działa stabilnie; nie przerywa to zadań i mogę normalnie korzystać ze wszystkich narzędzi.

- Kategoria: Krótkie opóźnienie zestawienia połączenia bezprzewodowego.
- Priorytet bazowy: Drobna zwłoka bez blokady wymaganych zadań.
- Grupa: `net-01`; checkbox blokady pracy: `false`.

## NET-02 — Sieć i łączność / low

W pokoju socjalnym zasięg firmowego Wi-Fi jest słaby i strony otwierają się wolno. Nie wykonujemy tam zadań służbowych; przy biurkach połączenie działa prawidłowo i praca nie jest utrudniona.

- Kategoria: Słaby zasięg połączenia bezprzewodowego w określonym miejscu.
- Priorytet bazowy: Niedogodność poza miejscem wykonywania pracy.
- Grupa: `net-02`; checkbox blokady pracy: `false`.

## NET-03 — Sieć i łączność / medium

W sali spotkań B połączenie Wi-Fi rozłącza się co kilka minut. Po podłączeniu laptopa przewodem do gniazda w tej sali spotkania internetowe działają stabilnie.

- Kategoria: Zrywanie połączenia bezprzewodowego.
- Priorytet bazowy: Połączenie przewodowe jest działającym obejściem.
- Grupa: `net-meeting-room-b`; checkbox blokady pracy: `false`.

## NET-04 — Sieć i łączność / medium

Zgłaszam to samo zrywanie firmowej sieci bezprzewodowej w sali B. Rozmowę mogę prowadzić po kablu; po odłączeniu przewodu Wi-Fi ponownie gubi połączenie.

- Kategoria: Objaw dotyczy konkretnego połączenia Wi-Fi.
- Priorytet bazowy: Kabel pozwala kontynuować spotkanie.
- Grupa: `net-meeting-room-b`; checkbox blokady pracy: `false`.

## NET-05 — Sieć i łączność / medium

Domowy internet zrywa mi połączenie z firmą kilka razy dziennie, również przy zwykłym przeglądaniu stron. Przełączam laptop na internet z telefonu i wtedy mogę pracować stabilnie.

- Kategoria: Utrata połączenia także poza jedną aplikacją.
- Priorytet bazowy: Internet z telefonu umożliwia pracę.
- Grupa: `net-05`; checkbox blokady pracy: `false`.

## NET-06 — Sieć i łączność / medium

W pokoju 12 gniazdo sieciowe nie daje połączenia, a ten sam laptop z tym samym przewodem łączy się w sąsiednim pokoju. Tymczasowo korzystam z firmowego Wi-Fi i obsługuję sprawy.

- Kategoria: Problem ścieżki połączenia przez konkretne gniazdo.
- Priorytet bazowy: Sprawne Wi-Fi zapewnia obejście.
- Grupa: `net-06`; checkbox blokady pracy: `false`.

## NET-07 — Sieć i łączność / high

VPN przyjmuje hasło i potwierdzenie logowania, ale zestawianie tunelu kończy się przekroczeniem czasu. Internet poza VPN działa; nie mogę połączyć się z systemem do dzisiejszej wysyłki i nie mam innej drogi dostępu.

- Kategoria: Uwierzytelnianie działa, nie udaje się zestawić połączenia.
- Priorytet bazowy: Ważne zadanie jednej osoby zablokowane bez obejścia.
- Grupa: `net-07`; checkbox blokady pracy: `true`.

## NET-08 — Sieć i łączność / high

Na moim stanowisku połączenie przewodowe i Wi-Fi nie uzyskują dostępu do sieci firmowej. Nie mogę obsługiwać zamówień, a stanowiska zastępczego ani zasięgu internetu mobilnego tutaj nie ma.

- Kategoria: Brak dostępu do sieci przez dwa rodzaje połączeń.
- Priorytet bazowy: Obsługa zamówień zablokowana, nie ma alternatywy.
- Grupa: `net-08`; checkbox blokady pracy: `true`.

## NET-09 — Sieć i łączność / high

Podczas zdalnej sesji z serwerem połączenie przerywa się co kilkanaście sekund. Dotyczy także innych usług po tym łączu; muszę dzisiaj zakończyć import danych i nie mam innego połączenia ani dostępu na miejscu.

- Kategoria: Utrata łączności z wieloma usługami, bez zgadywania przyczyny.
- Priorytet bazowy: Pilne zadanie nie ma działającej drogi zastępczej.
- Grupa: `net-09`; checkbox blokady pracy: `true`.

## NET-10 — Sieć i łączność / critical

W całym oddziale przestały działać internet i połączenia z centralą, zarówno po kablu, jak i po Wi-Fi. Trzydzieści osób nie może przyjmować zamówień, a łącze zapasowe również nie daje dostępu.

- Kategoria: Rozległy brak łączności sieciowej.
- Priorytet bazowy: Kluczowa obsługa zamówień wielu osób zablokowana.
- Grupa: `net-10`; checkbox blokady pracy: `true`.

## SW-01 — Oprogramowanie / low

Po aktualizacji edytora część ikon na pasku narzędzi ma rozmyte krawędzie. Wszystkie przyciski działają, dokumenty zapisują się poprawnie i mogę pracować jak wcześniej.

- Kategoria: Niepoprawne wyświetlanie elementów aplikacji.
- Priorytet bazowy: Wyłącznie kosmetyczny problem interfejsu.
- Grupa: `sw-01`; checkbox blokady pracy: `false`.

## SW-02 — Oprogramowanie / low

Lista ostatnio otwieranych dokumentów w programie nie zachowuje wybranej kolejności po ponownym uruchomieniu. Dokumenty otwierają się normalnie, a sortowanie nie jest potrzebne do wykonywania zadań.

- Kategoria: Błąd zapamiętywania ustawienia aplikacji.
- Priorytet bazowy: Drobna uciążliwość bez utraty wymaganej funkcji.
- Grupa: `sw-02`; checkbox blokady pracy: `false`.

## SW-03 — Oprogramowanie / medium

Program do raportów zamyka się przy eksporcie do PDF. Te same raporty mogę otworzyć w przeglądarce i zapisać do PDF przez drukowanie, więc wysyłam je terminowo.

- Kategoria: Awaria konkretnej funkcji programu.
- Priorytet bazowy: Alternatywny sposób tworzenia PDF działa.
- Grupa: `sw-reports-pdf`; checkbox blokady pracy: `false`.

## SW-04 — Oprogramowanie / medium

Wracam do tego samego błędu eksportu raportów: naciśnięcie zapisu jako PDF wyłącza aplikację. Nadal przygotowuję pliki przez wydruk z wersji przeglądarkowej i mogę przekazać raporty.

- Kategoria: Powtórzenie awarii eksportu, nie problemu drukarki.
- Priorytet bazowy: Wersja przeglądarkowa pozwala wykonać zadanie.
- Grupa: `sw-reports-pdf`; checkbox blokady pracy: `false`.

## SW-05 — Oprogramowanie / medium

W jednym programie drukowanie formularza kończy się zamknięciem okna. Strona testowa drukarki działa; mogę wyeksportować formularz do obrazu i wydrukować go z innego programu.

- Kategoria: Błąd dotyczy aplikacji przy sprawnej drukarce.
- Priorytet bazowy: Inny program umożliwia wydruk.
- Grupa: `sw-05`; checkbox blokady pracy: `false`.

## SW-06 — Oprogramowanie / medium

Kalendarz w aplikacji na komputerze nie pokazuje nowo dodanych spotkań, choć są widoczne w jej wersji WWW. Sprawdzam terminy w przeglądarce i nie opuszczam spotkań.

- Kategoria: Nieaktualny widok w konkretnej wersji aplikacji.
- Priorytet bazowy: Wersja WWW zapewnia dostęp do terminów.
- Grupa: `sw-06`; checkbox blokady pracy: `false`.

## SW-07 — Oprogramowanie / high

Program księgowy zamyka się za każdym razem przy zatwierdzaniu deklaracji. Inne funkcje działają, ale muszę dziś wysłać deklarację; nie ma wersji WWW ani innego sposobu jej zatwierdzenia.

- Kategoria: Powtarzalna awaria operacji w aplikacji.
- Priorytet bazowy: Ważna operacja jest niemożliwa bez obejścia.
- Grupa: `sw-07`; checkbox blokady pracy: `true`.

## SW-08 — Oprogramowanie / high

Po aktualizacji aplikacja do podpisywania dokumentów nie uruchamia się i od razu pokazuje błąd programu. Muszę podpisać dzisiaj umowę, a firmowa procedura dopuszcza tylko tę aplikację i nie ma zastępstwa.

- Kategoria: Program nie uruchamia się po aktualizacji.
- Priorytet bazowy: Podpisanie wymaganej umowy jest zablokowane.
- Grupa: `sw-08`; checkbox blokady pracy: `true`.

## SW-09 — Oprogramowanie / high

W systemie magazynowym zatwierdzenie mojej listy wysyłkowej stale zwraca błąd obliczeń. Mam uprawnienia i inne listy otwierają się poprawnie, ale tej wysyłki nie da się zatwierdzić ręcznie ani w innym narzędziu.

- Kategoria: Błąd obliczeń funkcji, nie odmowa dostępu.
- Priorytet bazowy: Konkretne ważne zadanie nie ma obejścia.
- Grupa: `sw-09`; checkbox blokady pracy: `true`.

## SW-10 — Oprogramowanie / critical

Po wdrożeniu nowej wersji system zamówień zamyka sesję błędem programu przy próbie zapisania dowolnego zamówienia. Dotyczy wszystkich konsultantów; cała obsługa sprzedaży stoi i nie ma trybu zastępczego.

- Kategoria: Awaria funkcji zapisu aplikacji dla wielu użytkowników.
- Priorytet bazowy: Kluczowa usługa całego zespołu jest niedostępna.
- Grupa: `sw-10`; checkbox blokady pracy: `true`.

---

# Rozszerzenie do 120 zgłoszeń — 2026-11-01

Użytkownik zatwierdził pierwotne 40 przykładów i ich etykiety w rozmowie. Powyższy opis `pending` jest stanem historycznym.
Poniżej 80 nowych propozycji oczekujących na ręczny przegląd. Zbiór ma po 30 przykładów na kategorię.
Aktualne decyzje znajdują się w `tickets.json`; zachowano 40 zatwierdzeń i 80 stanów `pending`.

## ACC-11 — accounts_access / low

W wizytówce mojego konta w książce adresowej widnieje stary numer telefonu wewnętrznego. Loguję się bez problemu i korzystam ze wszystkich usług; błędny numer nie przeszkadza mi w zadaniach.

- Kategoria: Nieaktualna informacja w profilu konta.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `acc-11`; work_blocked: `false`; review: `pending`.

## ACC-12 — accounts_access / low

W portalu samoobsługowym nazwa mojego zespołu nadal jest poprzednia, mimo przeniesienia miesiąc temu. Dostęp do nowego zespołu już mam, a wyświetlana nazwa niczego nie blokuje.

- Kategoria: Dane organizacyjne przypisane do konta.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `acc-12`; work_blocked: `false`; review: `pending`.

## ACC-13 — accounts_access / low

Przy logowaniu widzę na liście dawną rolę z zakończonego projektu. Jej wybór niczego nie otwiera, natomiast bieżąca rola daje mi wszystkie potrzebne uprawnienia i mogę normalnie pracować.

- Kategoria: Widoczność nieaktualnej roli użytkownika.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `acc-13`; work_blocked: `false`; review: `pending`.

## ACC-14 — accounts_access / low

Panel konta pokazuje komunikat o konieczności uzupełnienia zdjęcia profilowego. Nie chcę dodawać zdjęcia; komunikat można zamknąć i wszystkie narzędzia pozostają dostępne.

- Kategoria: Wymaganie dotyczące profilu konta.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `acc-14`; work_blocked: `false`; review: `pending`.

## ACC-15 — accounts_access / medium

W folderze projektu Orion straciłem prawo tworzenia nowych dokumentów, chociaż istniejące mogę czytać. Współpracowniczka z zespołu zapisuje przesyłane przeze mnie pliki, więc praca trwa.

- Kategoria: Brak prawa tworzenia dokumentów w folderze.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-orion-folder`; work_blocked: `false`; review: `pending`.

## ACC-16 — accounts_access / medium

Chodzi o tę samą odmowę zapisu w katalogu Orion: odczyt działa, ale przy dodaniu pliku pojawia się brak uprawnień. Przekazuję dokumenty koleżance, która umieszcza je w katalogu.

- Kategoria: Jawna odmowa uprawnienia do zapisu.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-orion-folder`; work_blocked: `false`; review: `pending`.

## ACC-17 — accounts_access / medium

Po wymianie telefonu aplikacja uwierzytelniająca nie ma mojego konta firmowego i nie mogę zatwierdzać nią logowania. Zachowane kody awaryjne pozwalają mi wejść do systemów i wykonać zadania.

- Kategoria: Brak skonfigurowanego składnika uwierzytelniania.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-17`; work_blocked: `false`; review: `pending`.

## ACC-18 — accounts_access / medium

Logowanie jednokrotne do portalu zwraca informację, że moje konto nie jest przypisane do tej aplikacji. Bezpośrednie logowanie kontem lokalnym nadal działa i mogę obsługiwać sprawy.

- Kategoria: Brak przypisania konta do aplikacji.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-18`; work_blocked: `false`; review: `pending`.

## ACC-19 — accounts_access / medium

Próba samodzielnego ustawienia nowego hasła kończy się komunikatem, że nie mam prawa zmieniać hasła. Dotychczasowe hasło nadal działa, korzystam z poczty i pozostałych systemów.

- Kategoria: Odmowa uprawnienia do zmiany hasła.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-19`; work_blocked: `false`; review: `pending`.

## ACC-20 — accounts_access / medium

W narzędziu zgłoszeniowym mam rolę pozwalającą czytać sprawy, ale odebrano mi prawo dopisywania notatek. Przekazuję notatki dyżurnemu, który je zapisuje; obsługa klientów jest możliwa.

- Kategoria: Brak konkretnego uprawnienia w roli.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-20`; work_blocked: `false`; review: `pending`.

## ACC-21 — accounts_access / medium

Portal odrzuca logowanie kluczem bezpieczeństwa komunikatem, że klucz nie jest przypisany do mojego użytkownika. Mogę wybrać drugi zarejestrowany klucz i wejść do narzędzi.

- Kategoria: Brak powiązania klucza z kontem.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-21`; work_blocked: `false`; review: `pending`.

## ACC-22 — accounts_access / medium

Nie widzę grupy archiwalnych raportów, bo system jawnie informuje o braku członkostwa w grupie dostępu. Osoba prowadząca projekt udostępnia mi potrzebne raporty pojedynczo, więc przygotowuję zestawienie.

- Kategoria: Brak członkostwa w grupie uprawnień.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `acc-22`; work_blocked: `false`; review: `pending`.

## ACC-23 — accounts_access / high

Podczas podpisywania listy przelewów system informuje, że moja rola nie pozwala zatwierdzać płatności. Jestem jedyną upoważnioną osobą na dyżurze i bez tej operacji nie wyślę dziś przelewów.

- Kategoria: Odmowa uprawnienia do zatwierdzania płatności.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-23`; work_blocked: `true`; review: `pending`.

## ACC-24 — accounts_access / high

Przy wejściu do repozytorium projektu dostaję komunikat, że moje członkostwo w organizacji wygasło. Muszę dziś przekazać poprawkę klientowi, nie mam kopii kodu ani innego uprawnionego konta.

- Kategoria: Wygasłe członkostwo warunkujące dostęp.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-24`; work_blocked: `true`; review: `pending`.

## ACC-25 — accounts_access / high

Moje konto administratora urządzeń zostało wyłączone, co potwierdza ekran logowania. Muszę skonfigurować dziś stanowisko nowego pracownika; inne konto nie ma tych uprawnień i nie ma zastępcy.

- Kategoria: Jawnie wyłączone konto uprzywilejowane.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-25`; work_blocked: `true`; review: `pending`.

## ACC-26 — accounts_access / high

System obsługi dokumentów żąda drugiego składnika, ale mój jedyny zarejestrowany klucz został zgubiony. Nie mam kodów awaryjnych ani innej metody i nie mogę wysłać wymaganej dzisiaj dokumentacji.

- Kategoria: Brak dostępnego składnika uwierzytelniania.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-26`; work_blocked: `true`; review: `pending`.

## ACC-27 — accounts_access / high

Po zmianie zakresu obowiązków odmówiono mi dostępu do folderu zamknięcia miesiąca z komunikatem o braku uprawnień. Potrzebuję tych dokumentów do dzisiejszego rozliczenia; nikt na zmianie nie może mi ich przekazać.

- Kategoria: Odmowa dostępu do wymaganego folderu.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-month-end-folder`; work_blocked: `true`; review: `pending`.

## ACC-28 — accounts_access / high

Ponownie zgłaszam utratę uprawnień do tego samego katalogu zamknięcia miesiąca. Nie mogę odczytać dokumentów do rozliczenia na dziś, a żadna dostępna osoba nie ma prawa udostępnić mi kopii.

- Kategoria: Ponowienie jawnego braku uprawnień do folderu.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `acc-month-end-folder`; work_blocked: `true`; review: `pending`.

## ACC-29 — accounts_access / critical

Wszyscy dyspozytorzy widzą przy logowaniu do systemu przewozów komunikat o odebraniu roli operatora. Nie możemy wydawać zleceń kierowcom, a żadne konto na tej zmianie nie ma dostępu zastępczego.

- Kategoria: Odebrana rola operatora u wielu użytkowników.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `acc-29`; work_blocked: `true`; review: `pending`.

## ACC-30 — accounts_access / critical

Od rana system uwierzytelniania odrzuca konta całego zespołu obsługi pacjentów jako nieaktywne. Rejestracja wizyt stoi dla wszystkich, a logowanie awaryjne również nie jest dopuszczone.

- Kategoria: Wspólna blokada aktywności kont.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `acc-30`; work_blocked: `true`; review: `pending`.

## HW-11 — hardware / low

Na obudowie służbowego laptopa pękła plastikowa zaślepka zawiasu. Ekran otwiera się stabilnie, przewody nie są odsłonięte i wykonuję wszystkie zadania bez ograniczeń.

- Kategoria: Uszkodzenie fizycznego elementu obudowy.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `hw-11`; work_blocked: `false`; review: `pending`.

## HW-12 — hardware / low

Pokrętło regulacji głośności na słuchawkach jest luźne, ale dźwięk i mikrofon działają. Ustawiam głośność w systemie i bez przeszkód prowadzę rozmowy.

- Kategoria: Mechaniczna wada elementu słuchawek.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `hw-12`; work_blocked: `false`; review: `pending`.

## HW-13 — hardware / low

Na klawiaturze zewnętrznej przestała świecić kontrolka Caps Lock. Same klawisze działają, stan widzę na ekranie i nie utrudnia to pisania dokumentów.

- Kategoria: Niesprawna kontrolka urządzenia.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `hw-13`; work_blocked: `false`; review: `pending`.

## HW-14 — hardware / low

Podstawka monitora nie trzyma wybranej wysokości i zsuwa się do najniższej pozycji. Na tej wysokości ekran jest dla mnie czytelny i mogę wykonywać wszystkie obowiązki.

- Kategoria: Mechanizm regulacji podstawki monitora.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `hw-14`; work_blocked: `false`; review: `pending`.

## HW-15 — hardware / medium

Czytnik kart w terminalu numer 4 nie reaguje także w jego własnym teście diagnostycznym. Przeniosłem obsługę na wolny terminal numer 5 i nadal przyjmuję klientów.

- Kategoria: Niesprawny czytnik potwierdzony testem urządzenia.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-terminal-4-reader`; work_blocked: `false`; review: `pending`.

## HW-16 — hardware / medium

Wracam do tego samego czytnika w terminalu 4: karty nie są wykrywane nawet w diagnostyce terminala. Korzystam z sąsiedniego stanowiska 5, więc klienci są obsługiwani.

- Kategoria: Powtórzenie niesprawności fizycznego czytnika.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-terminal-4-reader`; work_blocked: `false`; review: `pending`.

## HW-17 — hardware / medium

Jeden port USB w stacji dokującej nie rozpoznaje podłączonych urządzeń, niezależnie od przewodu. Pozostałe porty działają; przełożyłem do nich mysz i klawiaturę i mogę pracować.

- Kategoria: Niesprawność konkretnego portu urządzenia.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-17`; work_blocked: `false`; review: `pending`.

## HW-18 — hardware / medium

Akumulator terminala mobilnego nie utrzymuje zasilania i urządzenie gaśnie po odłączeniu ładowarki. Przy ladzie pracuję z podłączonym zasilaniem i mogę rejestrować wydania.

- Kategoria: Brak podtrzymania zasilania przez akumulator.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-18`; work_blocked: `false`; review: `pending`.

## HW-19 — hardware / medium

Mysz dwukrotnie rejestruje pojedyncze kliknięcie także na innym komputerze. Pożyczyłem sprawną mysz z zapasu i wykonuję zadania, ale moja wymaga wymiany.

- Kategoria: Objaw fizycznego urządzenia powtarza się na innym komputerze.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-19`; work_blocked: `false`; review: `pending`.

## HW-20 — hardware / medium

W skanerze dokumentów podajnik zatrzymuje kartki również przy kopiowaniu bez komputera. Mogę skanować pojedyncze strony z szyby i w ten sposób przekazuję dokumenty.

- Kategoria: Mechanizm podawania papieru działa nieprawidłowo.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-20`; work_blocked: `false`; review: `pending`.

## HW-21 — hardware / medium

Zewnętrzny dysk nie jest wykrywany na dwóch komputerach, a jego dioda nie świeci. Potrzebne pliki mam również na firmowym zasobie, więc pobieram je stamtąd i pracuję dalej.

- Kategoria: Brak reakcji urządzenia na różnych komputerach.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-21`; work_blocked: `false`; review: `pending`.

## HW-22 — hardware / medium

Wbudowany mikrofon laptopa trzeszczy także podczas lokalnego nagrania testowego. Podłączony zestaw słuchawkowy nagrywa czysto i używam go do wszystkich rozmów.

- Kategoria: Objaw mikrofonu występuje poza aplikacją rozmów.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `hw-22`; work_blocked: `false`; review: `pending`.

## HW-23 — hardware / high

Jedyny monitor przy stanowisku kontroli świeci podświetleniem, lecz nie wyświetla nawet własnego menu. Muszę dzisiaj przeprowadzić odbiór partii; nie mamy innego ekranu ani stanowiska do tej kontroli.

- Kategoria: Brak obrazu także w menu samego monitora.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-23`; work_blocked: `true`; review: `pending`.

## HW-24 — hardware / high

Drukarka etykiet przewozowych nie podaje papieru i zgłasza uszkodzenie mechanizmu także w teście z panelu. Dzisiejszych paczek nie można nadać bez tych etykiet, a drugiej drukarki ani wydruku zastępczego nie ma.

- Kategoria: Awaria mechanizmu drukarki potwierdzona bez aplikacji.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-24`; work_blocked: `true`; review: `pending`.

## HW-25 — hardware / high

Urządzenie do nanoszenia podpisu nie włącza się na żadnym z dostępnych portów. Muszę dzisiaj odebrać podpis klienta, procedura nie dopuszcza papieru i nie mamy zapasowego urządzenia.

- Kategoria: Fizyczne urządzenie nie uruchamia się.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-25`; work_blocked: `true`; review: `pending`.

## HW-26 — hardware / high

W komputerze do przygotowania prezentacji słychać stukanie dysku, a test sprzętowy zgłasza jego awarię i system się nie uruchamia. Potrzebne pliki są tylko tutaj; nie mam kopii ani innego sposobu przygotowania dzisiejszego pokazu.

- Kategoria: Awaria dysku wskazana przez test sprzętowy.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-26`; work_blocked: `true`; review: `pending`.

## HW-27 — hardware / high

Jedyny zasilacz terminala przy bramie załadunkowej ma urwany przewód, terminal jest rozładowany. Muszę teraz rejestrować samochody, ale nie ma drugiego zasilacza ani innego stanowiska z tą funkcją.

- Kategoria: Uszkodzony przewód zasilacza i brak zasilania terminala.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-loading-gate-charger`; work_blocked: `true`; review: `pending`.

## HW-28 — hardware / high

Zgłaszam ponownie ten sam zerwany kabel ładowarki terminala przy bramie. Urządzenie nie ma już baterii, więc nie wpiszę przyjeżdżających pojazdów; ładowarki zastępczej i innego stanowiska nie mamy.

- Kategoria: Powtórzenie uszkodzenia zasilacza terminala.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `hw-loading-gate-charger`; work_blocked: `true`; review: `pending`.

## HW-29 — hardware / critical

Centralny zasilacz awaryjny nie daje napięcia na wyjściu i pokazuje błąd modułu mocy także po teście własnym. Wyłączone są wszystkie stanowiska punktu obsługi, klienci nie mogą być przyjmowani i nie ma zasilania zastępczego.

- Kategoria: Usterka fizycznego modułu zasilania.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `hw-29`; work_blocked: `true`; review: `pending`.

## HW-30 — hardware / critical

Główny serwer rejestracji nie reaguje na przycisk zasilania, a obie jednostki zasilające zgłaszają czerwone kontrolki. Cały zespół nie może obsługiwać wizyt i nie ma uruchamialnego serwera zastępczego.

- Kategoria: Sprzętowe objawy braku zasilania serwera.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `hw-30`; work_blocked: `true`; review: `pending`.

## NET-11 — network / low

Po przejściu między pokojami telefon służbowy przez chwilę pokazuje brak sieci Wi-Fi, po czym sam się łączy. W tym czasie nie prowadzę rozmów ani zadań i nie tracę dostępu do narzędzi potrzebnych do pracy.

- Kategoria: Krótka przerwa podczas zmiany punktu dostępu.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `net-11`; work_blocked: `false`; review: `pending`.

## NET-12 — network / low

Sieć dla gości w poczekalni otwiera stronę powitalną z kilkusekundowym opóźnieniem. Służbowa sieć przy stanowiskach działa normalnie, opóźnienie nie dotyczy wykonywanej pracy.

- Kategoria: Opóźnienie nawiązywania dostępu do sieci gościnnej.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `net-12`; work_blocked: `false`; review: `pending`.

## NET-13 — network / low

Po podłączeniu przewodu ikona sieci zmienia stan na połączony dopiero po kilku sekundach. Później wszystkie usługi działają stabilnie, a oczekiwanie nie przerywa mi żadnego zadania.

- Kategoria: Opóźnienie ustanowienia połączenia przewodowego.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `net-13`; work_blocked: `false`; review: `pending`.

## NET-14 — network / low

Na tarasie biura firmowe Wi-Fi ma bardzo mały zasięg i strony ładują się wolno. To miejsce odpoczynku; w pomieszczeniach pracy mam pełny dostęp i realizuję wszystkie obowiązki.

- Kategoria: Słaby zasięg sieci w konkretnym obszarze.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `net-14`; work_blocked: `false`; review: `pending`.

## NET-15 — network / medium

W sali szkoleniowej C połączenie przewodowe jest rozłączane co kilka minut, także przy zwykłym otwieraniu stron. Przełączyłem komputer na Wi-Fi i szkolenie może trwać dalej.

- Kategoria: Powtarzające się zerwanie połączenia przewodowego.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-training-room-c`; work_blocked: `false`; review: `pending`.

## NET-16 — network / medium

To ponowne zgłoszenie zrywania kabla sieciowego w sali C: usługi przestają odpowiadać, po chwili wracają. Na bezprzewodowym połączeniu szkolenie działa bez przerw, więc obecnie z niego korzystamy.

- Kategoria: Ten sam problem stabilności połączenia w sali.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-training-room-c`; work_blocked: `false`; review: `pending`.

## NET-17 — network / medium

W biurze nie otwierają się żadne strony po nazwach, ale wejście na znany adres IP serwera działa. Po przełączeniu na dozwolony zapasowy resolver nazwy znów działają i obsługuję sprawy.

- Kategoria: Problem rozwiązywania nazw w połączeniu sieciowym.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-17`; work_blocked: `false`; review: `pending`.

## NET-18 — network / medium

W rozmowach przez firmowe łącze głos urywa się, a test pokazuje utratę pakietów także do innych usług. Po podłączeniu do łącza zapasowego mogę rozmawiać i obsługiwać klientów.

- Kategoria: Utrata pakietów dotyczy wielu usług.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-18`; work_blocked: `false`; review: `pending`.

## NET-19 — network / medium

Firmowa sieć bezprzewodowa nie przydziela mojemu laptopowi adresu; urządzenie pokazuje oczekiwanie na konfigurację sieci. Po podłączeniu przewodem dostaję połączenie i mogę pracować.

- Kategoria: Brak konfiguracji adresowej połączenia bezprzewodowego.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-19`; work_blocked: `false`; review: `pending`.

## NET-20 — network / medium

Po zalogowaniu do VPN połączenie znika przy wysyłaniu większego pliku, a to samo dzieje się z kilkoma usługami. Pliki przekazuję przez zatwierdzony portal zewnętrzny i zadanie jest wykonywane.

- Kategoria: Niestabilność połączenia VPN po uwierzytelnieniu.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-20`; work_blocked: `false`; review: `pending`.

## NET-21 — network / medium

Wynajęty pokój pracy nie ma działającego połączenia z firmową centralą, choć lokalne strony są osiągalne. Korzystam z zatwierdzonego łącza komórkowego i dzięki temu wykonuję obowiązki.

- Kategoria: Niedostępna trasa połączenia z centralą.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-21`; work_blocked: `false`; review: `pending`.

## NET-22 — network / medium

Po zmianie stanowiska połączenie przez gniazdo 18 jest bardzo wolne przy kopiowaniu i otwieraniu różnych usług. Przeniosłem się do wolnego biurka z innym gniazdem i praca przebiega normalnie.

- Kategoria: Ograniczona wydajność konkretnego połączenia sieciowego.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `net-22`; work_blocked: `false`; review: `pending`.

## NET-23 — network / high

Z mojego punktu obsługi nie można połączyć się z centralą, żądania do wszystkich jej usług kończą się przekroczeniem czasu. Muszę dzisiaj potwierdzić wydania, a nie ma łącza zapasowego ani możliwości przejścia na inne stanowisko.

- Kategoria: Brak łączności z wieloma usługami centrali.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-23`; work_blocked: `true`; review: `pending`.

## NET-24 — network / high

Na służbowym laptopie nie działa ani firmowa sieć przewodowa, ani bezprzewodowa; nie osiągam żadnego firmowego adresu. Muszę przeprowadzić dzisiaj rozmowę z klientem, telefon nie ma tutaj zasięgu i nie mam innego stanowiska.

- Kategoria: Brak dostępu do sieci przez różne połączenia.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-24`; work_blocked: `true`; review: `pending`.

## NET-25 — network / high

Połączenie do zdalnego pulpitu jest uwierzytelniane, ale ruch do serwera zatrzymuje się i kończy timeoutem, podobnie jak dostęp do innych usług w tej lokalizacji. Muszę zatwierdzić dzisiejszy import i nie mam innej drogi do serwera.

- Kategoria: Po uwierzytelnieniu brakuje łączności do lokalizacji.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-25`; work_blocked: `true`; review: `pending`.

## NET-26 — network / high

Łącze używane do transmisji dzisiejszego szkolenia traci pakiety i rozłącza także inne aplikacje. Nie mogę poprowadzić transmisji, a dostępne tu urządzenia nie obsługują żadnego innego połączenia.

- Kategoria: Utrata łączności obejmuje wiele aplikacji.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-26`; work_blocked: `true`; review: `pending`.

## NET-27 — network / high

Moje połączenie z firmą z placówki terenowej przestało odpowiadać; wszystkie usługi centrali mają timeout, choć logowanie do lokalnego urządzenia działa. Muszę dzisiaj wysłać protokół, a w tej lokalizacji nie ma alternatywnego łącza ani innego punktu dostępu.

- Kategoria: Wspólna utrata łączności do centrali z jednej placówki.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-field-office-uplink`; work_blocked: `true`; review: `pending`.

## NET-28 — network / high

Ponawiam sprawę niedostępnego połączenia placówki terenowej z centralą. Każda jej usługa przekracza czas odpowiedzi; dzisiejszy protokół czeka, a nie ma tutaj sieci zapasowej ani drugiego dostępu.

- Kategoria: Ten sam brak łączności z usługami centrali.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `net-field-office-uplink`; work_blocked: `true`; review: `pending`.

## NET-29 — network / critical

W całej firmie nazwy wewnętrznych systemów przestały się rozwiązywać, a znane adresy IP są osiągalne. Wszystkie zespoły utraciły dostęp do obsługi zamówień, zapasowy resolver również nie odpowiada i nie ma dopuszczonego obejścia.

- Kategoria: Wspólna awaria rozwiązywania nazw w sieci.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `net-29`; work_blocked: `true`; review: `pending`.

## NET-30 — network / critical

Obie trasy sieciowe między magazynem a centralą są niedostępne; każda usługa centralna kończy się timeoutem. Wszystkie zmiany w magazynie stoją, bo nie da się rejestrować wydań, i nie ma trzeciego łącza ani pracy offline.

- Kategoria: Brak łączności przez obie dostępne trasy.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `net-30`; work_blocked: `true`; review: `pending`.

## SW-11 — software / low

W programie do notatek po ostatniej aktualizacji tekst podpowiedzi nachodzi na ikonę. Po odsunięciu myszy podpowiedź znika, wszystkie funkcje działają i tworzę notatki normalnie.

- Kategoria: Błąd wyświetlania elementu programu.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `sw-11`; work_blocked: `false`; review: `pending`.

## SW-12 — software / low

Aplikacja pokazuje nazwę miesiąca po angielsku, chociaż wybrałem polski język. Daty są poprawne, rozumiem nazwy i mogę wykonywać wszystkie operacje.

- Kategoria: Niepoprawna lokalizacja interfejsu aplikacji.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `sw-12`; work_blocked: `false`; review: `pending`.

## SW-13 — software / low

W oknie pomocy programu odnośnik do spisu treści przewija stronę do złego nagłówka. Pozostałe funkcje są sprawne i tej pomocy nie potrzebuję do bieżących obowiązków.

- Kategoria: Nieprawidłowe działanie odnośnika w aplikacji.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `sw-13`; work_blocked: `false`; review: `pending`.

## SW-14 — software / low

Po ponownym uruchomieniu narzędzia wybrany kolor motywu wraca do domyślnego. Nie tracę ustawień potrzebnych do zadań ani dokumentów i pracuję bez przeszkód.

- Kategoria: Program nie zapamiętuje kosmetycznego ustawienia.
- Priorytet bazowy: Drobna uciążliwość bez ograniczenia wymaganych zadań.
- Grupa: `sw-14`; work_blocked: `false`; review: `pending`.

## SW-15 — software / medium

Eksport listy kontaktów do CSV w aplikacji sprzedażowej kończy się błędem programu. Mogę skopiować tabelę do arkusza i zapisać ją jako CSV, więc przekazuję listy w terminie.

- Kategoria: Awaria funkcji eksportu aplikacji.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-contacts-csv`; work_blocked: `false`; review: `pending`.

## SW-16 — software / medium

Ponownie zgłaszam ten sam błąd zapisu kontaktów do CSV: przycisk eksportu wyświetla wyjątek zamiast pliku. Kopiowanie tabeli do arkusza i zapis stamtąd nadal pozwala przygotować listę.

- Kategoria: Powtórzenie błędu eksportu kontaktów.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-contacts-csv`; work_blocked: `false`; review: `pending`.

## SW-17 — software / medium

Filtr dat w programie raportowym pokazuje pustą listę mimo istniejących rekordów. Wyłączam filtr i wybieram potrzebne wiersze z pełnej listy, dzięki czemu przygotowuję raport.

- Kategoria: Błąd filtrowania wyników w programie.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-17`; work_blocked: `false`; review: `pending`.

## SW-18 — software / medium

Program do faktur źle sortuje po numerze i przestawia dokumenty w losowej kolejności. Wyszukiwanie konkretnego numeru działa, dlatego nadal wystawiam i odnajduję faktury.

- Kategoria: Nieprawidłowa funkcja sortowania dokumentów.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-18`; work_blocked: `false`; review: `pending`.

## SW-19 — software / medium

Podgląd załącznika PDF w aplikacji pokazuje pustą stronę, ale pobrany plik otwiera się poprawnie w osobnym czytniku. Pobieram dokumenty i na tej podstawie obsługuję sprawy.

- Kategoria: Błąd podglądu pliku w aplikacji.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-19`; work_blocked: `false`; review: `pending`.

## SW-20 — software / medium

Przeciągnięcie załącznika do formularza zamyka okno z błędem programu. Dodanie tego samego pliku przez przycisk wyboru działa, więc mogę wysyłać wymagane formularze.

- Kategoria: Awaria jednej metody dodawania załącznika.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-20`; work_blocked: `false`; review: `pending`.

## SW-21 — software / medium

W programie zestawień suma kolumny nie aktualizuje się po zmianie wiersza. Ponowne otwarcie dokumentu przelicza ją prawidłowo; sprawdzam w ten sposób wartości i kończę zestawienia.

- Kategoria: Nieprawidłowe odświeżanie obliczeń w aplikacji.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-21`; work_blocked: `false`; review: `pending`.

## SW-22 — software / medium

Aplikacja do ewidencji czasu zawiesza się na ekranie zapisu, choć jej wersja przeglądarkowa działa. Wprowadzam godziny przez przeglądarkę i mogę rozliczać pracę.

- Kategoria: Zawieszenie konkretnej wersji aplikacji.
- Priorytet bazowy: Opis zawiera działające obejście pozwalające kontynuować pracę.
- Grupa: `sw-22`; work_blocked: `false`; review: `pending`.

## SW-23 — software / high

Program płacowy przy obliczeniu mojego zestawienia pokazuje błąd arytmetyczny i przerywa operację. Muszę dziś zamknąć wynagrodzenia, ale nie da się ich zatwierdzić ręcznie ani w innym narzędziu.

- Kategoria: Błąd obliczeń przerywa funkcję programu.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-23`; work_blocked: `true`; review: `pending`.

## SW-24 — software / high

Przy zapisaniu przygotowanej oferty aplikacja sprzedażowa stale wyświetla wyjątek i usuwa formularz. Muszę wysłać tę ofertę dzisiaj, a polityka firmy wymaga zapisu w tym systemie i nie ma alternatywnej wersji.

- Kategoria: Powtarzalny błąd zapisu formularza.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-24`; work_blocked: `true`; review: `pending`.

## SW-25 — software / high

Narzędzie importu danych zatrzymuje się na każdym pliku komunikatem o błędzie parsowania, również na własnym poprawnym pliku przykładowym. Muszę dziś wczytać dane klienta i nie istnieje import ręczny ani inne narzędzie.

- Kategoria: Awaria parsera w narzędziu importu.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-25`; work_blocked: `true`; review: `pending`.

## SW-26 — software / high

Aplikacja projektowa zamyka się podczas otwierania mojego wymaganego dokumentu, także z jego zachowanej kopii. Mam właściwe uprawnienia, lecz nie mogę przygotować dzisiejszej dokumentacji, a inny program nie obsługuje tego formatu.

- Kategoria: Zamknięcie aplikacji przy odczycie dokumentu.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-26`; work_blocked: `true`; review: `pending`.

## SW-27 — software / high

Publikowanie mojego grafiku w systemie dyżurów kończy się błędem programu mimo poprawnego sprawdzenia danych. Muszę udostępnić grafik na jutro, a system nie ma drugiego sposobu publikacji i eksport nie jest akceptowany.

- Kategoria: Awaria operacji publikacji po walidacji danych.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-roster-publication`; work_blocked: `true`; review: `pending`.

## SW-28 — software / high

To ponowienie sprawy tego samego grafiku: kontrola formularza przechodzi, lecz zatwierdzenie publikacji wyświetla wyjątek. Grafik na jutro nadal jest niedostępny; nie można go opublikować inną ścieżką ani zastąpić eksportem.

- Kategoria: Ten sam błąd publikowania grafiku.
- Priorytet bazowy: Ważne zadanie zgłaszającego jest zablokowane i nie ma dostępnego obejścia.
- Grupa: `sw-roster-publication`; work_blocked: `true`; review: `pending`.

## SW-29 — software / critical

Po aktualizacji aplikacji magazynowej zapis każdego wydania kończy się wyjątkiem dla wszystkich operatorów. Logowanie i sieć działają, ale cały magazyn nie może wydawać towaru i nie ma trybu offline ani systemu zastępczego.

- Kategoria: Awaria funkcji zapisu aplikacji u wszystkich operatorów.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `sw-29`; work_blocked: `true`; review: `pending`.

## SW-30 — software / critical

Program obsługi infolinii zamyka się na każdym stanowisku przy przyjęciu rozmowy, podczas gdy inne usługi sieciowe działają. Cały zespół nie może odbierać połączeń od klientów i nie mamy alternatywnej aplikacji ani przekierowania.

- Kategoria: Zamknięcie aplikacji wywoływane wspólną operacją.
- Priorytet bazowy: Niedostępna kluczowa usługa blokuje pracę wielu osób bez trybu zastępczego.
- Grupa: `sw-30`; work_blocked: `true`; review: `pending`.

---

# Końcowa partia pilotażu — 50 słabo opisanych zgłoszeń

Użytkownik zatwierdził również poprzednie 80 par. Wszystkie wcześniejsze 120 przykładów ma teraz status approved.
Nowe 50 propozycji poniżej pozostaje pending. Są wyłącznie zapytaniami do KNN z referencją 120; nie są przykładami referencyjnymi.
Puste etykiety (null) oznaczają niewystarczającą informację w opisie. Nie należy ich zgadywać ani zastępować medium.

## WEAK-01 — accounts_access / null

Konto zablokowane.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-02 — accounts_access / null

Nie mam uprawnień do folderu.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-03 — accounts_access / null

MFA nie dochodzi na telefon.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-04 — accounts_access / null

Hasło wygasło, nie mogę wejść.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-05 — accounts_access / null

Zabrali mi rolę w systemie.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-06 — accounts_access / null

Nie mogę zatwierdzić logowania na nowym telefonie.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-07 — accounts_access / low

Konto pokazuje dawny telefon. Pracuję normalnie.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Opis potwierdza możliwość normalnej pracy mimo uciążliwości.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-08 — accounts_access / medium

Brak uprawnień do raportów. Kolega wysyła mi pliki.

- Kategoria: Opis wskazuje konto, uprawnienie lub uwierzytelnianie.
- Priorytet bazowy: Opis zawiera dostępne działające obejście.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-09 — hardware / null

Urwał się klawisz.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-10 — hardware / null

Monitor ma pękniętą matrycę.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-11 — hardware / null

Wentylator ociera o obudowę.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-12 — hardware / null

Bateria jest spuchnięta.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-13 — hardware / null

Zasilacz iskrzy.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-14 — hardware / low

Pękła podstawka monitora. Ekran stoi stabilnie, pracuję.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Opis potwierdza możliwość normalnej pracy mimo uciążliwości.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-15 — hardware / medium

Mysz nie klika, pożyczona działa.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Opis zawiera dostępne działające obejście.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-16 — hardware / high

Jedyny skaner nie włącza się. Paczki stoją, brak zapasowego.

- Kategoria: Opis zawiera fizyczny objaw dotyczący urządzenia.
- Priorytet bazowy: Ważne zadanie jest zablokowane bez opisanej dostępnej alternatywy.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-17 — network / null

Wi-Fi ciągle zrywa.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-18 — network / null

VPN uwierzytelnia, potem timeout.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-19 — network / null

Adresy IP działają, nazwy nie.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-20 — network / null

Pakiety giną na całym łączu.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-21 — network / medium

Kabel sieciowy nie łączy. Pracuję przez Wi-Fi.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Opis zawiera dostępne działające obejście.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-22 — network / high

Bez internetu nie wyślę dziś rozliczenia. Nie mam innego łącza.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Ważne zadanie jest zablokowane bez opisanej dostępnej alternatywy.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-23 — network / critical

Cały oddział bez sieci. Wszyscy nie mogą przyjmować zamówień, łącza zapasowego brak.

- Kategoria: Opis wskazuje utratę lub nieprawidłowe działanie łączności.
- Priorytet bazowy: Kluczowa obsługa wielu osób jest zablokowana bez zastępstwa.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-24 — software / null

Program zamyka się przy zapisie.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-25 — software / null

Eksport CSV rzuca wyjątek.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-26 — software / null

Kalendarz nie odświeża wpisów.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-27 — software / null

Aplikacja zawiesza się przy otwieraniu PDF.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-28 — software / high

Program do podpisu nie startuje. Dziś umowa, tylko ten program jest dopuszczony.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Ważne zadanie jest zablokowane bez opisanej dostępnej alternatywy.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-29 — software / critical

Po aktualizacji program sprzedaży pada wszystkim. Nie da się przyjąć żadnego zamówienia, brak zastępstwa.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Kluczowa obsługa wielu osób jest zablokowana bez zastępstwa.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-30 — software / null

Nie zapisuje ustawień widoku.

- Kategoria: Opis wskazuje nieprawidłowe działanie funkcji programu.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-31 — null / null

Nie działa.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-32 — null / null

Znowu to samo.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-33 — null / null

Pilne!!!

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-34 — null / null

Wszystko się sypie.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-35 — null / null

Strasznie wolno.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-36 — null / null

Nie mogę wejść.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-37 — null / null

Błąd od rana.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-38 — null / null

Nic nie idzie zrobić.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-39 — null / null

Dalej lipa po restarcie.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-40 — null / null

To coś ciągle znika.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-41 — null / null

Jak klikam, jest źle.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-42 — null / null

Wczoraj było dobrze.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-43 — null / null

Mam ten sam problem co inni.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-44 — null / null

Zobaczcie to proszę.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-45 — null / null

Wywala mnie.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-46 — null / null

Nie ma tego, co trzeba.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-47 — null / null

Kręci się i kręci.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-48 — null / null

Cały czas czerwone.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-49 — null / null

Nie przechodzi dalej.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-50 — null / null

Pomocy, nie wiem co się stało.

- Kategoria: Brak objawów pozwalających odróżnić kategorię; wymagane doprecyzowanie.
- Priorytet bazowy: Brak wystarczających danych o wpływie i obejściu; nie przypisujemy wzorcowego priorytetu.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.
