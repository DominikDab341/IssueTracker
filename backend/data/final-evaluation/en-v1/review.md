# Wszystkie przypadki testu EN v1

Cały zbiór: 100 przypadków; zatwierdzone: 100; oczekujące: 0.

Etykiety poniżej są propozycjami asystenta, nie przewidywaniami klasyfikatora.
Przegląd obejmuje treść, kategorię, priorytet bazowy i odrębność od pilotażu.
Zatwierdzenia dotyczą wyłącznie wskazanych ID; nie obejmują nowo dopisanych przypadków.
Wszystkie przypadki mają reference_eligible=false i pozostają poza treningiem.
Układ: 70 pełniejszych opisów oraz 30 słabych. Null = brak informacji do ustalenia etykiety, nie klasa unknown.
Zatwierdzenie słabego opisu może oznaczać potwierdzenie, że kategorii lub priorytetu nie da się ustalić.

[Protokół i historia przeglądu](README.md)

## FINAL-EN-001

The API accepts the service account's token, but rejects the inventory upload with 'required scope inventory.write is missing'. Downloading the inventory still works. I have to publish tonight's stock correction before dispatch starts; this upload is the only supported route and nobody available can issue a token with that scope.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Jawna odmowa uprawnienia w zakresie tokenu, mimo poprawnego uwierzytelnienia.
Priorytet: Ważna operacja jest zablokowana, a opis wyklucza dostępne obejście; nie podano awarii blokującej wiele osób.

Odrębność: Nowy incydent dotyczący zakresu tokenu konta usługowego, a nie parafraza istniejącej sprawy o folder, rolę użytkownika lub logowanie do VPN.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-002

Signing into the engineering wiki from my loan laptop is refused with 'access policy requires a managed device'. My account opens the same pages through the approved virtual desktop. I can finish the design review there, although switching between the virtual desktop and my local drawings is cumbersome.

Jakość opisu: **complete**.

Propozycja: **accounts_access / medium**.

Kategoria: Dostęp odrzuca jawna polityka warunkowa konta i urządzenia, nie zerwanie połączenia.
Priorytet: Praca jest utrudniona, ale działa zatwierdzony pulpit wirtualny.

Odrębność: Nowy przypadek warunkowego dostępu zależnego od zarządzania urządzeniem, z odrębnym obejściem.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-003

The display on the desk's USB power meter has become very faint. Its physical digits are difficult to read even with nothing connected. The dock and all attached equipment work normally; I only use that meter out of curiosity and none of my duties needs its readings.

Jakość opisu: **complete**.

Propozycja: **hardware / low**.

Kategoria: Objaw dotyczy fizycznego wyświetlacza osobnego przyrządu, niezależnie od aplikacji.
Priorytet: Drobna wada nie ogranicza żadnego zadania służbowego.

Odrębność: Nowy fizyczny przyrząd pomiarowy; nie dotyczy pikseli monitora ani kontrolki klawiatury z pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-004

The cooling unit for the server cabinet has seized: its fans do not turn and the hardware panel reports an over-temperature shutdown. The hosts have powered themselves off. Every operator in the distribution centre has lost the picking service, so no orders can be released, and the standby cabinet is unavailable.

Jakość opisu: **complete**.

Propozycja: **hardware / critical**.

Kategoria: Opisano zatrzymane wentylatory i ochronne wyłączenie sprzętu z powodu temperatury.
Priorytet: Niedostępna kluczowa usługa zatrzymała pracę całego zespołu; brak dostępnego zastępstwa.

Odrębność: Nowa awaria chłodzenia szafy, odrębna od zasilacza, UPS i macierzy z pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-005

Connections using IPv6 stall in several unrelated applications on the office link, whereas their IPv4 connections complete. IT gave me an approved IPv4-only proxy, and the vendor portals work through it. I can continue checking deliveries, but I have to launch a separate browser for those portals.

Jakość opisu: **complete**.

Propozycja: **network / medium**.

Kategoria: Wspólny problem transmisji IPv6 w niezależnych aplikacjach przy działającym IPv4.
Priorytet: Utrudnienie ma działające, zatwierdzone obejście przez proxy.

Odrębność: Nowy przypadek różnicy osiągalności IPv6/IPv4, nie parafraza utraty Wi-Fi, DNS lub tunelu VPN.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-006

My test workstation can reach everything on its own subnet, but connections to all three instruments on the lab subnet time out. Those instruments answer from a workstation already on their subnet; traffic from mine stops at the gateway. I need to run the acceptance tests from this licensed workstation today, and there is no approved alternative connection or offline procedure.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Zawodzi komunikacja między podsieciami do kilku urządzeń, które są lokalnie osiągalne.
Priorytet: Ważne testy jednego stanowiska są zablokowane bez dopuszczonego obejścia.

Odrębność: Nowy incydent komunikacji między podsieciami laboratorium; nie ten sam incydent co niedostępne łącza do centrali.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-007

The meeting recorder puts the wrong day of the week in suggested filenames, although the numeric date is correct. I name each recording myself before saving it. Recording, playback and saving all work, and this has not delayed or complicated any of my tasks.

Jakość opisu: **complete**.

Propozycja: **software / low**.

Kategoria: Program generuje niepoprawną część proponowanej nazwy pliku.
Priorytet: Drobna nieprawidłowość nie utrudnia pracy; ręczne nazywanie było normalnym sposobem pracy.

Odrębność: Nowy błąd generowania nazwy nagrania; nie parafraza wyglądu ikon, sortowania list ani awarii eksportu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-008

The capacity planner now assigns the same loading bay to every truck in a time slot, even when the dispatchers enter different available bays. It saves these conflicting allocations without an error. All dispatchers have had to stop releasing loading instructions because the output is unusable; this is our only authorised allocation system and there is no manual fallback.

Jakość opisu: **complete**.

Propozycja: **software / critical**.

Kategoria: Aplikacja zapisuje błędny wynik alokacji mimo różnych poprawnych danych wejściowych.
Priorytet: Błędne działanie kluczowej usługi zablokowało pracę całego zespołu bez zastępstwa.

Odrębność: Nowy błąd logiczny przydzielania zasobu, odrębny od awarii procesu i błędów zapisu zamówień w pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:23:34+00:00.
Jawne zatwierdzenie pierwszej próbki w rozmowie: „Akceptuj to”. Bez zmian treści i etykiet.

## FINAL-EN-009

My supplier guest account is already active and opens every project I need. Its original invitation still appears under pending invitations in our access portal. There is nothing left for me to accept and the old entry has no effect on my work; please remove that obsolete invitation when convenient.

Jakość opisu: **complete**.

Propozycja: **accounts_access / low**.

Kategoria: Zgłoszenie dotyczy stanu zaproszenia konta gościa przy poprawnym dostępie.
Priorytet: Nieaktualny wpis nie utrudnia pracy ani uprawnień.

Odrębność: Porządkowanie zaproszenia gościa, odrębne od nazw kont i przypisania do zespołu w pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-011

A completed contractor engagement remains in my account's list of expired access packages. It is clearly marked expired and grants no access. My current packages are active and all my tasks work normally. Could the obsolete package be archived from my account history view?

Jakość opisu: **complete**.

Propozycja: **accounts_access / low**.

Kategoria: Historia wygasłego pakietu uprawnień dotyczy konta i jego dostępu.
Priorytet: Wpis jest informacyjny, nie daje dostępu i nie wpływa na obowiązki.

Odrębność: Historia wygasłego pakietu kontraktora, nie próba korzystania z aktywnej roli projektu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-012

The access system says my temporary research entitlement is awaiting an approver who has left the team. I can do the analysis with the same authorised dataset in the department's supervised workspace, but I have to reserve a session each morning instead of opening it at my own desk.

Jakość opisu: **complete**.

Propozycja: **accounts_access / medium**.

Kategoria: Wstrzymane nadanie uprawnienia z powodu ścieżki zatwierdzania dostępu.
Priorytet: Dostępna jest legalna alternatywa, lecz wymaga codziennej rezerwacji.

