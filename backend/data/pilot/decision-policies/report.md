# Polityki weryfikacji i sugestii duplikatów

Pomiar: 2026-11-07T17:27:56.774311+00:00

120 zatwierdzonych EN; progi klasyfikacji wybrane wyłącznie z przewidywań poza własną grupą (5 foldów).
Maksymalizujemy macro-F1 z odmowami liczonymi jako FN; minimum 70% pokrycia jest przyjętym ograniczeniem użytkowym.
Wynik TF-IDF jest niekalibrowanym wynikiem modelu, nie potwierdzonym prawdopodobieństwem poprawności.

| Decyzja | Próg | Pokrycie | Accuracy zaakceptowanych |
|---|---:|---:|---:|
| Kategoria | 0.22 | 95.8% | 92.2% |
| Priorytet | 0.38 | 100.0% | 86.7% |

Minimalny udział głosów kategorii: 0.667.
Próg podobieństwa duplikatów: >0.67; filtr kategorii: False.

## Pary duplikatów

Etykiety wyprowadzono z istniejących group_id, bez dopisywania nowego zatwierdzenia przez człowieka.
Grupy incydentów walidacji i wydzielonej próby diagnostycznej są rozłączne. Wszystkie pary w każdej części są oceniane, w tym trudne podobne pary ujemne.
Filtr kategorii używa kategorii operacyjnych przewidywanych poza własną grupą po zastosowaniu polityki weryfikacji, nie etykiet wzorcowych.

| Część | Wariant | TP | FP | FN | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| validation | old | 3 | 0 | 3 | 100.0% | 50.0% | 0.667 |
| validation | selected | 5 | 0 | 1 | 100.0% | 83.3% | 0.909 |
| validation | without_category | 5 | 0 | 1 | 100.0% | 83.3% | 0.909 |
| validation | with_category | 5 | 0 | 1 | 100.0% | 83.3% | 0.909 |
| held_out_diagnostic | old | 5 | 2 | 1 | 71.4% | 83.3% | 0.769 |
| held_out_diagnostic | selected | 6 | 7 | 0 | 46.2% | 100.0% | 0.632 |
| held_out_diagnostic | without_category | 6 | 7 | 0 | 46.2% | 100.0% | 0.632 |
| held_out_diagnostic | with_category | 6 | 6 | 0 | 50.0% | 100.0% | 0.667 |

## Ograniczenia

To diagnostyka na znanym, syntetycznym pilotażu; nie niezależny test końcowy ani wynik na danych organizacji.
Kandydat 0.67 / bez filtra kategorii pogorszył precision na wydzielonej próbie. W aplikacji zachowujemy 0.75 i filtr kategorii; nie dostrajamy nowego progu do wyników tej próby.
W każdej części jest niewiele par dodatnich; dobór progu może być niestabilny. Podobny tekst nie dowodzi wspólnej awarii.
Podział, wszystkie pary, surowe przewidywania i siatki są zapisane w [report.json](report.json).
50 słabych pending nie bierze udziału w doborze progów ani treningu.
