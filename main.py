from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any
import functools
import threading
import time
import urllib.request

from config_iterator import ServerConfigIterator
from log_parser import parse_logs
from server_model import MonitoredServer


log_lock = threading.Lock()


def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mierzy czas wykonania funkcji."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        print(f"[Czas zapytania dla {args[0]}: {elapsed:.4f}s]")
        return result

    return wrapper


def retry(attempts: int = 3, delay: float = 0.5) -> Callable[..., Any]:
    """Ponawia wykonanie funkcji w przypadku błędu."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    print(
                        f"  -> Próba {attempt}/{attempts} "
                        f"dla {args[0]} nieudana ({e})"
                    )

                    if attempt < attempts:
                        time.sleep(delay)

            save_log(args[0], "OFFLINE (wyczerpano limit prób)")
            return None

        return wrapper

    return decorator


def save_log(url: str, status: str) -> None:
    """Zapisuje informację o stanie serwera do pliku logów."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | {url} | {status}\n"

    with log_lock:
        with open("server_logs.txt", "a", encoding="utf-8") as file:
            file.write(log_entry)


@measure_time
@retry(attempts=3, delay=0.5)
def check_server_status(url: str) -> int | None:
    """Sprawdza dostępność serwera HTTP."""

    with urllib.request.urlopen(url, timeout=3) as response:
        status = response.getcode()

    save_log(url, f"OK ({status})")

    return status


def check_server(server: MonitoredServer) -> None:
    """Sprawdza serwer i aktualizuje jego stan w modelu."""
    status = check_server_status(server.url)
    server.update_status(f"OK ({status})" if status is not None else "OFFLINE")


def main() -> None:
    """Sprawdza wszystkie serwery z pliku konfiguracyjnego równolegle."""
    servers = [MonitoredServer(url) for url in ServerConfigIterator("servers.txt")]

    total_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(check_server, servers))

    total_elapsed = time.perf_counter() - total_start

    print(
        f"\nCałkowity czas sprawdzania wszystkich serwerów: "
        f"{total_elapsed:.4f}s"
    )

    print("\n--- Historia z pliku logów ---")
    for entry in parse_logs("server_logs.txt"):
        print(f"{entry['timestamp']} | {entry['url']} | {entry['status']}")


if __name__ == "__main__":
    main()