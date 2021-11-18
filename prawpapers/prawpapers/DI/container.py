from dependency_injector import containers, providers
from ..Configuration.configurator import Configurator
from ..Configuration.argument_parser import ArgumentParser
from ..scraper import Scraper


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Configurator)
    argument_parser = providers.Singleton(ArgumentParser,
                                          configurator=config)

    scraper = providers.Singleton(Scraper,
                                  configurator=config,
                                  argument_parser=argument_parser)

