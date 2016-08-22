import argparse
from scraper import Scraper

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--subreddit", help="specify subreddit to scrape", default="wallpapers")
parser.add_argument("-l", "--limit", help="set amount of posts to sift through (default 25)", default=25, type=int)
parser.add_argument("--log", help="save a log of wallpapers downloaded/skipped/failed",
                    action="store_true", default=False)
parser.add_argument("-re", "--redownload", help="attempt to download all the links in the database",
                    action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="increase output detail", action="store_true",
                    default=False)
args = parser.parse_args()

scraper = Scraper(args)

if args.redownload:
    scraper.re_download()
else:
    scraper.run()
