from scraper import Scraper
from configurator import Configurator

scraper = Scraper()


def main():
    if scraper.args.redownload:
        scraper.re_download()
    elif scraper.args.configure:
        config = Configurator()
        config.menu()
    else:
        scraper.run()

if __name__ == '__main__':
    main()