Odrębność: Nowy incydent procesu zatwierdzania czasowego uprawnienia do zbioru badawczego.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-013

My dashboard role no longer includes permission to download the management summary: the download action explicitly reports 'report.download denied'. I can still use the authorised scheduled delivery of that same summary to my mailbox. The daily report goes out, but waiting for the scheduled copy makes my preparation slower.

Jakość opisu: **complete**.

Propozycja: **accounts_access / medium**.

Kategoria: Operacja jest jawnie zabroniona przez brak konkretnego uprawnienia.
Priorytet: Zadanie da się ukończyć dzięki działającej dostawie harmonogramowej.

Odrębność: Uprawnienie pobierania gotowego podsumowania i niezależna dostawa mailowa, nie błąd eksportu aplikacji.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-016

The lab upload client presents its machine certificate, but the authentication gateway rejects it as an expired machine identity. The instrument still measures correctly. I must deliver the certified calibration record this afternoon, and the gateway permits neither password authentication nor an upload from another computer. No one available can renew that identity.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Bramka odrzuca wygasłe poświadczenie tożsamości maszyny.
Priorytet: Wymagana dostawa dokumentacji jest zablokowana bez dostępnej alternatywy.

Odrębność: Nowe uwierzytelnienie certyfikatem urządzenia, odrębne od zakresu tokenu w 001.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-017

I can authenticate to the encryption-key vault, but retrieving the archive key returns 'principal not permitted to use this key'. I am the engineer assigned to restore one client's archived drawings today. Without that key the restore cannot proceed, and there is no other authorised key holder or unencrypted copy available.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Jawna odmowa uprawnienia do klucza po poprawnym uwierzytelnieniu.
Priorytet: Ważne odtworzenie danych jednego klienta jest zablokowane bez obejścia.

Odrębność: Nowe uprawnienie do użycia klucza szyfrującego, nie brak dostępu do folderu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-020

Since the central federation certificate rollover, every registrar receives 'identity assertion signature is not trusted' from the sign-in gateway. The identity team confirms that the new signing identity has not been authorised by the registry service. Registration is stopped across all our offices, and local or emergency accounts are not supported.

Jakość opisu: **complete**.

Propozycja: **accounts_access / critical**.

Kategoria: Jawnie niezaufana tożsamość podpisująca asercję blokuje uwierzytelnianie.
Priorytet: Kluczowa usługa rejestracji jest niedostępna dla wielu biur bez awaryjnego logowania.

Odrębność: Nowy incydent zaufania podpisu federacji po rotacji, nie wyłączenie kont zespołu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-021

Every operator in the certificate-issuing team can sign in, but the key service refuses each request with 'issuance group is denied signing-key use'. No certificates can be issued to customers anywhere in the team. The previous group was removed during an access-policy change and no alternate signing identity or offline issuance is available.

Jakość opisu: **complete**.

Propozycja: **accounts_access / critical**.

Kategoria: Jawna odmowa uprawnienia całej grupie do klucza podpisującego.
Priorytet: Cały zespół nie może realizować podstawowej usługi, bez alternatywnego trybu.

Odrębność: Nowy zbiorowy brak uprawnienia do klucza usługi wydawania certyfikatów, bez awarii logowania.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-023

There is a shallow scratch on the plastic bezel outside the touchscreen of the reception kiosk. The glass is intact, the scratch does not cover the display, and touch input works over the entire screen. Visitor registration continues exactly as before; the mark is cosmetic.

Jakość opisu: **complete**.

Propozycja: **hardware / low**.

Kategoria: Kosmetyczne uszkodzenie obudowy fizycznego kiosku.
Priorytet: Rejestracja i dotyk działają bez ograniczeń.

Odrębność: Nowy fizyczny bezel kiosku, nie wada obrazu monitora lub pęknięcie zawiasu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-026

A strip of the pen display has stopped detecting the stylus, including in its built-in diagnostic grid. The desktop mouse still controls the whole application and I can finish the drawing with it. Freehand annotations are much slower that way, but the file can be delivered.

Jakość opisu: **complete**.

Propozycja: **hardware / medium**.

Kategoria: Martwy obszar wejścia jest widoczny w diagnostyce sprzętu.
Priorytet: Mysz umożliwia ukończenie pracy kosztem wydajności.

Odrębność: Nowy częściowy brak detekcji rysika, nie awaria klawiszy lub mikrofonu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-027

Our receipt printer produces very pale lines even on its own self-test after a fresh roll is loaded. The engineer's diagnostic identifies a worn thermal head. I can issue acceptable receipts on the spare unit at the end of the counter, but walking to it for every transaction is slowing service.

Jakość opisu: **complete**.

Propozycja: **hardware / medium**.

Kategoria: Potwierdzone zużycie głowicy termicznej i wada testu bez komputera.
Priorytet: Zapasowa drukarka pozwala obsługiwać transakcje z dodatkowym nakładem czasu.

Odrębność: Nowy fizyczny problem jakości nadruku, nie mechanizm papieru ani błąd drukowania w aplikacji.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-028

The workstation's hardware setup reports a depleted real-time-clock battery and loses its clock settings after power is disconnected. Our approved start-up checklist lets me set the time manually, after which the workstation and required tools work correctly. I can complete my work, but this extra setup is needed each morning.

Jakość opisu: **complete**.

Propozycja: **hardware / medium**.

Kategoria: Diagnostyka wskazuje baterię zegara sprzętowego i utratę ustawień po odłączeniu zasilania.
Priorytet: Zatwierdzone ustawienie czasu przy starcie przywraca normalną pracę.

Odrębność: Nowa bateria RTC, odrębna od rozładowanego akumulatora terminala i awarii ładowarki.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-031

The archival tape drive has a cartridge jammed in its loading mechanism; its front-panel eject test ends with a mechanical error. I must restore a specific legal archive for today's review. This is the only drive that can read those tapes, and there is no disk copy or replacement drive available.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Mechanizm ładowania napędu taśmowego zgłasza błąd bez udziału aplikacji.
Priorytet: Ważne odtworzenie archiwum jest niemożliwe bez sprzętu zastępczego lub kopii.

Odrębność: Nowy mechanizm napędu taśmowego, nie uszkodzony dysk komputera lub niedostępna macierz.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-032

The workstation's pre-boot hardware diagnostics reports an internal TPM failure. The encrypted engineering volume therefore stays locked even though my credentials are valid. I have to finish the controlled design on that volume today; the recovery material is unavailable and the file is not held on any other device.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Awarię modułu sprzętowego potwierdza diagnostyka przed startem systemu.
Priorytet: Wymagana dokumentacja jest niedostępna bez klucza odzyskiwania i kopii.

Odrębność: Nowy potwierdzony błąd TPM, odrębny od odmowy użycia klucza przez uprawnienia konta.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-033

The contactless encoder at my desk cannot write a badge and reports an antenna-coil fault in its own test. The booking software still works, but I need to issue the configured access badge for a technician's visit today. Temporary paper passes are not allowed for this visit, and no other encoder is available on site.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Samodzielny test wskazuje fizyczną usterkę cewki enkodera.
Priorytet: Ważne wydanie identyfikatora nie ma dopuszczonej alternatywy.

Odrębność: Nowe urządzenie zapisujące identyfikatory, nie czytnik kart terminala ani program uprawnień.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-034

A storage-controller diagnostic reports failed cache protection and has put the production database volumes into hardware-enforced read-only mode. Every checkout desk can view items but cannot complete a sale. The standby controller is also unavailable, and there is no alternate checkout service, so the entire store has stopped selling.

Jakość opisu: **complete**.

Propozycja: **hardware / critical**.

Kategoria: Potwierdzona usterka kontrolera sprzętowo blokuje zapis na wolumenach.
Priorytet: Kluczowa usługa sprzedaży zatrzymała wszystkie stanowiska bez zastępstwa.

Odrębność: Nowa awaria ochrony cache i tryb tylko do odczytu, nie brak zasilania macierzy.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-036

