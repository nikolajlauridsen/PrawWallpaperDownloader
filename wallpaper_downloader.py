import argparse
from scraper import Scraper

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--subreddit", help="specify subreddit to scrape", default="wallpapers")
args = parser.parse_args()

scraper = Scraper(args)
scraper.run()
