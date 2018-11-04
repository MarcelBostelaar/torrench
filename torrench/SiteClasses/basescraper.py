from torrench.globals import logger
from torrench.utilities.search_result import SearchResult

from typing import List


class BaseScraper:

    """
    Takes a title to search, the number of pages to search
    Returns list of search results
    Needs to be overridden in inheriting class
    """
    def search(self, title: str, max_results: int) -> List[SearchResult]:
        logger.debug("Search is not implemented in {}".format(self.__class__.__name__))
        raise NotImplementedError("Search is not implemented in {}".format(self.__class__.__name__))

    """
    Returns a boolean indicating if it is able to search or not
    Needs to be overridden in inheriting class
    """
    def can_search(self) -> bool:
        logger.debug("Cansearch is not implemented in {}".format(self.__class__.__name__))
        raise NotImplementedError("Cansearch is not implemented in {}".format(self.__class__.__name__))