The desk link negotiates at 100 Mbps rather than the 1 Gbps shown for neighbouring desks. It is stable, and our measured file transfers and calls meet all of my work requirements. No task is delayed or unavailable; please check the negotiated rate when there is time.

Jakość opisu: **complete**.

Propozycja: **network / low**.

Kategoria: Zgłoszenie dotyczy parametrów zestawionego łącza sieciowego.
Priorytet: Opis wprost wskazuje brak ograniczeń i opóźnień pracy.

Odrębność: Nowa obserwacja negocjacji prędkości bez wpływu na zadania, nie wolny transfer wymagający przeprowadzki.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-037

The discovery list on the office network advertises the same meeting display twice under two network names. Either entry reaches the same display and screen sharing works normally. I do not lose any time or functionality; could the duplicate network advertisement be cleaned up during maintenance?

Jakość opisu: **complete**.

Propozycja: **network / low**.

Kategoria: Powtarza się ogłoszenie usługi w sieci przy sprawnej komunikacji z urządzeniem.
Priorytet: Duplikat informacyjny nie utrudnia korzystania z usługi.

Odrębność: Nowe powielone ogłoszenie wykrywania usługi, nie błąd listy dokumentów aplikacji.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-040

The site's web gateway sends requests back to the same proxy repeatedly, and several browsers report a proxy loop for unrelated external sites. IT's approved bypass profile reaches those sites correctly. I can process the supplier requests using that profile, although I have to switch profiles for internal sites.

Jakość opisu: **complete**.

Propozycja: **network / medium**.

Kategoria: Wspólny problem trasy przez pośredniczącą bramkę występuje w wielu przeglądarkach.
Priorytet: Zatwierdzony profil obejścia pozwala realizować zadania z dodatkowym przełączaniem.

Odrębność: Nowa pętla proxy, odrębna od różnicy IPv6/IPv4 i rozwiązywania nazw DNS.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-041

The link to the rendering cluster drops large network frames, while small probes and the same transfer over the approved lower-MTU profile succeed. I can send the assets with that profile and the jobs run, but I must apply it separately for each connection. Authentication and the remote application are working.

Jakość opisu: **complete**.

Propozycja: **network / medium**.

Kategoria: Problem transmisji zależy od wielkości ramek i ustawienia MTU, bez błędu aplikacji.
Priorytet: Działa zatwierdzony profil przesyłania, choć wymaga ręcznej obsługi połączeń.

Odrębność: Nowy incydent MTU na ścieżce do klastra, nie zrywany tunel VPN z pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-044

Traffic from our secure workstation loops between two routers instead of reaching the external evidence portal; the trace repeats the same two hops until it expires. The portal is reachable from its provider's network. I must submit today's evidence bundle from this workstation, and the rules prohibit another connection or device for that submission.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Zaobserwowana pętla routingu uniemożliwia dotarcie do celu.
Priorytet: Ważna terminowa wysyłka nie ma dopuszczonej alternatywnej ścieżki.

Odrębność: Nowa pętla pomiędzy routerami do konkretnego portalu, nie niedostępne wszystkie usługi centrali.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-045

The supplier's IPv6-only endpoint has no reachable route from our testing network; traces end at the border router. Their service is up and our local services work. I need to complete the required interoperability test today, but the approved test device cannot use a tunnel, an IPv4 substitute or another network.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Brak trasy do sieci docelowej IPv6, bez objawu błędu aplikacji lub uwierzytelnienia.
Priorytet: Ważny test nie może zostać wykonany inną dozwoloną drogą.

Odrębność: Nowy endpoint wyłącznie IPv6 bez obejścia, odrębny incydent od utrudnienia kilku aplikacji w 005.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-046

The market-data multicast feed has stopped reaching every dealing desk. The network team sees the feed arrive at the edge but no multicast packets leave the core towards the desks; sign-in and ordinary websites still work. All traders have stopped accepting orders because live prices are required, and the backup feed uses the same failed route.

Jakość opisu: **complete**.

Propozycja: **network / critical**.

Kategoria: Kluczowy strumień nie jest przekazywany przez sieć, mimo działającego logowania i WWW.
Priorytet: Brak wymaganych danych blokuje wszystkich traderów, bez niezależnej ścieżki zapasowej.

Odrębność: Nowa zbiorowa awaria routingu multicastu, nie całkowity brak Internetu lub DNS.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-047

A broadcast storm is saturating the office switches: their port counters rise continuously and packets to every local business service are being dropped. All departments in this building have had to stop handling work. The incident team has not yet isolated the loop, and no separate working network or offline process is available.

Jakość opisu: **complete**.

Propozycja: **network / critical**.

Kategoria: Masowy ruch rozgłoszeniowy przeciąża przełączniki i powoduje utratę transmisji.
Priorytet: Zablokowane są wszystkie działy budynku i nie ma alternatywnego trybu pracy.

Odrębność: Nowa burza rozgłoszeniowa w LAN, nie awaria połączenia oddziału z centralą.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-049

When I move the pointer out of a row in the asset viewer, its hover highlight sometimes stays on until the next click. The row's data remains readable and selecting, editing and saving work correctly. This visual residue has not delayed my work or changed any data.

Jakość opisu: **complete**.

Propozycja: **software / low**.

Kategoria: Błąd stanu wizualnego wiersza dotyczy działania interfejsu programu.
Priorytet: Wada wizualna nie ogranicza operacji ani tempa pracy.

Odrębność: Nowy stan podświetlenia po wyjściu kursora, nie rozmyte ikony i nie sortowanie dokumentów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-052

The case editor's autosave restores the previous draft over my latest text. The reproducible issue stops when I disable autosave, and manual Save keeps all changes correctly. I can complete the cases with autosave off, but I must remember to save after every edit until the function is fixed.

Jakość opisu: **complete**.

Propozycja: **software / medium**.

Kategoria: Funkcja automatycznego zapisu aplikacji przywraca niewłaściwą wersję roboczą.
Priorytet: Ręczny zapis z wyłączoną wadliwą funkcją jest działającym obejściem.

Odrębność: Nowa nieprawidłowa wersja autosave, nie zamykanie formularza przy zapisie.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-053

The video editor shifts imported subtitles two seconds late even though the source subtitle file has the right times. Applying a minus-two-second offset in the editor produces a correct preview and export. I can publish the training videos, but each import now needs that extra adjustment and check.

Jakość opisu: **complete**.

Propozycja: **software / medium**.

Kategoria: Aplikacja błędnie interpretuje czas importowanych napisów.
Priorytet: Działająca korekta przesunięcia umożliwia wykonanie zadania.

Odrębność: Nowy błąd synchronizacji napisów przy poprawnym pliku źródłowym, nie błąd eksportu PDF.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-054

The bulk-renaming utility skips filenames containing accented characters and shows an internal exception. The same names can be assigned correctly through the operating system's normal Rename action. I can finish organising the project files individually, but doing them one at a time is considerably slower than the bulk operation.

Jakość opisu: **complete**.

Propozycja: **software / medium**.

Kategoria: Jedna funkcja programu zgłasza wyjątek dla poprawnych nazw Unicode.
Priorytet: Ręczna operacja systemowa umożliwia ukończenie pracy kosztem czasu.

Odrębność: Nowe zbiorcze przemianowanie plików i obsługa znaków, odrębne od importu danych w pilotażu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-057

The audit extractor converts every event time to local time but still marks the output as UTC. The source events and workstation clock are correct. I must provide a certified UTC event sequence today, and the required extractor has no timezone override; manual edits and exports from other tools are not accepted.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Program błędnie przekształca i oznacza strefę czasową danych wyjściowych.
Priorytet: Ważna wymagana sekwencja zdarzeń nie może być poprawnie dostarczona dozwoloną metodą.

Odrębność: Nowy błąd konwersji stref w ekstraktorze, nie brak sieciowego czasu ani bateria RTC.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-058

