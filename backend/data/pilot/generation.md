# Pochodzenie próbki pilot-pl-v1

Data: 2026-10-28. Narzędzie: asystent OpenAI Codex w tej rozmowie.
Dokładny identyfikator modelu, temperature, top_p oraz seed generatora nie
zostały udostępnione asystentowi. Nie deklarujemy powtarzalności generacji.
Powtarzalny jest zapisany artefakt JSON, identyfikowany przez SHA-256 w raporcie.

Użytkownik zaakceptował przygotowanie instrukcji etykietowania, 40 polskich
zgłoszeń pilotażowych po 10 na kategorię i wstępnego sprawdzenia obowiązkowego
MiniLM przed rozbudową zbioru. Treści przygotowano bez danych organizacji,
bez danych osobowych, haseł i sekretów. Nie używano zewnętrznego generatora API.

Instrukcja przygotowania danych zastosowana podczas redagowania:

> Przygotuj 40 syntetycznych, krótkich zgłoszeń helpdesku IT po polsku,
> po 10 w kategoriach Konta i uprawnienia, Sprzęt, Sieć i łączność oraz
> Oprogramowanie. Użyj różnych scenariuszy i naturalnych wypowiedzi,
> uwzględniając granice kategorii. Każdy opis powinien zawierać informacje
> o wpływie i obejściu wystarczające do zaproponowania priorytetu bazowego.
> W każdej kategorii zaproponuj 2 low, 4 medium, 3 high i 1 critical.
> Priorytet critical wymaga opisanej blokady wielu osób przez awarię
> kluczowej usługi; blokada ważnego zadania jednej osoby bez obejścia to high.
> Umieść jedną parę parafraz tego samego incydentu w każdej kategorii
> i oznacz wspólną grupą. Pozostałe rekordy powinny opisywać odrębne przypadki.
> Zachowaj niezależne pole checkboxa blokady pracy. Do każdej propozycji
> kategorii i priorytetu dodaj uzasadnienie. Wszystkie rekordy oznacz jako
> oczekujące na ręczny przegląd, bez przypisywania fikcyjnego recenzenta.

Stałe liczebności służą pokryciu przypadków w pilotażu i nie opisują naturalnego
rozkładu zgłoszeń. Priorytety i styl opisów mogą tworzyć sztuczne wskazówki
językowe. Wyników nie należy przedstawiać jako skuteczności na danych organizacji.

Żaden rekord na dzień generacji nie został zatwierdzony przez autora pracy.
