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
