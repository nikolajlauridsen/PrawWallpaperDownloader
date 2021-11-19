from .configurator import Configurator
import argparse
import sys


class ArgumentParser:
    def __init__(self, configurator: Configurator) -> None:
        self.__config = configurator.get_config()
        self.__arguments = None

    def get_arguments(self):
        """Get the arguments parsed from the commandline"""
        if self.__arguments is None:
            self.__arguments = self.__parse_arguments()
        return self.__arguments

    def __parse_arguments(self):
        """Parse arguments from commandline"""
        parser = argparse.ArgumentParser()

        parser.add_argument("-s", "--subreddit",
                            help="specify subreddit to scrape",
                            default=self.__config['Sub'])

        parser.add_argument("-se", "--section",
                            help="specify section of subreddit to scrape (hot, top, rising or new)",
                            default=self.__config['section'])

        parser.add_argument("-l", "--limit",
                            help="set amount of posts to sift through "
                                 "(default " + self.__config['Limit'] + ")",
                            default=int(self.__config['Limit']), type=int)

        parser.add_argument("--log",
                            help="save a log of wallpapers downloaded/skipped/failed",
                            action="store_true", default=False)

        parser.add_argument("-re", "--redownload",
                            help="attempt to download all the links in the database",
                            action="store_true", default=False)

        parser.add_argument("-v", "--verbose", help="increase output detail",
                            action="store_true",
                            default=False)

        parser.add_argument('-nc', "--noclean",
                            help="Skip cleaning off small images (Cleaning: " + self.__config['Clean'] + ")",
                            action="store_true", default=not self.__config.getboolean('Clean'))

        parser.add_argument('-ns', '--nosort',
                            help="Skip sorting out previously downloaded images (Sorting: {})".format(
                                self.__config['sort']),
                            action="store_true", default=not self.__config.getboolean('Sort'))

        parser.add_argument('-na', '--noalbum', help='Skip imgur albums',
                            action='store_true', default=not self.__config.getboolean('Albums'))

        parser.add_argument('-t', '--threads', help='Amount of threads for downloading images',
                            default=int(self.__config['Threads']), type=int)

        parser.add_argument('-con', '--configure', help="Change settings",
                            action='store_true', default=False)

        parser.add_argument('-rlock', '--ratiolock',
                            help="Sort out images with incorrect aspect ratio, 0 for no lock, "
                                 "1 for full lock (Ratio lock: {})".format(self.__config['ratiolock']),
                            default=float(self.__config['ratiolock']), type=float)

        parser.add_argument('-q', '--search', help="Scrape by search term", default=False, type=str)

        arguments = parser.parse_args()
        if arguments.ratiolock < 0 or arguments.ratiolock > 1:
            sys.exit(f"Incorrect ratio lock, please keep it between 0.0 and 1.0 (Currently {arguments.ratiolock})")

        return arguments
