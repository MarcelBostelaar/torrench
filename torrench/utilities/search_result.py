

class SearchResult:
    def __init__(self, site: str, name: str, uploader: str, link: str, magnetlink: str, seeders: int, leechers: int):
        self.site = site
        self.name = name
        self.link = link
        self.magnet = magnetlink
        self.seeders = seeders
        self.leechers = leechers
        self.uploader = uploader



