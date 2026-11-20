import re

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s\|\s(?P<url>https?://\S+)\s\|\s(?P<status>.+)$"
)

URL_VALIDATOR = re.compile(r"^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/.*)?$")


def is_valid_url(url: str) -> bool:
    """Sprawdza poprawność składni adresu URL za pomocą regex."""
    return re.fullmatch(URL_VALIDATOR, url) is not None


def read_logs_generator(filepath: str):
    """Leniwie wczytuje linie z pliku logów, oszczędzając pamięć RAM."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                yield line.strip()
    except FileNotFoundError:
        print(f"Plik {filepath} nie istnieje. Uruchom najpierw główny skrypt.")


def parse_logs(filepath: str):
    """Przetwarza strumień linii z generatora i wyciąga dane za pomocą regex."""
    non_empty_lines = (line for line in read_logs_generator(filepath) if line)

    for line in non_empty_lines:
        match = LOG_PATTERN.match(line)
        if match:
            yield match.groupdict()


if __name__ == "__main__":
    print("--- Test parsera logów ---")
    for parsed_entry in parse_logs("server_logs.txt"):
        print(parsed_entry)