The packaging solver rejects a valid container as over capacity even when its own detail view shows the load below the limit. The issue reproduces with the vendor's valid sample and access permissions are fine. I must approve this customer's packing plan today, but approval requires the solver and there is no manual or alternative planning path.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Sprzeczne wyniki walidacji programu występują także na poprawnej próbce producenta.
Priorytet: Ważny plan jednego klienta nie może zostać zatwierdzony bez działającej funkcji.

Odrębność: Nowy błąd warunku pojemności solvera, nie duplikowanie przydziałów zatok z 008.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-059

The release-manifest tool replaces non-ASCII characters in component names with question marks, so its signed manifest no longer matches the unchanged package. This occurs with the vendor's test package too. I must deliver this multilingual release today; the receiving system requires that signed manifest and there is no supported alternate generator or editing step.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Generator manifestu błędnie koduje nazwy komponentów przy poprawnym pakiecie.
Priorytet: Ważne wydanie jest zablokowane przez wymagany format bez alternatywnego generatora.

Odrębność: Nowa utrata znaków przy tworzeniu podpisanego manifestu, nie odmowa uprawnienia do publikacji tagu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-060

After the scheduling engine's calendar update, it treats every future date as a closed day, including dates marked open in its own calendar. All hospital scheduling staff are unable to book any procedure. Sign-in and other services work, but this is the only authorised booking engine and there is no emergency or paper scheduling mode.

Jakość opisu: **complete**.

Propozycja: **software / critical**.

Kategoria: Silnik aplikacji błędnie interpretuje wszystkie daty mimo poprawnego kalendarza wejściowego.
Priorytet: Kluczowa usługa planowania zabiegów jest zablokowana dla całego zespołu bez trybu zastępczego.

Odrębność: Nowy błąd semantyki dni roboczych, odrębny od zawieszania aplikacji i błędnego przypisania zasobów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-061

The shared notebook opens, but adding a section says 'your role is view-only'.

Jakość opisu: **weak**.

Propozycja: **accounts_access / nieustalalny priorytet**.

Kategoria: Jawna odmowa uprawnienia zapisu pozwala określić kategorię.
Priorytet: Nie opisano wpływu na pracę, pilności zadania ani dostępnego obejścia.

Odrębność: Nowy krótki incydent uprawnienia do sekcji wspólnego notatnika.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na obowiązki i informacji o obejściu; priorytet nieustalalny.
Zatwierdzone etykiety: **accounts_access / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na obowiązki i informacji o obejściu; priorytet nieustalalny.

## FINAL-EN-062

Signing into the booking dashboard says my one-time code has already been used.

Jakość opisu: **weak**.

Propozycja: **accounts_access / nieustalalny priorytet**.

Kategoria: Odrzucenie jednorazowego kodu dotyczy uwierzytelniania.
Priorytet: Nie wiadomo, czy można uzyskać nowy kod ani jakie zadania blokuje problem.

Odrębność: Nowy incydent ponownego użycia kodu jednorazowego, nie brak SMS na telefonie.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak danych o skutkach i dostępnych innych metodach dostępu.
Zatwierdzone etykiety: **accounts_access / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak danych o skutkach i dostępnych innych metodach dostępu.

## FINAL-EN-063

The cooling fins on the docking brick are bent and a piece of its casing is loose.

Jakość opisu: **weak**.

Propozycja: **hardware / nieustalalny priorytet**.

Kategoria: Wprost opisano fizyczne uszkodzenie urządzenia.
Priorytet: Nie wiadomo, czy urządzenie działa i czy ogranicza obowiązki.

Odrębność: Nowy niepełny opis uszkodzonej obudowy i żeber stacji dokującej.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na działanie i pracę oraz informacji o urządzeniu zastępczym.
Zatwierdzone etykiety: **hardware / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na działanie i pracę oraz informacji o urządzeniu zastępczym.

## FINAL-EN-064

The document scanner's lid has snapped at the hinge. That's all I can tell so far.

Jakość opisu: **weak**.

Propozycja: **hardware / nieustalalny priorytet**.

Kategoria: Złamany zawias pokrywy skanera jest objawem sprzętowym.
Priorytet: Nie opisano zadania, możliwości dalszego skanowania ani zastępstwa.

Odrębność: Nowa pokrywa skanera, odrębna od obudowy zawiasu laptopa w pilotażu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak informacji o możliwości dalszej pracy i obejściu.
Zatwierdzone etykiety: **hardware / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak informacji o możliwości dalszej pracy i obejściu.

## FINAL-EN-065

Two PCs report an address conflict. Both have been given the same IPv4 address.

Jakość opisu: **weak**.

Propozycja: **network / nieustalalny priorytet**.

Kategoria: Konflikt adresów dwóch urządzeń dotyczy konfiguracji komunikacji sieciowej.
Priorytet: Nie podano, czy komunikacja jest zablokowana ani jakie są skutki dla zadań.

Odrębność: Nowy konflikt adresów, odrębny od braku przydzielenia adresu w pilotażu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na pracę i możliwości zmiany adresacji lub użycia innego stanowiska.
Zatwierdzone etykiety: **network / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na pracę i możliwości zmiany adresacji lub użycia innego stanowiska.

## FINAL-EN-066

Packets arrive out of order on the link between the media encoder and receiver. No other details yet.

Jakość opisu: **weak**.

Propozycja: **network / nieustalalny priorytet**.

Kategoria: Opis dotyczy kolejności pakietów na połączeniu sieciowym.
Priorytet: Nie wiadomo, czy odbiornik kompensuje zmianę kolejności i czy zadanie jest utrudnione.

Odrębność: Nowe niepełne zgłoszenie zmiany kolejności pakietów, nie gubienia połączenia.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak skutków dla jakości usługi, zadań i dostępnych obejść.
Zatwierdzone etykiety: **network / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak skutków dla jakości usługi, zadań i dostępnych obejść.

## FINAL-EN-067

The image viewer rotates a picture twice when I click Rotate once.

Jakość opisu: **weak**.

Propozycja: **software / nieustalalny priorytet**.

Kategoria: Jedno wywołanie funkcji programu daje niepoprawny wynik.
Priorytet: Nie opisano wpływu na zadanie ani sposobu poprawienia wyniku.

Odrębność: Nowy błąd pojedynczej operacji obracania obrazu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na obowiązki i informacji o alternatywnej operacji lub narzędziu.
Zatwierdzone etykiety: **software / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na obowiązki i informacji o alternatywnej operacji lub narzędziu.

## FINAL-EN-068

That extension calls the same webhook twice for one button press.

Jakość opisu: **weak**.

Propozycja: **software / nieustalalny priorytet**.

Kategoria: Rozszerzenie programu powiela wywołanie operacji po jednym naciśnięciu.
Priorytet: Nie opisano skutków podwójnego wywołania ani wpływu na pracę.

Odrębność: Nowa duplikacja żądania przez rozszerzenie, nie zbiorcze maile aplikacji monitorującej.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak skutków, zasięgu problemu i obejścia.
Zatwierdzone etykiety: **software / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak skutków, zasięgu problemu i obejścia.

## FINAL-EN-069

There's an unused guest login in my account list. It is disabled; my own access and work are unaffected.

Jakość opisu: **weak**.

Propozycja: **accounts_access / low**.

Kategoria: Opis wskazuje stan nieużywanego konta gościa.
Priorytet: Opis wprost wyklucza wpływ na dostęp i obowiązki.

Odrębność: Nowe nieaktywne konto gościa, odrębne od oczekującego zaproszenia do projektu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak szczegółów administracyjnych; objaw i brak wpływu wystarczają do obu etykiet.
Zatwierdzone etykiety: **accounts_access / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-070

My laptop's trackpad is physically cracked and won't click. A USB mouse lets me do the job, just awkward on the train.

Jakość opisu: **weak**.

Propozycja: **hardware / medium**.

Kategoria: Opisano fizycznie pęknięty i niesprawny trackpad.
Priorytet: Działa obejście myszą, choć utrudnia pracę w podróży.

Odrębność: Nowy trackpad, nie niesprawna mysz ani klawisze laptopa z pilotażu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Krótki opis bez diagnostyki; podany objaw i obejście wystarczają do obu etykiet.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-071

