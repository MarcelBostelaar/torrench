"""nyaa.si module."""

import logging
import platform
import sys

from torrench.utilities.Config import Config


class NyaaTracker(Config):
    """
    Nyaa.si class.

    This class fetches results from nyaa.si
    and displays in tabular form.

    Known problems:
    - If the torrent name in the website is too long (200 chars+) the table will be displayed incorrectly in the terminal.
    Possible fixes:
    - Cut the name if the name is too big.
    """

    def __init__(self, title: str):
        """Class constructor"""
        Config.__init__(self)
        self.proxy = self.check_proxy('nyaa')
        self.title = title
        self.logger = logging.getLogger('log1')
        self.index = 0
        self.mapper = []
        self.search_parameter = "/?f=0&c=0_0&q={query}&s=seeders&o=desc".format(query=self.title)
        self.soup, self.total_fetch_time = self.http_request_time(self.proxy+self.search_parameter)
        self.OS_WIN = False
        if platform.system() == "Windows":
            self.OS_WIN = True
        self.output_headers = ['NAME', 'INDEX', 'SIZE', 'SE/LE']

    def check_proxy(self, proxy: str):
        """
        Check for proxies in the `config.ini` file.
        :params: proxy
        :returns: proxy on success, -1 on error
        """
        _torrench_proxies = self.get_proxies(proxy)
        counter = 0
        if _torrench_proxies:
            for proxy in _torrench_proxies:
                print("Testing: {proxy}".format(proxy=self.colorify("yellow", proxy)))
                proxy_soup = self.http_request(proxy+'/?f=0&c=0_0&q=hello&s=seeders&o=desc')
                self.logger.debug("Testing {proxy} as a possible candidate.".format(proxy=proxy))
                if not proxy_soup.find_all('td', {'colspan': '2'}):
                    print("{proxy} was a bad proxy. Trying next proxy.".format(proxy=proxy))
                    counter += 1
                    if counter == len(_torrench_proxies):
                        self.logger.debug("Proxy list finished. No valid proxies were found.")
                        print("Failed to find any valid proxies. Terminating.")
                        return -1
                else:
                    print("Proxy `{proxy}` is available. Connecting.".format(proxy=proxy))
                    self.logger.debug("Proxy `{proxy}` is a valid proxy.")
                    return proxy
        print("No proxies were given.")
        return -1

    def parse_name(self):
        """
        Parse torrent name
        """
        t_names = []
        for name in self.soup.find_all('td', {'colspan': '2'}):
            n = name.get_text().replace('\n', '')
            t_names.append(n)
        if t_names:
            return t_names
        print("\nYour search returned no results.\nIf you think this is a bug, report on the Torrench Github repo: https://github.com/kryptxy/torrench")
        sys.exit(2)

    def parse_urls(self):
        t_urls = []
        for url in self.soup.find_all('a'):
            try:
                if url.get('href').startswith('/download/'):
                    t_urls.append(self.colorify('yellow', 'https://nyaa.si'+url['href']))
            except AttributeError:
                pass
        return t_urls

    def parse_magnets(self):
        t_magnets = []
        for url in self.soup.find_all('a'):
            try:
                if url['href'].startswith('magnet:'):
                    t_magnets.append(url['href'])
            except KeyError:
                pass
        return t_magnets

    def parse_sizes(self):
        t_size = []
        for size in self.soup.find_all('td', {'class': 'text-center'}):
            if size.get_text().endswith(("GiB", "MiB")):
                if self.OS_WIN:
                    t_size.append(size.get_text())
                else:
                    t_size.append(self.colorify("yellow", size.get_text()))
            else:
                pass
        return t_size

    def parse_seeds(self):
        t_seeds = []
        for seed in self.soup.find_all('td', {'style': 'color: green;'}):
            t_seeds.append(self.colorify("green", seed.get_text()))
        return t_seeds

    def parse_leeches(self):
        t_leeches = []
        for leech in self.soup.find_all('td', {'style': 'color: red;'}):
            t_leeches.append(self.colorify("red", leech.get_text()))
        return t_leeches

    def fetch_results(self):
        """
        Fetch results for a given query.

        @datafanatic:
        Work in progress
        """
        print("Fetching results")
        self.logger.debug("Fetching...")
        self.logger.debug("URL: %s", self.url)
        try:
            name = self.parse_name()
            urls = self.parse_urls()
            sizes = self.parse_sizes()
            seeds = self.parse_seeds()
            leeches = self.parse_leeches()
            seedleech = []
            for seed, leech in zip(seeds, leeches):
                seedleech.append(seed + '/' + leech)
            magnets = self.parse_magnets()
            self.index = len(urls)
        except (KeyError, AttributeError) as e:
            print("Something went wrong. Logging and terminating.")
            self.logger.exception(e)
            print("OK. Terminating.")
        if self.index == 0:
            print("No results were found for the given query. Terminating")
            self.logger.debug("No results were found for `%s`.", self.title)
            return -1
        self.logger.debug("Results fetched. Showing table.")
        self.mapper.insert(self.index+1, (name, urls, magnets))
        return list(zip(name, ["--"+str(idx)+"--" for idx in range(1, self.index+1)], sizes, seedleech))

    def after_output_text(self):
        """
        After output is displayed, Following text is displayed on console.

        Text includes instructions, total torrents fetched and total time taken to fetch results.
        """
        oplist = [self.index, self.total_fetch_time]
        self.after_output('nyaa', oplist)
    
    def select_torrent(self):
        """
        Select torrent

        Torrent is selected using index value.
        All of its functionality is defined in Common.py file.
        """
        self.logger.debug("Output displayed. Selecting torrent")
        while True:
            index = self.select_index(len(self.mapper[0][0]))
            if index == 0:
                continue
            self.select_option(self.mapper, index, 'nyaa')


def main(title):
    """
    Execution will begin here.
    """
    try:
        print("\n[Nyaa.si]\n")
        nyaa = NyaaTracker(title.replace("\"", ""))
        results = nyaa.fetch_results()
        nyaa.show_output([result for result in results], nyaa.output_headers)
        nyaa.after_output_text()
        nyaa.select_torrent()
    except KeyboardInterrupt:
        nyaa.logger.debug("Interrupt detected. Terminating.")
        print("Terminated")


if __name__ == "__main__":
    print("Modules are not supposed to be run standalone.")