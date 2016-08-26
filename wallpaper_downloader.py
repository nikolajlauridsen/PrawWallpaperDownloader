from scraper import Scraper
scraper = Scraper()

if scraper.args.redownload:
    scraper.re_download()
else:
    scraper.run()
