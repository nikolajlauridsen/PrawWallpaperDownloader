from scraper import Scraper
from configurator import Configurator

scraper = Scraper()

if scraper.args.redownload:
    scraper.re_download()
elif scraper.args.configure:
    config = Configurator()
    config.menu()
else:
    scraper.run()
