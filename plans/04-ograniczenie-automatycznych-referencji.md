# Ograniczenie automatycznych referencji

Zgłoszenie ze statusem `Resolved`, aktualnym embeddingiem i kompletnymi etykietami automatycznie trafia do zbioru referencji klasyfikatora. Status potwierdza rozwiązanie problemu. Zapisana kategoria operacyjna i priorytet bazowy mogą nadal pochodzić z błędnej predykcji.

Błędna kategoria może zmienić głosowanie KNN, a błędny priorytet bazowy może wpłynąć na ponowny trening modelu TF-IDF z regresją logistyczną. W ten sposób automatyczne dodawanie referencji może utrwalać wcześniejsze błędy w kolejnych klasyfikacjach.

Wyniki trafności z etapu E10.3 dotyczą zamrożonego zbioru referencji. Wpływ automatycznego dodawania zgłoszeń na trafność pozostaje do sprawdzenia. W obu wariantach porównania należy użyć tych samych niezależnych zgłoszeń testowych i tej samej konfiguracji klasyfikatora, zmieniając wyłącznie zbiór referencji. Zgłoszenia testowe pozostają poza treningiem w obu wariantach.
