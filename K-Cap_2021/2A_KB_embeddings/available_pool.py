import requests
import xmltodict

def main():

    queries = [
        'type=artikel AND date within "1890-01-01 1899-12-31"',
        'type=artikel AND date within "1900-01-01 1909-12-31"',
        'type=artikel AND date within "1910-01-01 1919-12-31"',
        'type=artikel AND date within "1920-01-01 1929-12-31"',
        'type=artikel AND date within "1930-01-01 1939-12-31"',
        'type=artikel AND date within "1940-01-01 1941-12-31"',
    ]

    for query in queries:
        available_pool: int = get_jsru_match_count(query)
        print(f"{query}, available pool = {available_pool}")


def get_jsru_match_count(query: str) -> int:
    """Return match count for query passed to http://jsru.kb.nl."""
    base_url = (
        "http://jsru.kb.nl/sru/sru?version=1.2"
        + "&operation=searchRetrieve"
        + "&x-collection=DDD_artikel&"
        + "recordSchema=dc"
    )

    r = get_response(base_url + "&startRecord=1&maximumRecords=1" + f"&query={(query)}")
    r: dict = xmltodict.parse(r.text)
    num_articles: int = int(r["srw:searchRetrieveResponse"]["srw:numberOfRecords"])

    return num_articles


def get_response(url: str, *, max_attempts=5) -> requests.Response:
    """Return the response.

    Tries to get response max_attempts number of times, otherwise return None

    Args:
       url (str): url string to be retrieved
       max_attemps (int): number of request attempts for same url

    E.g.,
        r = get_response(url)
        r = xmltodict.parse(r.text)
        # or
        r = json.load(r.text)
    """
    for count, x in enumerate(range(max_attempts)):
        try:
            response = requests.get(url, timeout=10)
            return response
        except:
            time.sleep(0.01)
    # if count exceeded
    return None


if __name__ == "__main__":
    main()
