import functools


def require_active(method):
    """Sprawdza stan obiektu (self.is_active) przed uruchomieniem metody."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_active:
            print(f"[Pominięto] Monitoring dla {self.url} jest wyłączony.")
            return None
        return method(self, *args, **kwargs)
    return wrapper


class MonitoredServer:
    """Reprezentuje pojedynczy monitorowany serwer wraz z jego stanem."""

    def __init__(self, url: str, is_active: bool = True):
        self.url = url
        self.is_active = is_active
        self._status = "UNKNOWN"
        self.checks_count = 0

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, new_status: str) -> None:
        if not new_status:
            raise ValueError("Status nie może być pusty!")
        self._status = new_status

    @staticmethod
    def format_report(url: str, status: str) -> str:
        return f"Host: {url:<35} | Stan: {status}"

    @require_active
    def update_status(self, new_status: str) -> None:
        self.status = new_status
        self.checks_count += 1
        print(f"{self.format_report(self.url, self.status)} | Sprawdzeń: {self.checks_count}")


if __name__ == "__main__":
    print("--- Test modelu serwera i dekoratorów metod ---")
    s1 = MonitoredServer("http://www.google.com", is_active=True)
    s1.update_status("OK (200)")

    s2 = MonitoredServer("http://serwer-w-konserwacji.pl", is_active=False)
    s2.update_status("OK (200)") 