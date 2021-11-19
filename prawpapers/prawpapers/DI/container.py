from dependency_injector import containers, providers
from ..Configuration.configurator import Configurator
from ..Configuration.argument_parser import ArgumentParser
from ..Configuration.logging_settings import LoggingSettings
from ..Persistance.db_handler import DbHandler
from ..scraper import Scraper


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Configurator)
    argument_parser = providers.Singleton(ArgumentParser,
                                          configurator=config)
    logging_settings = providers.Singleton(LoggingSettings,
                                           args=argument_parser)

    database = providers.Singleton(DbHandler)

    scraper = providers.Singleton(Scraper,
                                  configurator=config,
                                  argument_parser=argument_parser,
                                  database=database)

