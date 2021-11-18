from dependency_injector import containers, providers
from ..Configuration.configurator import Configurator
from ..scraper import Scraper


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Configurator)
    scraper = providers.Singleton(Scraper,
                                  configurator=config)

