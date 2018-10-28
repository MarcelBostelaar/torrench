import requests
from bs4 import BeautifulSoup
import sys
from torrench.globals import logger


def http_request(url, timeout_seconds):
    """
    http_request method.

    This method does not calculate time.
    Only fetches URL and returns soup
    """
    try:
        try:
            raw = requests.get(url, timeout=timeout_seconds)
            logger.debug("returned status code: %d for url %s" % (raw.status_code, url))
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            logger.error(e)
            logger.exception("Stacktrace...")
            return None
        raw = raw.content
        soup = BeautifulSoup(raw, 'lxml')
        return soup
    except KeyboardInterrupt as e:
        print("Aborted!")
        logger.exception(e)
        sys.exit(2)
