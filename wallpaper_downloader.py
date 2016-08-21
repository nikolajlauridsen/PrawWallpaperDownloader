import argparse
from scraper import Scraper

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--subreddit", help="specify subreddit to scrape")
args = parser.parse_args()

if args.subreddit:
    scraper = Scraper(sub=args.subreddit)
else:
    scraper = Scraper()
scraper.run()
