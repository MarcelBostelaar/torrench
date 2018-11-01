import multiprocessing as mp
from torrench.utilities.http_utils import http_request
from torrench.globals import logger
from torrench.utilities.search_result import SearchResult
from bs4 import BeautifulSoup

from typing import List
proxy_timeout_s = 15


class BaseScraper:

    """Checks a list of proxies and returns a proxy that is valid"""
    @staticmethod
    def check_proxies(proxies: List[str], validityfunc) -> List[str]:
        output = mp.Queue()
        processes = [mp.Process(target=http_request, args=(proxy, proxy_timeout_s)) for proxy in proxies]

        # Run processes
        for p in processes:
            p.start()

        # Exit the completed processes
        for p in processes:
            p.join()

        # Get process results from the output queue
        results = [output.get() for p in processes]
        return [x for x in results if x is not None and validityfunc(x)]


    """
    Fetches a list of url strings and returns the soup
    """
    @staticmethod
    def fetch_pages(urls: List[str], timeout_fetch_seconds) -> List[BeautifulSoup]:
        #  Possible to parralellize this function similar to check_proxies
        return [http_request(x, timeout_fetch_seconds) for x in urls]


    """
    Takes a title to search, the number of pages to search
    Returns list of search results
    Needs to be overridden in inheriting class
    """
    def search(self, title, pages) -> List[SearchResult]:
        logger.debug("Search is not implemented in {}".format(self.__class__.__name__))
        raise NotImplementedError("Search is not implemented in {}".format(self.__class__.__name__))

    """
    Returns a boolean indicating if it is able to search or not
    Needs to be overridden in inheriting class
    """
    def can_search(self) -> bool:
        logger.debug("Cansearch is not implemented in {}".format(self.__class__.__name__))
        raise NotImplementedError("Cansearch is not implemented in {}".format(self.__class__.__name__))