import requests
from bs4 import BeautifulSoup
import sys
from torrench.globals import logger
from typing import Union, List, Tuple
from multiprocessing import Queue
import multiprocessing as mp

proxy_timeout_s = 15


def http_request(url: str, timeout_seconds: int) -> Union[None, BeautifulSoup]:
    """
    http_request method.

    This method does not calculate time.
    Only fetches URL and returns soup
    """
    try:
        try:
            raw = requests.get(url, timeout=timeout_seconds)
            logger.debug("returned status code: %d for url %s" % (raw.status_code, url))
        except:
            return None
        raw = raw.content
        soup = BeautifulSoup(raw, 'lxml')
        return soup
    except KeyboardInterrupt as e:
        print("Aborted!")
        logger.exception(e)
        sys.exit(2)


def http_check(url: str, timeout_seconds: int) -> bool:
    """Checks if a webpage can be reached without parsing it"""
    try:
        try:
            raw = requests.get(url, timeout=timeout_seconds)
            logger.debug("returned status code: %d for url %s" % (raw.status_code, url))
        except:
            return False
        return True
    except KeyboardInterrupt as e:
        print("Aborted!")
        logger.exception(e)
        sys.exit(2)


def check_proxy_multithread(url: str, timeout_seconds: int, queue: Queue):
    """Checks if proxies can be reached
    Puts proxy link in queue if reachable, puts None if not reachable"""
    if http_check(url, timeout_seconds):
        queue.put(url)
    else:
        queue.put(None)


def check_proxies(proxies: List[str], validityfunc) -> List[str]:
    """Checks a list of proxies and returns a proxy that is valid"""
    manager = mp.Manager()
    output = manager.Queue()
    processes = [mp.Process(target=check_proxy_multithread, args=(proxy, proxy_timeout_s, output)) for proxy in proxies]

    # Run processes
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    # Get process results from the output queue
    results = [output.get() for p in processes]  # check if value is available instead of doing all threads
    results = [x for x in results if x is not None]  # filter out nones
    pages = fetch_pages_withurl(results, proxy_timeout_s)
    return [page[0] for page in pages if page[1] is not None and validityfunc(page[1])]


def fetch_pages(urls: List[str], timeout_fetch_seconds: int) -> List[BeautifulSoup]:
    """
    Fetches a list of url strings and returns the soup
    """
    #  Cannot parrallize this function until pickle can handle beautifullsoup objects
    return [http_request(x, timeout_fetch_seconds) for x in urls]


def fetch_pages_withurl(urls: List[str], timeout_fetch_seconds: int) -> List[Tuple[str, BeautifulSoup]]:
    """
    Fetches a list of url strings and returns the tuple with the url and soup
    """
    #  Cannot parrallize this function until pickle can handle beautifullsoup objects
    return [(x, http_request(x, timeout_fetch_seconds)) for x in urls]
