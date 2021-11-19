from .configurator import Configurator
import argparse
import sys


class ArgumentParser():
    def __init__(self, configurator: Configurator) -> None:
        self.config = configurator.get_config()

    def parse_arguments(self):
        """Parse arguments from commandline"""
        parser = argparse.ArgumentParser()

        parser.add_argument("-s", "--subreddit",
                            help="specify subreddit to scrape",
                            default=self.config['Sub'])

        parser.add_argument("-se", "--section",
                            help="specify section of subreddit to scrape (hot, top, rising or new)",
                            default=self.config['section'])

        parser.add_argument("-l", "--limit",
                            help="set amount of posts to sift through "
                                 "(default " + self.config['Limit'] + ")",
                            default=int(self.config['Limit']), type=int)

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
                            help="Skip cleaning off small images (Cleaning: " + self.config['Clean'] + ")",
                            action="store_true", default=not self.config.getboolean('Clean'))

        parser.add_argument('-ns', '--nosort',
                            help="Skip sorting out previously downloaded images (Sorting: {})".format(
                                self.config['sort']),
                            action="store_true", default=not self.config.getboolean('Sort'))

        parser.add_argument('-na', '--noalbum', help='Skip imgur albums',
                            action='store_true', default=not self.config.getboolean('Albums'))

        parser.add_argument('-t', '--threads', help='Amount of threads for downloading images',
                            default=int(self.config['Threads']), type=int)

        parser.add_argument('-con', '--configure', help="Change settings",
                            action='store_true', default=False)

        parser.add_argument('-rlock', '--ratiolock',
                            help="Sort out images with incorrect aspect ratio, 0 for no lock, "
                                 "1 for full lock (Ratio lock: {})".format(self.config['ratiolock']),
                            default=float(self.config['ratiolock']), type=float)

        parser.add_argument('-q', '--search', help="Scrape by search term", default=False, type=str)

        arguments = parser.parse_args()
        if arguments.ratiolock < 0 or arguments.ratiolock > 1:
            sys.exit(f"Incorrect ratio lock, please keep it between 0.0 and 1.0 (Currently {arguments.ratiolock})")

        return arguments
