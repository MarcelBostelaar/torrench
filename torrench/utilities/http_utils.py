import requests
from bs4 import BeautifulSoup
import sys
from torrench.globals import logger
from typing import Union
from multiprocessing import Queue


def http_request_multi(url: str, timeout_seconds: int, queue: Queue):
    result = http_request(url, timeout_seconds)
    if result is not None:
        queue.put(result)
    print("Finished thread")


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