Only ICMP crosses the temporary link; TCP sessions time out. Today's remote inspection is blocked, no other route.

Jakość opisu: **weak**.

Propozycja: **network / high**.

Kategoria: Różna osiągalność protokołów na łączu wskazuje komunikację sieciową.
Priorytet: Ważna inspekcja jest zablokowana bez innej trasy.

Odrębność: Nowe tymczasowe łącze przepuszczające jedynie ICMP, odrębne od NTP i IPv6.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak dokładnej przyczyny i pełnej diagnostyki; objaw i wpływ wystarczają do obu etykiet.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-072

The queue handler drops every new job after yesterday's patch. Our whole dispatch team is stopped; there is no fallback.

Jakość opisu: **weak**.

Propozycja: **software / critical**.

Kategoria: Obsługa kolejki po aktualizacji odrzuca każde nowe zadanie.
Priorytet: Kluczowy proces całego zespołu stoi bez trybu zastępczego.

Odrębność: Nowa utrata zadań w obsłudze kolejki, nie błąd zapisu zamówień z pilotażu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak logów i szczegółów implementacji; objaw oraz skutki wystarczają do obu etykiet.
Zatwierdzone etykiety: **software / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-073

The panel gets stuck on that step again, sometimes.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Nie wskazano, czym jest panel, który krok zawodzi ani czy przyczyną jest dostęp, sprzęt, sieć lub aplikacja.
Priorytet: Brak zadania, jego znaczenia, zasięgu i obejścia.

Odrębność: Nowe nieokreślone zatrzymanie panelu, bez przypisania do konkretnego incydentu pilotażu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Nieustalalne są obie etykiety; potrzebny opis urządzenia lub narzędzia, objawu i wpływu.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Nieustalalne są obie etykiety; potrzebny opis urządzenia lub narzędzia, objawu i wpływu.

## FINAL-EN-074

I keep getting a red warning at the desk. I don't know which bit it comes from.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Nie wiadomo, czy ostrzeżenie pochodzi z urządzenia, sieci, konta lub programu.
Priorytet: Nie opisano wpływu na wykonywanie pracy.

Odrębność: Nowe nieokreślone źródło ostrzeżenia, a nie kopia znanego opisu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak źródła, treści ostrzeżenia i skutków dla pracy.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak źródła, treści ostrzeżenia i skutków dla pracy.

## FINAL-EN-075

It says 'not available' when I try from here.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Ogólny komunikat nie określa mechanizmu ani narzędzia.
Priorytet: Nie podano celu operacji, dostępnych alternatyw ani liczby dotkniętych osób.

Odrębność: Nowy ogólny komunikat niedostępności, bez dopowiadania rodzaju usługi.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak identyfikacji usługi, szczegółów objawu i wpływu.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak identyfikacji usługi, szczegółów objawu i wpływu.

## FINAL-EN-076

Something changed overnight; I can't get the usual thing done.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Opis nie identyfikuje urządzenia, usługi ani rodzaju awarii.
Priorytet: Nie wiadomo, czym jest zadanie, czy jest ważne i czy istnieje obejście.

Odrębność: Nowy nieokreślony problem po nocnej zmianie; nie przypisujemy fikcyjnej przyczyny.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak konkretnego objawu, zadania, jego znaczenia i alternatywy.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak konkretnego objawu, zadania, jego znaczenia i alternatywy.

## FINAL-EN-077

The little warning is still there. Everything I need works, and it doesn't slow me down.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / low**.

Kategoria: Nie określono źródła ani treści ostrzeżenia.
Priorytet: Użytkownik wprost stwierdza brak wpływu na zadania i tempo pracy.

Odrębność: Nowy ogólny komunikat bez wpływu; nie znamy jego technicznego źródła.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Kategoria nieustalalna; priorytet ustalalny na podstawie jawnego braku utrudnień.
Zatwierdzone etykiety: **None / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Kategoria nieustalalna; priorytet ustalalny na podstawie jawnego braku utrudnień.

## FINAL-EN-078

That thing still won't open, but the approved backup option works. Switching over is slowing my work.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / medium**.

Kategoria: Nie wiadomo, czym jest niedostępny element ani dlaczego się nie otwiera.
Priorytet: Działające zatwierdzone obejście umożliwia pracę kosztem czasu.

Odrębność: Nowe nieokreślone narzędzie z działającą opcją zapasową, bez ukrytej etykiety kategorii.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak rodzaju narzędzia i mechanizmu awarii; podano wpływ oraz obejście.
Zatwierdzone etykiety: **None / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak rodzaju narzędzia i mechanizmu awarii; podano wpływ oraz obejście.

## FINAL-EN-079

I can't complete today's required equipment acceptance. There is no alternative way or available replacement to do it.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / high**.

Kategoria: Samo zadanie odbioru sprzętu nie wskazuje, czy problem jest sprzętowy, uprawnieniowy, sieciowy lub programowy.
Priorytet: Ważne wymagane zadanie jest zablokowane bez alternatywy.

Odrębność: Nowa nieokreślona blokada odbioru; nie traktujemy słowa equipment jako dowodu awarii sprzętu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak konkretnego objawu i źródła problemu; opis wystarcza do priorytetu.
Zatwierdzone etykiety: **None / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak konkretnego objawu i źródła problemu; opis wystarcza do priorytetu.

## FINAL-EN-080

Whatever failed has stopped every agent from handling customer requests. The main service is unavailable and we have no fallback.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / critical**.

Kategoria: Nie określono źródła ani rodzaju niedostępności głównej usługi.
Priorytet: Kluczowa usługa blokuje cały zespół i nie ma obejścia.

Odrębność: Nowa zbiorowa blokada o nieznanej przyczynie, bez kopiowania opisu znanego incydentu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak kategorii technicznej; podany zasięg i brak obejścia wystarczają do priorytetu.
Zatwierdzone etykiety: **None / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak kategorii technicznej; podany zasięg i brak obejścia wystarczają do priorytetu.

## FINAL-EN-081

The account directory still lists an old recovery contact that has already been disabled by our identity team. It cannot be used to reset anything, my current recovery contact works, and signing in is unaffected. I only want the inactive entry removed from my account's list; it has not interrupted any duty.

Jakość opisu: **complete**.

Propozycja: **accounts_access / low**.

Kategoria: Nieaktywny kontakt odzyskiwania jest elementem administracji konta.
Priorytet: Działający właściwy kontakt i brak wpływu na obowiązki uzasadniają niski priorytet.

Odrębność: Nowy nieaktywny kontakt odzyskiwania, odrębny od działających kluczy i zaproszeń gościa.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-082

The remote-access account page continues to show a device registration that was retired last year. IT confirms its credential has been revoked, so it grants no access. My current registered device signs in correctly and all work proceeds normally; please remove the stale registration at the next account tidy-up.

Jakość opisu: **complete**.

Propozycja: **accounts_access / low**.

Kategoria: Zgłoszenie dotyczy historycznej rejestracji tożsamości urządzenia i odwołanego poświadczenia.
Priorytet: Wpis nie daje dostępu i nie ogranicza pracy z bieżącym urządzeniem.

Odrębność: Nowa odwołana rejestracja urządzenia, nie wygasłe zaproszenie lub pakiet kontraktora.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-083

Our time-entry service explicitly says my permission to submit as a project delegate has been removed. I can still submit the same entries directly under my own existing project membership, and the manager accepts them that way. I now have to split the entries project by project instead of sending the delegated batch, so reporting takes longer.

Jakość opisu: **complete**.

Propozycja: **accounts_access / medium**.

Kategoria: Jawna odmowa delegowanej operacji przy zachowanym osobistym uprawnieniu.
Priorytet: Działa alternatywny sposób złożenia tych samych danych kosztem dodatkowej pracy.

Odrębność: Nowe rozdzielenie osobistego i delegowanego prawa do złożenia wpisów czasu, nie delegacja zatwierdzania rekordów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-084

