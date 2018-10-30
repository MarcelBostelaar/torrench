from torrench.SiteClasses.basescraper import BaseScraper
from torrench.globals import logger
from torrench.utilities.http_utils import http_request
from torrench.utilities.search_result import SearchResult
import re
from typing import List

searchurlbase = "/search/%s/%d/99/0"
top = "/top/all"
top48 = "/top/48hall"
timeout_fetch_s = 15
sitename = "The Pirate Bay"


"""
A subclass of the search result class specifically for pirate bay results
Contains additional information:
 - number of comments
 - is the uploader trusted
 - is the uploader a VIP
 - category
 - subcategory
 - date
 - size
"""


class PirateBayResult(SearchResult):
    def __init__(self, name: str, uploader: str, link: str, magnetlink: str, seeders: int, leechers: int,
                 number_of_comments: int, is_trusted: bool, is_vip: bool,
                 category: str, subcategory: str, date: str, size: str):
        SearchResult.__init__(self, sitename, name, uploader, link, magnetlink, seeders, leechers)
        self.number_of_comments = number_of_comments
        self.is_trusted = is_trusted
        self.is_VIP = is_vip
        self.category = category
        self.subcategory = subcategory
        self.date = date
        self.size = size


"""
A scraper implementation for the pirate bay. 
Has additional methods top 48h and top100, which returns search results 
for the top of the past 48h and the top 100 torrents respectively.
"""


class ThePirateBay(BaseScraper):

    def __init__(self, proxies):
        validproxies = self.check_proxies(proxies, lambda soup: soup.a.string != 'The Pirate Bay')
        if len(validproxies) > 0:
            self.active_proxy = validproxies[0]
        else:
            self.active_proxy = None

    def search(self, title, pages) -> List[PirateBayResult]:
        if not self.can_search():
            search_message = "Cannot search the pirate bay"
            logger.debug(search_message)
            raise Exception(search_message)
        pages = [self.active_proxy + searchurlbase % (title, page) for page in range(pages)]
        return self.__parsehtml(self.fetch_pages(pages, timeout_fetch_s))

    def can_search(self):
        return self.active_proxy is not None

    def search_top48h(self) -> List[PirateBayResult]:
        return self.__parsehtml(self.fetch_pages([self.active_proxy + top48], timeout_fetch_s))

    def search_top100(self) -> List[PirateBayResult]:
        return self.__parsehtml(self.fetch_pages([self.active_proxy + top], timeout_fetch_s))

    def __parsehtml(self, pages) -> List[PirateBayResult]:
        content = [page.find('table', id="searchResult") for page in pages]
        data = [x.find_all('tr') for x in content]
        data = [[self.__parse_table_entry(entry) for entry in page[1:]] for page in data]
        flattened = []
        for i in data:
            flattened += i
        return flattened

    def __parse_table_entry(self, entry) -> PirateBayResult:
        name = entry.find('a', class_='detLink').string
        if name is None:
            name = entry.find('a', class_='detLink')['title'].split(" ")[2:]
            name = " ".join(str(x) for x in name)
        uploader = entry.find('font', class_="detDesc").a
        if uploader is None:
            uploader = entry.find('font', class_="detDesc").i.string
        else:
            uploader = uploader.string
        comment_regex = re.compile("This torrent has [\d] comments\.")
        comments = entry.find(
            'img', {'title': comment_regex})
        # Total number of comments
        if comments is None:
            num_of_comments = 0
        else:
            num_of_comments = int(comments['alt'].split(" ")[-2])
        # See if uploader is VIP/Truested/Normal Uploader
        is_vip = entry.find('img', {'title': "VIP"}) is not None
        is_trusted = entry.find('img', {'title': 'Trusted'}) is not None
        categ = entry.find('td', class_="vertTh").find_all('a')[0].string
        sub_categ = entry.find('td', class_="vertTh").find_all('a')[1].string
        seeds = int(entry.find_all('td', align="right")[0].string)
        leeches = int(entry.find_all('td', align="right")[1].string)
        date = entry.find('font', class_="detDesc").get_text().split(' ')[1].replace(',', "")
        size = entry.find('font', class_="detDesc").get_text().split(' ')[3].replace(',', "")
        # Unique torrent id
        torr_id = entry.find('a', {'class': 'detLink'})["href"].split('/')[2]
        # Upstream torrent link
        link = "%s/torrent/%s" % (self.active_proxy, torr_id)
        magnet = entry.find_all('a', {'title': 'Download this torrent using magnet'})[0]['href']

        return PirateBayResult(name, uploader, link, magnet, seeds, leeches, num_of_comments,
                               is_trusted, is_vip, categ, sub_categ, date, size)
