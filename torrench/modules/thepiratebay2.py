from torrench.modules.basescraper import BaseScraper
from torrench.utilities.search_result import SearchResult
from torrench.utilities.print_utils import colorify, Colors
from torrench.globals import logger
from torrench.utilities.http_utils import http_request
import sys

from typing import List

searchurlbase = "/search/%s/%d/99/0"
top = "/top/all"
top48 = "/top/48hall"
timeout_fetch_s = 15
sitename = "The Pirate Bay"

class ThePirateBay2(BaseScraper):

    def __init__(self, proxies):
        self.temp = 1
        validproxies = self.check_proxies(proxies, lambda soup: soup.a.string != 'The Pirate Bay')
        if len(validproxies) > 0:
            self.active_proxy = validproxies[0]
        else:
            self.active_proxy = None

    def search(self, title, pages) -> List[SearchResult]:
        searchurls = []
        if title is not None:
            searchurls = [searchurlbase % (title, page) for page in range(pages)]
        else:
            print(colorify(Colors.Green, "\n\n*Top 100 TPB Torrents*"))
            print("1. Top (ALL)\n2. Top (48H)\n")
            option = int(input("Option: "))
            if option == 1:
                logger.debug("Selected [TOP-ALL] (Option: %d)" % option)
                searchurls = [top]
            elif option == 2:
                logger.debug("Selected [TOP-48h] (Option: %d)" % option)
                searchurls = [top48]
            else:
                print("Bad Input! Exiting!")
                sys.exit(2)
        html = [http_request(x, timeout_fetch_s) for x in searchurls]
        return self.__parsehtml(html)

    def can_search(self):
        return self.active_proxy is not None

    @staticmethod
    def __parsehtml(pages) -> List[SearchResult]:
        content = [page.find('table', id="searchResult") for page in pages]
        data = [x.find_all('tr') for x in content]
        data = [[ThePirateBay2.__parse_dataentry(entry) for entry in page[1:]] for page in data]

    @staticmethod
    def __parse_dataentry(entry) -> SearchResult:
        name = entry.find('a', class_='detLink').string
        if name is None:
            name = entry.find('a', class_='detLink')['title'].split(" ")[2:]
            name = " ".join(str(x) for x in name)
        uploader = entry.find('font', class_="detDesc").a
        if uploader is None:
            uploader = entry.find('font', class_="detDesc").i.string
        else:
            uploader = uploader.string

        # figure out a way to do the comments, do the rest, expand searchresult

        comments = entry.find(
            'img', {'src': '//%s/static/img/icon_comment.gif' % (self.proxy.split('/')[2])})
        # Total number of comments
        if comments is None:
            comment = '0'
        else:
            comment = comments['alt'].split(" ")[-2]
        # See if uploader is VIP/Truested/Normal Uploader
        self.non_color_name = name
        is_vip = i.find('img', {'title': "VIP"})
        is_trusted = i.find('img', {'title': 'Trusted'})
        if (is_vip is not None):
            name = self.colorify("green", name)
            uploader = self.colorify("green", uploader)
        elif (is_trusted is not None):
            name = self.colorify("magenta", name)
            uploader = self.colorify("magenta", uploader)
        categ = i.find('td', class_="vertTh").find_all('a')[0].string
        sub_categ = i.find('td', class_="vertTh").find_all('a')[1].string
        seeds = i.find_all('td', align="right")[0].string
        leeches = i.find_all('td', align="right")[1].string
        date = i.find('font', class_="detDesc").get_text().split(' ')[1].replace(',', "")
        size = i.find('font', class_="detDesc").get_text().split(' ')[3].replace(',', "")
        seeds_color = self.colorify("green", seeds)
        leeches_color = self.colorify("red", leeches)
        # Unique torrent id
        torr_id = i.find('a', {'class': 'detLink'})["href"].split('/')[2]
        # Upstream torrent link
        link = "%s/torrent/%s" % (self.proxy, torr_id)
        magnet = i.find_all('a', {'title': 'Download this torrent using magnet'})[0]['href']