The application access broker refuses to refresh my desktop client's token with 'device grant revoked'. The browser session through the approved access portal still opens the same cases and allows all required actions. I can serve customers there, but handling attachments takes extra steps compared with the desktop client.

Jakość opisu: **complete**.

Propozycja: **accounts_access / medium**.

Kategoria: Dostęp odrzuca jawnie cofnięte przyznanie uprawnienia do tokenu urządzenia.
Priorytet: Przeglądarkowy dostęp działa i pozwala realizować zadania z dodatkową obsługą.

Odrębność: Nowy cofnięty device grant przy odświeżaniu tokenu, odrębny od zakresu tokenu konta usługowego.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-085

The cluster accepts my login but refuses the required production namespace with 'namespace entitlement not assigned'. I need to run the recovery job for one customer's failed deployment before their maintenance window closes. The job cannot run in another namespace, and no other entitled operator is available during this window.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Po logowaniu występuje jawny brak uprawnienia do konkretnej przestrzeni zasobów.
Priorytet: Ważne odtworzenie jednego wdrożenia jest zablokowane bez dostępnego wykonawcy zastępczego.

Odrębność: Nowy brak entitlement do namespace klastra, nie brak folderu lub roli tagowania wydania.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-086

The evidence repository accepts my password but denies downloading the sealed bundle: 'legal-hold retrieval permission absent'. I am the designated reviewer for today's hearing and need that bundle. Screen viewing is not a permitted substitute, no authorised colleague is on duty, and the approved retrieval route is the only way to obtain it.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Konkretna operacja pobrania jest odrzucona z powodu brakującego uprawnienia.
Priorytet: Ważny wymagany materiał nie ma dozwolonego zastępstwa ani dostępnego uprawnionego wykonawcy.

Odrębność: Nowe uprawnienie do pobrania zabezpieczonego pakietu dowodowego, nie klucz szyfrowania archiwum.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-087

After the tenant migration my account is recognised, but submitting the safety declaration returns 'user belongs to a different authorised tenant'. I must lodge this site's declaration today. The receiving service requires my assigned tenant identity; I cannot submit on paper, change tenants myself or ask an available delegate to do it.

Jakość opisu: **complete**.

Propozycja: **accounts_access / high**.

Kategoria: Jawna niezgodność przypisania konta do uprawnionego tenant-a blokuje operację.
Priorytet: Obowiązkowe zgłoszenie jest zablokowane bez dostępnej dozwolonej ścieżki.

Odrębność: Nowe przypisanie tenant-a po migracji, odrębne od niezwiązanego subject tożsamości federacyjnej.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-088

The identity broker reports 'approved audience removed from trust policy' for every operator's token when opening the emergency dispatch console. The trust-policy administrator confirms the console's audience was removed. All operators across the control room are unable to dispatch jobs, and there is no separate login or manual dispatch mode.

Jakość opisu: **complete**.

Propozycja: **accounts_access / critical**.

Kategoria: Jawna zmiana polityki zaufania tokenów blokuje uwierzytelnienie do konsoli.
Priorytet: Kluczowa usługa całej dyspozytorni jest niedostępna bez zastępczego trybu.

Odrębność: Nowy błąd zaufania audience tokenów, nie podpis certyfikatu lub wyłączone konta.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **accounts_access / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-089

The latch on the external webcam's protective travel cover has broken. The camera body and lens are intact and calls look and sound normal. I leave the camera on my desk and do not need that transport cover for work; this is a request to replace the cover at routine maintenance.

Jakość opisu: **complete**.

Propozycja: **hardware / low**.

Kategoria: Uszkodzona jest fizyczna osłona transportowa urządzenia.
Priorytet: Akcesorium nie jest potrzebne do obowiązków, a kamera działa prawidłowo.

Odrębność: Nowy zatrzask osłony podróżnej, nie niesprawny obraz kamery ani stopka kamery dokumentowej.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-090

The spare display's cable-management clip has snapped off its stand. The stand itself is stable and the power and signal cables are undamaged and properly supported. The screen works normally and nothing about my work is affected; the clip just needs replacing when a part is available.

Jakość opisu: **complete**.

Propozycja: **hardware / low**.

Kategoria: Fizyczna wada uchwytu porządkowania kabli przy sprawnym monitorze.
Priorytet: Nie wpływa na stabilność, przewody ani wykonywanie obowiązków.

Odrębność: Nowy klips kablowy, odrębny od regulacji wysokości podstawy i uszkodzeń obrazu.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-091

The handset's coiled cord has a broken conductor, confirmed by testing it on a second desk phone. Conversations cut out when that cord bends. The same phone works reliably on speakerphone, which is permitted here, so I can continue taking calls, although I have to use a quiet booth for confidential ones.

Jakość opisu: **complete**.

Propozycja: **hardware / medium**.

Kategoria: Przerwany przewód słuchawki potwierdzono na drugim urządzeniu.
Priorytet: Działa dozwolony tryb głośnomówiący z dodatkowym ograniczeniem miejsca rozmów.

Odrębność: Nowy przewód słuchawki telefonu, nie awaria transmisji RTP lub mikrofonu laptopa.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-092

The scanner's physical start button stays pressed and its local diagnostic identifies a failed switch. Starting the scan from the computer still captures every page correctly. I can finish the digitisation using that method, but I have to return to the computer between batches rather than use the button beside the paper tray.

Jakość opisu: **complete**.

Propozycja: **hardware / medium**.

Kategoria: Własna diagnostyka urządzenia wskazuje uszkodzony fizyczny przycisk.
Priorytet: Uruchomienie z komputera jest działającym obejściem wymagającym dodatkowej obsługi.

Odrębność: Nowy przycisk startu skanera, nie mechanizm podajnika lub pokrywa urządzenia.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-093

The hardware diagnostic on our calibration colourimeter says its measurement sensor has failed; it cannot take a reading even in stand-alone mode. I need a certified colour reading to release today's proof. We have no compatible spare sensor, and a visual estimate or another type of meter is not accepted for release.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Diagnostyka sprzętu potwierdza uszkodzony czujnik pomiarowy.
Priorytet: Ważna certyfikowana kontrola jest niemożliwa bez akceptowanego urządzenia zastępczego.

Odrębność: Nowy czujnik kolorymetru, nie ekran, napęd lub przyrząd pokazujący tylko kosmetyczną wadę.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-094

The secure signing token's built-in diagnostic reports a failed memory chip, and it cannot read its stored certificate on either workstation we tried. I must sign one customer's approved design today. The certificate has no exportable copy, a replacement token is not available, and signing by another method is not authorised.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Wskazano fizyczny błąd pamięci tokenu potwierdzony na dwóch stanowiskach.
Priorytet: Ważny podpis jest zablokowany bez kopii poświadczenia i urządzenia zastępczego.

Odrębność: Nowa pamięć tokenu sprzętowego, odrębna od uprawnień do klucza lub utraty zarejestrowanego klucza MFA.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-095

The small optical-disc writer used for sealed evidence media has a broken tray motor; its own service test cannot close the tray. I must produce today's required write-once evidence disc. The authority accepts only that approved medium and device combination, and we have no replacement writer or permitted online delivery route.

Jakość opisu: **complete**.

Propozycja: **hardware / high**.

Kategoria: Mechanizm napędu ma potwierdzony błąd silnika w teście serwisowym.
Priorytet: Wymagany nośnik dowodowy nie może powstać inną dopuszczoną drogą.

Odrębność: Nowy silnik tacki zapisu optycznego, nie zakleszczona taśma archiwalna.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-096

The central storage shelf reports a failed backplane and none of its drives can be reached by either controller, although the controllers themselves pass their tests. Every production terminal has lost the order database and production has stopped. The replica is unavailable and there is no offline order list or replacement shelf to use.

Jakość opisu: **complete**.

Propozycja: **hardware / critical**.

Kategoria: Diagnostyka wskazuje fizyczne uszkodzenie backplane przy sprawnych kontrolerach.
Priorytet: Kluczowa baza jest niedostępna dla wszystkich terminali bez repliki lub trybu offline.

