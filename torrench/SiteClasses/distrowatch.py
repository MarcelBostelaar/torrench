from torrench.SiteClasses.basescraper import BaseScraper
from torrench.globals import logger
from torrench.utilities.http_utils import http_request
from torrench.utilities.search_result import SearchResult
import re
from bs4 import Tag
from typing import List

siteurl = "https://distrowatch.com/dwres.php?resource=bittorrent"
timeout = 15


class DistroWatch(BaseScraper):


    def __init__(self):
        soup = http_request(siteurl, timeout)
        tables = [x for x in soup.findAll('table') if x.find('table') is None]  # only tables that do not contain tables
        rows = []
        for x in tables:
            rows += x.children  # add all child elements of tables to a one dimensional list
        rows = [x for x in rows if isinstance(x, Tag)]  # remove all elements that arent tags
        rows = [x for x in rows if x.find('td', 'torrent') is not None]  # remove all tags that do not contain a td with a property torrent
        self.data = [self.process_row(x) for x in rows]
        first = rows[0]
        i = 10

    @staticmethod
    def process_row(tag: Tag):
        children = list(tag.children)
        nametag = children[0]
        linktag = children[1]
        datetag = children[2]

        name = list(nametag.children)[2]
        link = "linkdummy"
        date = "dummy date"
        return name, link, date

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
