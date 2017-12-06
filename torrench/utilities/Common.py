"""Common Module - Used by all torrent-fetching modules."""
import inspect
import logging
import os
import platform
import subprocess
import sys
import time
import webbrowser
from configparser import SafeConfigParser

import colorama
import requests
from bs4 import BeautifulSoup

import pyperclip
from tabulate import tabulate


class Common:
    """
    Common class.

    This class consists common methods that are used by all the modules.

    methods:
    -- http_request_time():: Returns 'self.soup' as well as time taken to fetch URL.
    -- http_request():: Same as above. Only does not return time taken
    Also, time taken to fetch URL is returned.
    -- download():: To download .torrent file in $HOME/Downloads/torrench dir.
    -- colorify():: To return colored self.output
    -- show_output():: To display search results self.output (self.output table)
    -- copy_magnet():: To copy magnetic link to clipboard.
    --load_torrent():: To load torrent magnetic link to client.
    """

    def __init__(self):
        """Initialisations."""
        self.config = SafeConfigParser()
        self.config_dir = os.getenv('XDG_CONFIG_HOME', os.path.expanduser(os.path.join('~', '.config')))
        self.full_config_dir = os.path.join(self.config_dir, 'torrench')
        self.config_file_name = "torrench.ini"
        self.torrench_config_file = os.path.join(self.full_config_dir, self.config_file_name)
        self.raw = None
        self.soup = None
        self.output = None
        self.start_time = 0
        self.page_fetch_time = 0
        self.colors = {}
        self.logger = logging.getLogger('log1')
        self.OS_WIN = False
        if platform.system() == "Windows":
            self.OS_WIN = True

    def http_request_time(self, url):
        """
        http_request_time method.

        Used to fetch 'url' page and prepare soup.
        It also gives the time taken to fetch url.
        """
        try:
            try:
                headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"}
                self.start_time = time.time()
                self.raw = requests.get(url, timeout=15, headers=headers)
                self.page_fetch_time = time.time() - self.start_time
                self.logger.debug("returned status code: %d for url %s" % (self.raw.status_code, url))
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                self.logger.error(e)
                self.logger.exception("Stacktrace...")
                return -1
            except KeyboardInterrupt as e:
                self.logger.exception(e)
                print("\nAborted!\n")
            self.raw = self.raw.content
            self.soup = BeautifulSoup(self.raw, 'lxml')
            return self.soup, self.page_fetch_time
        except KeyboardInterrupt as e:
            print("Aborted!")
            self.logger.exception(e)
            sys.exit(2)

    def http_request(self, url):
        """
        http_request method.

        This method does not calculate time.
        Only fetches URL and prepares self.soup
        """
        try:
            try:
                self.raw = requests.get(url, timeout=15)
                self.logger.debug("returned status code: %d for url %s" % (self.raw.status_code, url))
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                self.logger.error(e)
                self.logger.exception("Stacktrace...")
                return -1
            self.raw = self.raw.content
            self.soup = BeautifulSoup(self.raw, 'lxml')
            return self.soup
        except KeyboardInterrupt as e:
            print("Aborted!")
            self.logger.exception(e)
            sys.exit(2)

    def download(self, dload_url, torrent_name, load):
        """
        Torrent download method.

        Used to download .torrent file.
        Torrent is downloaded in ~/Downloads/torrench/
        """
        try:
            mod = inspect.getmodulename(inspect.stack()[1][1])
            modules_to_exclude = ['linuxtracker', 'distrowatch']
            self.logger.debug("Download begins...")
            home = os.path.expanduser(os.path.join('~', 'Downloads'))
            downloads_dir = os.path.join(home, 'torrench')
            self.logger.debug("Default download directory: %s", (downloads_dir))
            if mod not in modules_to_exclude:
                downloads_dir = os.path.join(downloads_dir, mod)
            if not os.path.exists(downloads_dir):
                self.logger.debug("download directory does not exist.")
                os.makedirs(downloads_dir)
                self.logger.debug("created directory: %s", (downloads_dir))

            torrent_file = os.path.join(downloads_dir, torrent_name)
            with open(torrent_file, "wb") as file:
                print("Downloading torrent...")
                response = requests.get(dload_url)
                file.write(response.content)
                self.logger.debug("Download complete!")
                print("Download complete!")
                print("\nSaved in %s\n" % (downloads_dir))
                self.logger.debug("Saved in %s", (downloads_dir))
            # Load torrent to client
            if load == 1:
                if not self.OS_WIN:
                    self.load_torrent(torrent_file)
                else:
                    print("Sorry. Torrents cannot be loaded from hard drive to client in windows.")
                    print("This feature is not yet supported. More information about the same is available in docs.")
                    print("The torrent file has been downloaded and can be loaded to client manually.")
        except KeyboardInterrupt as e:
            self.logger.exception(e)
            print("\nAborted!\n")

    def colorify(self, color, text):
        """To return colored text."""
        colorama.init()
        self.colors = {
            "yellow": colorama.Fore.YELLOW + colorama.Style.BRIGHT,
            "green": colorama.Fore.GREEN + colorama.Style.BRIGHT,
            "magenta": colorama.Fore.MAGENTA + colorama.Style.BRIGHT,
            "red": colorama.Fore.RED + colorama.Style.BRIGHT,
            "cyan": colorama.Fore.CYAN + colorama.Style.BRIGHT,
            "reset": colorama.Style.RESET_ALL
        }
        text = self.colors[color] + text + self.colors["reset"]
        return text

    def show_output(self, masterlist, headers):
        """To display tabular output of torrent search."""
        try:
            masterlist = masterlist
            self.output = tabulate(masterlist, headers=headers, tablefmt="grid")
            if self.OS_WIN:
                self.output = self.output.encode('ascii', 'replace').decode()
            print("\n%s" % (self.output))
        except KeyboardInterrupt as e:
            self.logger.exception(e)
            print("\nAborted!\n")

    def after_output(self, site, oplist):
        """
        After output is displayed, Following text is displayed on console.

        Text includes instructions, total torrents fetched, total pages,
        and total time taken to fetch results.
        """
        total_torrent_count = oplist[0]
        total_fetch_time = oplist[1]
        # `max` is maximum number of torrents in 1 page
        if site == 'tpb' or site == 'kat':
            max = 30
        elif site == 'sky':
            max = 40
        elif site == 'x1337':
            max = 20
        elif site == 'idope':
            max = 10
        elif site == 'nyaa':
            max = 75
        else:
            max = total_torrent_count
        exact_no_of_pages = total_torrent_count // max
        has_extra_pages = total_torrent_count % max
        if has_extra_pages > 0:
            exact_no_of_pages += 1
        self.logger.debug("Total torrents: %d" % (total_torrent_count))
        self.logger.debug("Total fetch time: %.2f" % (total_fetch_time))
        self.logger.debug("Total pages: %d" % (exact_no_of_pages))
        try:
            print("\nTotal %d torrents [%d pages]" % (total_torrent_count, exact_no_of_pages))
            print("Total time: %.2f sec" % (total_fetch_time))
        except Exception as e:
            self.logger.exception(e)
            print("Error message: %s" %(e))
            print("Something went wrong! See logs for details. Exiting!")
            sys.exit(2)
    
    def select_index(self, len):
        """
        Select index method.

        Once output is displayed, specific torrent is selected using
        its corresponding index value.

        len is the total number of records fetched.
        Index starts from 0 upto len(total number of records.)

        The selected index is returned to to caller module.
        """
        self.logger.debug("Selecting torrent index")
        try:
            index = None
            while index != 'q':
                print("\nEnter torrent's INDEX value")
                index = input("\n(q = quit)\nindex > ")
                self.logger.debug("selected index %s" % (index))
                if index == 'q':
                    print("\nBye!")
                    self.logger.debug("Torrench quit!")
                    sys.exit(2)
                else:
                    index = int(index)
                if index < 1 or index > len:
                    self.logger.debug("Bad Input!")
                    print("\nBad Input!")
                    continue
                else:
                    return index
        except (ValueError, TypeError) as e:
            print("\nBad Input!")
            self.logger.exception(e)
            return 0

    def select_option(self, mapper, index, site):
        """
        Select option method.

        After index is selected, few options are displayed
        asking as to what to do with selected torrents.

        Options are as follows:
        [COMMON TO ALL MODULES/WEBSITES]
        [1] Print links (magnetic, upstream): Prints magnetic and upstream links
        on screen. Further, those links can be copied to clipboard
        [2] Load torrent to client: To load torrent to client from torrench
        [r] Return: To return to previous screen/options
        [q] Quit: To quit torrench

        [ONLY-FOR-TPB]
        [3] Get torrent details: To fetch torrent details and store those in a custom
        HTML page.
        """
        try:
            selected_torrent = mapper[index-1][0]
            self.logger.debug("selected torrent: %s ; index: %d" % (selected_torrent, index))
            selected_torrent_colored = self.colorify("yellow", selected_torrent)
            print("\nSelected index [%d] - %s\n" % (index, selected_torrent_colored))
            option_one = "[1] Print links (magnetic, upstream)\n"
            option_two = "[2] Load torrent to client\n"
            option_three = "[3] Get torrent details\n"
            option_return = "[r] Return\n"
            option_quit = "[q] Quit\n"
            if site == 'tpb':
                options = option_one + option_two + option_three + option_return + option_quit
            else:
                options = option_one + option_two + option_return + option_quit
            print(options)
            self.logger.debug("Selecting option")
            opt = input("Option > ")
            self.logger.debug("Selected option: {}".format(opt))
            if opt == '':
                raise ValueError
            elif opt in 'rR':
                self.logger.debug(option_return)
                return
            elif opt in 'qQ':
                self.logger.debug("Torrench quit!")
                print("\nBye!\n")
                sys.exit(2)
            else:
                opt = int(opt)
                if opt == 1:
                    self.logger.debug(option_one)
                    magnetic_link, torrent_link = self.get_links(mapper, index, site)
                    self.print_links(magnetic_link, torrent_link)
                elif opt == 2:
                    self.logger.debug(option_two)
                    magnetic_link, torrent_link = self.get_links(mapper, index, site)
                    self.load_torrent(magnetic_link)
                
                # Fetch TPB torrent details. fetch_tpb_details is defined in Common.py file itself.
                elif opt == 3 and site == 'tpb':
                    self.logger.debug(option_three)
                    magnetic_link, torrent_link = self.get_links(mapper, index, site)
                    print("Fetching details for torrent index [{}]: {}".format(index, selected_torrent))
                    file_url = self.fetch_tpb_details(torrent_link, index)
                    file_url_color = self.colorify("yellow", file_url)
                    print("File URL: {}".format(file_url_color))
                    self.copylink_clipboard(file_url)
                else:
                    raise ValueError
            self.select_option(mapper, index, site)
        except (ValueError, TypeError) as e:
                print("\nBad Input!\n")
                self.logger.exception(e)
                self.select_option(mapper, index, site)
    
    def get_links(self, mapper, index, site):
        """
        Get links method.

        This method fetches and returns magnetic/upstream links.
        """
        try:
            self.logger.debug("Fetching magnetic and upstream links for {}".format(site))
            if site in ['1337x', 'x1337']:
                torrent_link = mapper[index-1][-1]
                magnetic_link = self.get_1337x_magnet(torrent_link)
            else:
                torrent_link = mapper[index-1][-1]
                magnetic_link = mapper[index-1][-2]
            self.logger.debug("Links fetched successfully.")
            return magnetic_link, torrent_link
        except Exception as e:
            print("Something went wrong. See logs for details.")
            self.logger.exception(e)

    def print_links(self, req_magnetic_link, torrent_link):
        """
        Print links method.

        This method is called when option [1] is selected from select_option()
        method. Prints magnetic and upstream links on screen.

        Further, two more options are available:
        [1] Copy magnetic link to clipboard
        [2] Copy upstream Link to clipboard
        [r] Return: To return to previous screen.
        """
        try:
            self.logger.debug("Printing magnetic and upstream links")
            print("\nMagnetic link - %s" % (self.colorify("red",  req_magnetic_link)))
            print("\n\nUpstream link - %s\n" % (self.colorify("yellow", torrent_link)))
            option_one = "[1] Copy magnetic link to clipboard\n"
            option_two = "[2] Copy upstream Link to clipboard\n"
            option_return = "[r] Return\n"
            options = option_one + option_two + option_return
            print(options)
            try:
                opt = input("Option > ")
                self.logger.debug("Selected option: {}".format(opt))
                if opt == '':
                    raise ValueError
                elif opt in 'rR':
                    self.logger.debug(option_return)
                    return
                else:
                    opt = int(opt)
                    if opt == 1:
                        self.logger.debug("{}: {}".format(opt, option_one))
                        self.copylink_clipboard(req_magnetic_link)
                    elif opt == 2:
                        self.logger.debug("{}: {}".format(opt, option_two))
                        self.copylink_clipboard(torrent_link)
                    else:
                        raise ValueError
            except (ValueError, TypeError) as e:
                    print("\nBad Input!\n")
                    self.logger.exception(e)
                    self.print_links(req_magnetic_link, torrent_link)
        except Exception as e:
            print("Something went wrong. See logs for details.")
            self.logger.exception(e)
            return

    def copylink_clipboard(self, link):
        """Copy Magnetic/Upstream link to clipboard"""
        try:
            self.logger.debug("Copying magnetic/upstream link to clipboard")
            pyperclip.copy(link)
            self.logger.debug("Copied successfully.")
            message = "Link copied to clipboard.\n"
            print(self.colorify("green", message))
        except Exception as e:
            print("Something went wrong.")
            print("Please make sure [xclip] package is installed.")
            print("See logs for details.\n\n")
            self.logger.error(e)

    def get_1337x_magnet(self, link):
        """Module to get magnetic link of torrent.

        Magnetic link is fetched from torrent's info page.
        """
        print("Fetching magnetic link...")
        self.logger.debug("Fetching magnetic link")
        soup = self.http_request(link)
        magnet = soup.find('ul', class_="download-links-dontblock").a['href']
        return magnet

    def fetch_tpb_details(self, link, index):
        """
        Fetch TPB torrent details and save it in custom HTML file.
        
        The file is stored in hard-drive with link printed and copied to clipboard
        automatically.
        """
        import torrench.modules.tpb_details as tpb_details
        self.logger.debug("fetching torrent details...")
        file_url = tpb_details.get_details(link, str(index))
        self.logger.debug("details fetched. saved in %s" % (file_url))
        return file_url

    def copy_magnet(self, link):
        """Copy magnetic link to clipboard.
        
        This method is different from copylink_clipboard().
        This method handles the --copy argument.

        If --copy argument is supplied, magnetic link is copied to clipboard.
        """
        from torrench.Torrench import Torrench
        tr = Torrench()
        if tr.check_copy():
            try:
                pyperclip.copy(link)
                print("(Magnetic link copied to clipboard)")
            except Exception as e:
                print("(Unable to copy magnetic link to clipboard. Is [xclip] installed?)")
                print("(See logs for details)")
                self.logger.error(e)
        else:
            print("(use --copy to copy magnet to clipboard)")

    def load_torrent(self, link):
        """Load torrent (magnet) to client."""
        try:
            if not self.OS_WIN:
                """
                [LINUX / MacOS]

                Requires config file to be setup.
                Default directory: $XDG_CONFIG_HOME/torrench,
                Fallback: $HOME/.config/torrench
                file name: torrench.ini
                Complete path: $HOME/.config/torrench/torrench.ini
                """
                if os.path.isfile(self.torrench_config_file):
                    self.logger.debug("torrench.ini file exists")
                    self.config.read(self.torrench_config_file)
                    client = self.config.get('Torrench-Config', 'CLIENT')
                    client = client.lower()
                    print("\n(%s)" % (client))
                    self.logger.debug("using client: %s" %(client))
                else:
                    print("No config (torrench.ini) file found!")
                    self.logger.debug("torrench.ini file not found!")
                    return
                """
                [client = Transmission (transmission-remote)]
                    > Load torrent to transmission client
                    > Torrent is added to daemon using `transmission-remote`.
                    > Requires running `transmission-daemon`.

                    1. For authentication:
                        $TR_AUTH environment variable is used.
                        [TR_AUTH="username:password"]
                    2. For SERVER and PORT:
                        Set the SERVER and PORT variables in torrench.ini file.

                    If None of the above are set, following default values are used:
                    DEFAULTS
                    Username - [None]
                    password - [None]
                    SERVER - localhost (127.0.0.1)
                    PORT - 9091
                """
                if client == 'transmission-remote':
                    server = self.config.get('Torrench-Config', 'SERVER')
                    port = self.config.get('Torrench-Config', 'PORT')
                    if server == '':
                        server = "localhost"
                    if port == '':
                        port = "9091"
                    connect = "%s:%s" % (server, port)
                    p = subprocess.Popen([client, connect, '-ne', '--add', link], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    e = p.communicate()  # `e` is a tuple.
                    error = e[1].decode('utf-8')
                    if error != '':
                        print(self.colorify("red", "[ERROR] %s" % (error)))
                        self.logger.error(error)
                    else:
                        print(self.colorify("green", "Success (PID: %d)") %(p.pid))
                        self.logger.debug("torrent added! (PID: %d)" %(p.pid))
                elif client == 'deluge-console':
                    p = subprocess.Popen([client, 'add', link], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                    print(self.colorify("green", "Success (PID: %d)") %(p.pid))
                    self.logger.debug("torrent added! (PID: %d)" %(p.pid))
                elif client == 'browser':
                    p = subprocess.Popen(['firefox', link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(self.colorify("green", "Success (PID: %d)") %(p.pid))
                    self.logger.debug("torrent added! (PID: %d)" %(p.pid))
                else:
                    """
                    Any other torrent client.
                    > Tested: transmission-gtk, transmission-qt
                    > Not tested, but should work: rtorrent, qbittorrent (please update me)
                    """
                    p = subprocess.Popen([client, link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
                    print(self.colorify("green", "Success (PID: %d)") %(p.pid))
                    self.logger.debug("torrent added! (PID: %d)" %(p.pid))
            else:
                """
                [WINDOWS]

                The magnetic link is added to web-browser.
                Web browser should be able to load torrent to client automatically
                """
                webbrowser.open_new_tab(link)
        except Exception as e:
            self.logger.exception(e)
            print(self.colorify("red",  "[ERROR]: %s") % (e))