Odrębność: Nowa awaria połączeń backplane, odrębna od zasilania macierzy i ochrony cache kontrolera.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **hardware / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-097

The network manager shows a public IPv6 address changing periodically on my work laptop. Connections remain stable, company services work and I have not lost any sessions. I am asking if this address rotation is expected; there is no delay or blocked task associated with it.

Jakość opisu: **complete**.

Propozycja: **network / low**.

Kategoria: Zgłoszenie dotyczy adresacji sieciowej urządzenia, nie konta lub programu użytkowego.
Priorytet: Połączenia i zadania pozostają sprawne bez utrudnień.

Odrębność: Nowa obserwacja rotacji adresu IPv6, nie brak trasy lub niedziałający transport IPv6.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-098

The approved screen-sharing receiver can be pinged and reached on the local network, but its discovery service is advertising the previous address after a subnet move. Our connection profile with the current fixed address works reliably. Meetings can continue, but hosts must choose the manual profile until the advertisement is corrected.

Jakość opisu: **complete**.

Propozycja: **network / medium**.

Kategoria: W sieci ogłaszany jest stary adres usługi po zmianie podsieci.
Priorytet: Działa zatwierdzony profil z poprawnym adresem, lecz wymaga wyboru ręcznego.

Odrębność: Nowe nieaktualne ogłoszenie po przeadresowaniu, odrębne od blokowania pakietów odkrywania między VLAN-ami.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-099

The new office firewall closes idle database TCP sessions after one minute, and our independent network test reproduces the reset without the application. The approved connection setting that opens a fresh session for each operation works. I can process the records with it, but each operation now takes longer to establish a connection.

Jakość opisu: **complete**.

Propozycja: **network / medium**.

Kategoria: Test poza aplikacją wskazuje reset bezczynnych sesji TCP przez pośredniczące urządzenie.
Priorytet: Dozwolone nowe połączenie dla każdej operacji pozwala pracować z opóźnieniem.

Odrębność: Nowy timeout bezczynnej sesji na firewallu, nie ciągłe zrywanie połączenia VPN.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-100

The laboratory broker accepts the network handshake but the route drops all return traffic from its data port; our packet captures show replies entering the border interface and never reaching my workstation. I need to collect today's certified test readings. There is no alternate port, approved network path or workstation that can complete this collection.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Zapis ruchu pokazuje brak przekazywania odpowiedzi na ścieżce sieciowej.
Priorytet: Ważny odbiór danych pomiarowych jest zablokowany bez dostępnej alternatywy.

Odrębność: Nowa jednokierunkowa ścieżka portu danych brokera, nie ogólna niedostępność całej podsieci laboratorium.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-101

The managed transfer gateway cannot resolve the external partner's new DNSSEC-signed domain: validation rejects its current chain, while unsigned unrelated domains resolve normally. The partner confirms its endpoint is running. I must send today's regulated transfer through this gateway; policy forbids disabling validation, using an IP address or sending through another channel.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Nie działa sieciowe rozwiązywanie konkretnej domeny z walidacją DNSSEC.
Priorytet: Ważna regulowana wysyłka nie ma dopuszczonego obejścia ani kanału zastępczego.

Odrębność: Nowa ścieżka walidacji DNSSEC do partnera, nie ogólny brak DNS lub zapisany stary adres.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-102

The wired acquisition device sends tagged traffic on VLAN 214, but the authorised uplink no longer carries that VLAN; the switch trace shows the frames being discarded there. I need its live samples for today's acceptance run. The device cannot use wireless, and no spare uplink or permitted local recording mode is available.

Jakość opisu: **complete**.

Propozycja: **network / high**.

Kategoria: Na łączu nie jest przenoszony wymagany VLAN i jego ramki są odrzucane.
Priorytet: Ważny pomiar na żywo jest zablokowany bez innego dozwolonego połączenia.

Odrębność: Nowy brak VLAN na trunku, odrębny od pętli routingu i konfliktu adresów IP.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-103

The branch's network admission gateway refuses to forward traffic for every already-authenticated workstation because its address-to-port bindings were cleared. The network team confirms packets are being discarded at that gateway, not rejected by users' accounts. All service desks are stopped, and no bypass network or offline service mode is available.

Jakość opisu: **complete**.

Propozycja: **network / critical**.

Kategoria: Uwierzytelnienie działa, a urządzenie sieciowe odrzuca ruch przez brak powiązań portów i adresów.
Priorytet: Wszystkie stanowiska obsługi są zablokowane bez sieci zapasowej lub trybu offline.

Odrębność: Nowa utrata powiązań bramki dopuszczania ruchu, nie odmowa uprawnień kont lub awaria łączy między oddziałami.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **network / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-104

The document comparison tool shows the result-tab title twice after I detach and reattach the tab. The comparison itself is accurate, the exported result is correct, and the duplicate title neither hides information nor slows any operation I need. This is a cosmetic issue in the tab header.

Jakość opisu: **complete**.

Propozycja: **software / low**.

Kategoria: Powielony tytuł zakładki jest błędem interfejsu aplikacji.
Priorytet: Funkcje, dane i tempo wykonywania zadań pozostają bez zmian.

Odrębność: Nowy tytuł odłączanej zakładki, nie powielone ogłoszenie sieciowe lub lista dokumentów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-105

The translation tool applies the first glossary entry to every selected term instead of using each term's matching entry. The source text is unchanged. I can apply the correct glossary items individually and produce an approved translation, but reviewing and replacing them one at a time makes each document slower to finish.

Jakość opisu: **complete**.

Propozycja: **software / medium**.

Kategoria: Funkcja masowego dopasowania słownika programu wybiera błędne wartości.
Priorytet: Ręczne zastosowanie prawidłowych wpisów jest działającym obejściem kosztem czasu.

Odrębność: Nowe dopasowanie glosariusza w tłumaczeniu, nie kodowanie nazw lub eksport pliku.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-106

The diagram editor moves connector arrows to the wrong shapes when I use automatic layout. Manual placement keeps every connector attached correctly, and the saved diagram passes our review. I can finish the design with auto-layout disabled, although arranging all the shapes and arrows manually takes extra time.

Jakość opisu: **complete**.

Propozycja: **software / medium**.

Kategoria: Automatyczne rozmieszczenie elementów programu błędnie przypisuje łączniki.
Priorytet: Ręczne rozmieszczenie daje poprawny wynik i pozwala wykonać zadanie.

Odrębność: Nowy błąd relacji po automatycznym układzie diagramu, nie awaria zapisu lub otwarcia rysunku.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-107

The medication-label generator prints a dose unit different from the unit in its validated input, including with the supplier's approved sample. The workstation, printer self-test and stored source record are correct. I must produce the verified label set for this patient's preparation today; handwritten labels and alternative generators are not authorised.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Generator etykiet zamienia jednostkę mimo poprawnych danych wejściowych i sprawnej drukarki.
Priorytet: Ważny wymagany zestaw etykiet nie może zostać poprawnie przygotowany inną dozwoloną drogą.

Odrębność: Nowa zamiana jednostek w generowaniu dokumentu, odrębna od minusów kwot i fizycznych wad drukarki.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-108

The digital preservation validator reads a valid archive but calculates its checksum over an empty stream; the same happens with the tool's bundled test archive. I need the validator's signed acceptance report for today's deposit. We may not substitute a manual checksum or another validator, and there is no supported setting that avoids the issue.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Potwierdzony na próbce narzędzia błąd obliczenia sumy kontrolnej dotyczy algorytmu programu.
Priorytet: Ważny wymagany raport akceptacji nie ma dopuszczonego sposobu zastępczego.

Odrębność: Nowy walidator sum archiwów, nie błąd odczytu dysku lub niepoprawny manifest nazw komponentów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-109

The accessibility checker marks every heading in a valid document as body text and omits its required structure report. The vendor's reference document produces the same result, and reading or editing the file works elsewhere. I must submit the certified structure report today; only this checker is approved and there is no manual attestation route.

