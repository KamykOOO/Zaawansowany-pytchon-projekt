# Dokumentacja Projektowa: System Monitorowania Usług Sieciowych i Analizy Logów

**Przedmiot:** Zaawansowane techniki programowania w języku Python  
**Środowisko uruchomieniowe:** Python 3.12+

---

## 1. Opis Projektu i Architektura

Projekt stanowi kompleksowy system do wielowątkowego monitorowania dostępności usług sieciowych (HTTP), bezpiecznego rejestrowania zdarzeń do pliku oraz wydajnej analizy powstałych logów przy użyciu generatorów i wyrażeń regularnych.

Kod został podzielony na wyspecjalizowane moduły zgodnie ze sztuką inżynierii oprogramowania:

* **`main.py`** – Główny moduł wykonawczy obsługujący wielowątkowe zapytania I/O (`ThreadPoolExecutor`) oraz synchroniczny zapis zdarzeń z użyciem blokady `threading.Lock`.
* **`server_model.py`** – Warstwa obiektowa reprezentująca monitorowany serwer (`MonitoredServer`), wykorzystująca dekoratory metod oraz właściwości `@property`.
* **`config_iterator.py`** – Własna klasa iteratora (`ServerConfigIterator`) odpowiedzialna za wczytywanie oraz wstępną walidację adresów z pliku `servers.txt`.
* **`log_parser.py`** – Moduł analityczny wykorzystujący funkcje generatorów (`yield`) oraz nazwane grupy wyrażeń regularnych do przetwarzania logów bez obciążania pamięci RAM.
* **`benchmark.py`** – Moduł testowy porównujący wydajność zadań przeliczeniowych (CPU-bound) w modelach sekwencyjnym, wielowątkowym oraz wieloprocesowym.

---

## 2. Zestawienie Wymagań Technicznych

| Lp. | Zagadnienie z Wymagań | Plik / Lokalizacja | Opis Implementacji |
| :--- | :--- | :--- | :--- |
| **1** | **Dekoratory funkcji** | `main.py` | `@measure_time` (pomiar czasu wykonania) oraz `@retry(attempts=3, delay=0.5)` z użyciem `functools.wraps`. |
| **2** | **Dekoratory metod & Klasy** | `server_model.py` | Klasa `MonitoredServer`: własny dekorator metody `@require_active`, właściwość `@property` z setterem oraz `@staticmethod`. |
| **3** | **Iteratory** | `config_iterator.py` | Klasa `ServerConfigIterator` implementująca protokół iteratora (`__iter__`, `__next__` rzucająca `StopIteration`). |
| **4** | **Generatory** | `log_parser.py` | Funkcja generatora `read_logs_generator` (`yield`) oraz wyrażenie generujące `non_empty_lines`. |
| **5** | **Wyrażenia regularne** | `log_parser.py` | `LOG_PATTERN` wykorzystujący grupy nazwane (`timestamp`, `url`, `status`) oraz wzorzec walidacyjny `URL_VALIDATOR`. |
| **6** | **Wątki (`threading`)** | `main.py` | `ThreadPoolExecutor` do równoległych zapytań HTTP + `threading.Lock()` do bezpiecznego zapisu do wspólnego pliku. |
| **7** | **Procesy (`multiprocessing`)** | `benchmark.py` | `ProcessPoolExecutor` realizujący obliczenia CPU-bound na wielu rdzeniach procesora. |
| **8** | **Pomiar i analiza GIL** | `benchmark.py` | Skrypt testowy i analiza porównawcza czasów wykonania (sekwencyjnie vs wątki vs procesy). |

---

## 3. Instrukcja Uruchomienia

Wszystkie skrypty należy uruchamiać z poziomu głównego katalogu projektu:

1. **Uruchomienie monitora serwerów:**
   ```bash
   python3 main.py
   ```
2. **Uruchomienie analizatora logów (generatory + regex):**
   ```bash
   python3 log_parser.py
   ```
3. **Weryfikacja modelu serwera:**
   ```bash
   python3 server_model.py
   ```
4. **Weryfikacja iteratora konfiguracji:**
   ```bash
   python3 config_iterator.py
   ```
5. **Wykonanie benchmarku wydajności GIL:**
   ```bash
   python3 benchmark.py
   ```

---

## 4. Analiza Wydajności i Wpływu GIL (Global Interpreter Lock)

### Wyniki Pomiarów (Zadanie CPU-bound: $4 \times 5 \cdot 10^6$ iteracji)
Pomiary przeprowadzono na architekturze Apple Silicon (macOS).

| Wariant Wykonania | Czas Wykonania | Przyspieszenie |
| :--- | :--- | :--- |
| **1. Sekwencyjnie (1 rdzeń)** | `~0.6631 s` | 1.0x (baza) |
| **2. Wątki (`ThreadPoolExecutor`)** | `~0.6270 s` | ~1.05x |
| **3. Procesy (`ProcessPoolExecutor`)** | `~0.2031 s` | **~3.26x** |

### Wnioski Techniczne

1. **Zadania I/O-bound a Wątki (`main.py`):** Operacje sieciowe (odpytywanie serwerów HTTP) są ograniczane przez czas oczekiwania na odpowiedź gniazda. W tym przypadku wątki pozwalają na efektywne zwalnianie interpretera i wielokrotne skrócenie czasu pracy skryptu głównego.
2. **Zadania CPU-bound a GIL (`benchmark.py`):** Global Interpreter Lock sprawia, że w przypadku intensywnych obliczeń matematycznych wątki nie działają równolegle – interpreter przełącza się między nimi, dając jedynie iluzję współbieżności.
3. **Ominięcie GIL przez Procesy:** Moduł `multiprocessing` tworzy oddzielne instancje Pythona z własną przestrzenią adresową i własnym mechanizmem GIL. Pozwala to na pełne wykorzystanie rdzeni fizycznych procesora, co przełożyło się na ponad 3-krotne skrócenie czasu wykonania zadania.