import urllib.request

#funkcja sprawdzająca status serwera
def check_server_status(url):
    try:
        response = urllib.request.urlopen(url)
        status = response.getcode()
        print(f"Status serwera {url}: {status}")
    except Exception as e:
        print(f"Błąd podczas sprawdzania serwera {url}: {e}")

#lista serwerów do sprawdzenia
server_list = [
    "http://www.google.com",
    "http://www.wp.pl",
    "http://www.niedzialajacyserwer.pl"
]

for server in server_list:
    check_server_status(server)