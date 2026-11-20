# Rubryka walidacji asystenta RAG

[Zestaw walidacyjny V01–V08](validation-en-v1.json) zawiera 15 syntetycznych angielskich zgłoszeń. [Zestaw testowy T01–T22](test-en-v1.json) ma własny korpus 28 zgłoszeń i korzysta z tej samej rubryki. Przy każdym pytaniu zapisano oczekiwane źródła, wymagane fakty i warunek zaliczenia. Dopytania wykorzystują rzeczywistą odpowiedź danego wariantu z wcześniejszej tury. V05 i T05 dopuszczają także aktywne tickety, żeby sprawdzić, czy niepotwierdzona sugestia zostanie przedstawiona jako rozwiązanie.

## Ocena odpowiedzi

Porównaj odpowiedź widoczną dla użytkownika z warunkiem zaliczenia i treścią przytoczonych ticketów. Oceń znaczenie odpowiedzi; parafrazy i zwięzłe sformułowania są dopuszczalne.

| Kryterium | 2 punkty | 1 punkt | 0 punktów |
|---|---|---|---|
| Poprawność | Wszystkie istotne twierdzenia są prawdziwe i odnoszą się do pytania. | Odpowiedź jest zasadniczo poprawna, z drobną nieścisłością. | Błędne rozwiązanie, twierdzenie zmieniające sens, odmowa mimo wystarczających danych lub brak odpowiedzi na pytanie. |
| Kompletność | Są wszystkie wymagane fakty. | Jest część wymaganych faktów. | Nie podano żadnego wymaganego faktu. |
| Oparcie na źródłach | Każde istotne twierdzenie wynika z przypisanego mu ticketu. | Drobny szczegół wykracza poza to, co dokumentuje przypisany ticket. | Rozwiązanie lub inne istotne twierdzenie nie wynika z przypisanego ticketu. |
| Cytaty | Każda istotna część ma właściwy identyfikator zwrócony w odpowiedzi czatu. | Co najmniej jeden cytat jest poprawny, a co najmniej jeden jest błędny albo pominięty. | Brak właściwych cytatów. |

Przy pytaniu z odpowiedzią przypadek zalicza się po uzyskaniu 2 punktów w każdym kryterium i spełnieniu warunku dla danego pytania. Gdy czat zwraca komunikat zastępczy zamiast danych, poprawność i kompletność mają wartość 0, a oparcie na źródłach i cytaty nie podlegają ocenie.

Przy pytaniu bez udokumentowanego rozwiązania stosuj osobną skalę. **2** oznacza jasną informację o braku udokumentowanej odpowiedzi, **1** oznacza niejasną odpowiedź bez wymyślonego rozwiązania, a **0** oznacza przedstawienie spekulacji lub błędnie dopasowanego źródła jako udokumentowanego rozwiązania. Zaliczenie wymaga 2 punktów. Błąd wykonania zapisuj osobno jako niezaliczony przypadek, z kodem błędu.

## Ocena wyszukiwania i raport

- Zapisz źródła przekazane do modelu w kolejności. Dla samodzielnych pytań z oczekiwanymi źródłami oblicz Recall@5 i MRR@5. W dopytaniu zapisz, które źródła wróciły z historii i czy były wystarczające do odpowiedzi.
- Dla pytań bez odpowiedzi zapisz, czy wyszukiwanie zwróciło jakieś tickety i czy model poprawnie rozpoznał brak danych. Samo zwrócenie potencjalnie podobnego zgłoszenia może być przydatną informacją diagnostyczną.
- Raportuj liczbę zaliczeń na wszystkich przypadkach oraz oddzielne wyniki pytań z odpowiedzią i bez niej. Przy niezaliczeniu zapisz, czy brakowało źródła w kontekście, czy odpowiedź źle wykorzystała dostępny materiał.
- W obu przebiegach ocenia Codex przez porównanie zapisu odpowiedzi ze zgłoszeniami. Oceny i wzorce odpowiedzi wymagają przeglądu autora przed użyciem w pracy jako ocena końcowa.
