from prawpapers.scraper import Scraper
from prawpapers.Configuration.configurator import Configurator
from dependency_injector.wiring import Provide, inject
import logging
from prawpapers.DI.container import Container


@inject
def main(
        scraper: Scraper = Provide[Container.scraper],
        config: Configurator = Provide[Container.config]) -> None:
    if scraper.args.redownload:
        scraper.re_download()
    elif scraper.args.configure:
        config.menu()
    else:
        scraper.run()
    logging.info('Logger stopped')


if __name__ == '__main__':
    container = Container()
    container.wire(modules=[__name__])
    main()
