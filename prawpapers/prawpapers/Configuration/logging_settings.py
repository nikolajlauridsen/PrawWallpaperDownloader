from .argument_parser import ArgumentParser
import logging
import os
import sys


class LoggingSettings:
    def __init__(self, args: ArgumentParser) -> None:
        self.__args = args.get_arguments()

    def configure_logger(self):
        handlers = []
        if self.__args.log:
            # Windows default encoding for text files isn't UTF-8 (it's ANSI afaik)
            # So we need to create a custom FileHandler which opens the text file in UTF-8
            file_handler = logging.FileHandler(filename='papers.log', mode='w', encoding="utf8")
            handlers.append(file_handler)
        if self.__args.verbose:
            # Create stream handler pointing to stdout (terminal) and add it to handlers.
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            handlers.append(stream_handler)
        elif not self.__args.log:
            handlers.append(logging.StreamHandler(stream=open(os.devnull, 'w', encoding="utf-8")))

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(message)s',
                            datefmt='%d/%m/%y %H:%M:%S:',
                            handlers=handlers)

        logging.info('Logger started')
        settings = "Arguments:\n"
        for key, val in zip(vars(self.__args).keys(), vars(self.__args).values()):
            settings += f"{key}: {val}\n"
        logging.info(settings)
