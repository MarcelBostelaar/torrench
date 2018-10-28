import colorama
from enum import Enum


class Colors(Enum):
    Yellow = colorama.Fore.YELLOW + colorama.Style.BRIGHT
    Green = colorama.Fore.GREEN + colorama.Style.BRIGHT
    Magenta = colorama.Fore.MAGENTA + colorama.Style.BRIGHT
    Red = colorama.Fore.RED + colorama.Style.BRIGHT
    Cyan = colorama.Fore.CYAN + colorama.Style.BRIGHT
    Reset = colorama.Style.RESET_ALL


def colorify(color: Colors, text):
    return color + text + Colors.Reset
