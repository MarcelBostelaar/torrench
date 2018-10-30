from torrench.SiteClasses.basescraper import BaseScraper
from torrench.globals import logger
from torrench.utilities.http_utils import http_request
from torrench.utilities.search_result import SearchResult
import re
from typing import List

siteurl = "https://distrowatch.com/dwres.php?resource=bittorrent"
timeout = 15


class DistroWatch(BaseScraper):


    def __init__(self):
        soup = http_request(siteurl, timeout)
        rows = soup.find_all(lambda x: x.find('td', 'torrent') is not None)
        # parse into tuples/dictionary
        # check with "title in name"

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
        return self.soup is not None
