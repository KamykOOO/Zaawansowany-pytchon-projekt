from log_parser import is_valid_url


class ServerConfigIterator:
    """Własny iterator wczytujący i walidujący adresy URL z pliku konfiguracyjnego."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._urls = self._load_urls()
        self._index = 0

    def _load_urls(self) -> list[str]:
        """Wczytuje linie z pliku i filtruje tylko poprawne adresy URL."""
        valid_urls = []
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                for line in file:
                    clean_url = line.strip()
                    if clean_url and is_valid_url(clean_url):
                        valid_urls.append(clean_url)
                    elif clean_url:
                        print(f"[Config Warning] Pominięto niepoprawny URL: {clean_url}")
        except FileNotFoundError:
            print(f"[Config Error] Nie znaleziono pliku: {self.filepath}")
        return valid_urls

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self) -> str:
        if self._index >= len(self._urls):
            raise StopIteration
        url = self._urls[self._index]
        self._index += 1
        return url


if __name__ == "__main__":
    print("--- Test iteratora konfiguracji ---")
    config = ServerConfigIterator("servers.txt")
    for server_url in config:
        print("Wczytano serwer:", server_url)