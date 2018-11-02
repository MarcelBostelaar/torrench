from torrench.SiteClasses.basescraper import BaseScraper
from torrench.globals import logger
from torrench.utilities.http_utils import http_request
from torrench.utilities.search_result import SearchResult
import re
from bs4 import Tag, NavigableString
from typing import List

siteurl = "https://distrowatch.com/dwres.php?resource=bittorrent"
sitename = "Distro Watch"
timeout = 15


class DistroWatchResult(SearchResult):
    def __init__(self, name: str, link: str, date: str):
        SearchResult.__init__(self, sitename, name, None, link, None, None, None)
        self.date = date

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

    @staticmethod
    def process_row(tag: Tag):
        children = list(tag.children)
        nametag = children[0]
        linktag = children[1]
        datetag = children[3]

        name = list(nametag.children)[0]
        if not isinstance(name, NavigableString):  # case where no link exists
            name = [x for x in name if not isinstance(x, Tag)][0]
        link = list(linktag.children)[0]["href"]
        date = list(datetag.children)[0]
        return name, link, date

    """
    Takes a title to search, the number of pages to search
    Returns list of search results
    Needs to be overridden in inheriting class
    """
    def search(self, title : str, pages : int) -> List[DistroWatchResult]:
        matches = [x for x in self.data if title.lower() in x[0].lower()]
        return [DistroWatchResult(x[0], siteurl + x[1], x[2]) for x in matches]

    """
    Returns a boolean indicating if it is able to search or not
    Needs to be overridden in inheriting class
    """
    def can_search(self) -> bool:
        return self.data is not None