Jakość opisu: **complete**.

Propozycja: **software / high**.

Kategoria: Funkcja klasyfikacji struktury dokumentu działa błędnie także dla poprawnego pliku referencyjnego.
Priorytet: Wymagany terminowy raport jest zablokowany bez zatwierdzonego narzędzia lub procedury zastępczej.

Odrębność: Nowa analiza struktury dostępności dokumentu, nie usuwanie treści lub podgląd PDF.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-110

A new rules-engine release treats every accepted reservation as cancelled as soon as it saves the record. All agents reproduce it with otherwise valid requests, while authentication and connectivity work. The entire booking service has stopped taking reservations, and neither the previous release nor a manual booking process is available.

Jakość opisu: **complete**.

Propozycja: **software / critical**.

Kategoria: Nowa wersja reguł programu niepoprawnie zmienia stan poprawnych rezerwacji.
Priorytet: Kluczowa usługa rezerwacji jest zablokowana dla wszystkich agentów bez alternatywy.

Odrębność: Nowe niepoprawne przejście stanu rezerwacji, nie interpretacja dni kalendarza lub alokacja zasobów.

Decyzja autora: **approved**.
Zatwierdzone etykiety: **software / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-111

The upload page says 'consent for this application has been withdrawn' after I sign in.

Jakość opisu: **weak**.

Propozycja: **accounts_access / nieustalalny priorytet**.

Kategoria: Jawne cofnięcie zgody aplikacyjnej określa problem dostępu.
Priorytet: Nie opisano skutków dla obowiązków ani dostępnej alternatywy.

Odrębność: Nowa krótka odmowa wycofanej zgody przy przesyłaniu, nie ten sam incydent istniejącego narzędzia webowego.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na pracę, zasięgu i obejścia.
Zatwierdzone etykiety: **accounts_access / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na pracę, zasięgu i obejścia.

## FINAL-EN-112

The headset's earcup bracket has snapped, and the cup is hanging by its wire.

Jakość opisu: **weak**.

Propozycja: **hardware / nieustalalny priorytet**.

Kategoria: Opisano fizycznie złamane mocowanie słuchawki.
Priorytet: Nie wiadomo, czy można rozmawiać, czy są wymagane rozmowy i czy jest zastępstwo.

Odrębność: Nowe mechaniczne mocowanie słuchawki, nie jej regulacja głośności lub przewód telefonu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu na zadania i możliwości użycia innego urządzenia.
Zatwierdzone etykiety: **hardware / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu na zadania i możliwości użycia innego urządzenia.

## FINAL-EN-113

Both ends show a duplex mismatch and the switch counts late collisions on that link.

Jakość opisu: **weak**.

Propozycja: **network / nieustalalny priorytet**.

Kategoria: Niezgodność dupleksu i kolizje dotyczą parametrów połączenia sieciowego.
Priorytet: Nie podano znaczenia ruchu ani skutków dla użytkowników.

Odrębność: Nowa niezgodność dupleksu łącza, odrębna od brakującego VLAN i zmiany prędkości.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak identyfikacji usługi, zasięgu awarii i obejścia.
Zatwierdzone etykiety: **network / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak identyfikacji usługi, zasięgu awarii i obejścia.

## FINAL-EN-114

The spreadsheet extension copies the first row into every output row when I press Generate.

Jakość opisu: **weak**.

Propozycja: **software / nieustalalny priorytet**.

Kategoria: Jedna operacja dodatku wytwarza powielone dane zamiast prawidłowego wyniku.
Priorytet: Nie opisano zadania ani możliwej innej metody przygotowania danych.

Odrębność: Nowe powielenie wiersza w generatorze dodatku, nie format liczb w podglądzie.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak wpływu, pilności i informacji o obejściu.
Zatwierdzone etykiety: **software / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak wpływu, pilności i informacji o obejściu.

## FINAL-EN-115

The network graph shows a brief jitter spike, but calls and every work task remain unaffected.

Jakość opisu: **weak**.

Propozycja: **network / low**.

Kategoria: Opis dotyczy zmienności opóźnienia transmisji.
Priorytet: Jawny brak wpływu na rozmowy i obowiązki uzasadnia niski priorytet.

Odrębność: Nowa obserwacja jittera bez skutków, nie gubienie połączenia lub brak danych o wpływie.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak diagnostyki szczegółowej; objaw i brak wpływu wystarczają do etykiet.
Zatwierdzone etykiety: **network / low**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-116

The packing app puts the last page first in its PDF. Reordering it in our approved PDF tool works, but adds work.

Jakość opisu: **weak**.

Propozycja: **software / medium**.

Kategoria: Program generuje dokument z błędną kolejnością stron.
Priorytet: Działające dozwolone obejście umożliwia pracę kosztem dodatkowej czynności.

Odrębność: Nowa kolejność stron gotowego dokumentu, nie wyłączanie aplikacji podczas eksportu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Krótki opis bez logów; podano błędny wynik i obejście.
Zatwierdzone etykiety: **software / medium**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji.

## FINAL-EN-117

The normal route ends at a blank screen now. Not sure what changed.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Brak nazwy narzędzia i objawu pozwalającego odróżnić dostęp, transmisję, urządzenie i aplikację.
Priorytet: Nie podano celu operacji, wpływu ani alternatywy.

Odrębność: Nowy ogólny pusty ekran bez ukrytej etykiety kategorii.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak narzędzia, warunków występowania i wpływu na obowiązki.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak narzędzia, warunków występowania i wpływu na obowiązki.

## FINAL-EN-118

It asks me to do something I don't recognise, then I can't carry on with that bit.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / nieustalalny priorytet**.

Kategoria: Nie opisano komunikatu, urządzenia ani mechanizmu zatrzymania.
Priorytet: Nie wiadomo, czym jest etap, jak ważne jest zadanie i czy istnieje obejście.

Odrębność: Nowe nieokreślone żądanie podczas operacji, nie kopia poprzedniego ogólnego błędu.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak treści komunikatu, identyfikacji operacji oraz skutków.
Zatwierdzone etykiety: **None / None**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak treści komunikatu, identyfikacji operacji oraz skutków.

## FINAL-EN-119

Today's mandatory validation cannot be completed. Nobody can cover it and there is no alternative method.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / high**.

Kategoria: Opis podaje tylko zablokowane zadanie, bez technicznego objawu lub narzędzia.
Priorytet: Ważna wymagana walidacja jest zablokowana bez zastępstwa i obejścia.

Odrębność: Nowa blokada obowiązkowej walidacji o nieznanym źródle technicznym.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak kategorii technicznej; wpływ i brak alternatywy pozwalają ustalić priorytet.
Zatwierdzone etykiety: **None / high**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak kategorii technicznej; wpływ i brak alternatywy pozwalają ustalić priorytet.

## FINAL-EN-120

The essential service is down for every operator at all sites. All processing has stopped and there is no backup process.

Jakość opisu: **weak**.

Propozycja: **nieustalalna kategoria / critical**.

Kategoria: Nie wskazano przyczyny ani technicznego rodzaju niedostępności usługi.
Priorytet: Kluczowa usługa blokuje wszystkich operatorów bez procesu zapasowego.

Odrębność: Nowa zbiorowa blokada o nieopisanym źródle, bez przypisywania domniemanej kategorii.

Decyzja autora: **approved**.
Brakujące informacje / ograniczenia: Brak objawu identyfikującego kategorię; podano zasięg i brak alternatywy.
Zatwierdzone etykiety: **None / critical**.
Autor: autor pracy (użytkownik rozmowy); zapis decyzji: 2026-11-07T18:52:37+00:00.
Jawne zatwierdzenie pozostałych przypadków w rozmowie: „Dobra, akceptuj te przypadki i lecimy”. Bez zmian treści i propozycji. Zatwierdzenie obejmuje podany brak informacji do ustalenia etykiety: Brak objawu identyfikującego kategorię; podano zasięg i brak alternatywy.
