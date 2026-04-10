## [1.0.0] - 2026-04-10

### Nowe funkcje

- Dodano tworzenie katalogów lotów bezpośrednio z poziomu aplikacji.
- Rozdzielono generowanie list oddziałowych, sekcyjnych i dodatkowych wariantów PDF.
- Dodano obsługę lotów gołębi starych i młodych wraz z przełączaniem typu sezonu.
- Dodano osobny generator listy startowo-zegarowej z pliku `DANE_GL/DRLSTZEG.TXT`.
- Dodano obsługę list rankingowych hodowców.
- Dodano wsparcie dla `II-LIGA`: dołączanie do listy głównej oraz generowanie osobnego PDF.
- Dodano zapamiętywanie ostatnio wybranego numeru lotu i stanu opcji w interfejsie.
- Dodano możliwość definiowania własnych nazw plików PDF i kolejności dołączanych plików.
- Dodano przykładowe pliki i rozszerzono zestaw testów projektu.

### Zmiany i usprawnienia

- Przebudowano główny widok aplikacji, menu oraz układ sekcji ustawień.
- Odświeżono okna `O programie` i `Dziennik zmian`.
- Uporządkowano logikę generowania PDF tak, aby lista startowo-zegarowa miała osobny pipeline i osobny szablon HTML.
- Poprawiono układ i paginację list oddziałowych oraz usunięto puste sekcje z generowania.
- Dodano generowanie osobnego PDF dla `II ligi` oraz wariantu zamkniętego.
- Usprawniono działanie zarządzania oddziałami i kolejnością list.
- Dopracowano nazewnictwo komunikatów, tekstów w interfejsie i opisów w aplikacji.

### Poprawki

- Poprawiono wyświetlanie danych w PDF oraz formatowanie wybranych wydruków.
- Usunięto błędy pamięci podręcznej UI po usunięciu oddziału.
- Poprawiono literówki i drobne niespójności w interfejsie.
- Poprawiono zgodność testów z aktualną strukturą projektu i ograniczono twardą zależność części modułów testowych od `pytest`.

## [0.7.3] - 2025-08-21

### Poprzednie wydanie

- Wersja bazowa przed zmianami prowadzącymi do wydania `1.0.0`.
