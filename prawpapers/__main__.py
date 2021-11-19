from prawpapers.scraper import Scraper
from prawpapers.Configuration.configurator import Configurator
from prawpapers.Configuration.logging_settings import LoggingSettings
from dependency_injector.wiring import Provide, inject
import logging
from prawpapers.DI.container import Container


@inject
def main(
        scraper: Scraper = Provide[Container.scraper],
        config: Configurator = Provide[Container.config],
        logging_settings: LoggingSettings = Provide[Container.logging_settings]) -> None:

    logging_settings.configure_logger()
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
