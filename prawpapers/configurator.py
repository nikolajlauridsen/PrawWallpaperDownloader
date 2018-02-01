import configparser
import sys
import os
import qprompt

class Configurator:
    def __init__(self):
        self.config = configparser.ConfigParser()

        if not os.path.isfile('config.ini'):
            self.create_default_config()
        else:
            self.config.read('config.ini')

    def create_default_config(self):
        """Create a default config file in the current working directory"""
        self.config['DEFAULT'] = {'MinWidth'   : '1280',
                                  'MinHeight'  : '720',
                                  'Sub'        : 'wallpapers',
                                  'Limit'      : '25',
                                  'Clean'      : 'yes',
                                  'Sort'       : 'yes',
                                  'MaxAge'     : 'none',
                                  'Albums'     : 'yes',
                                  'Threads'    : '10'}
        self.config['user'] = {}
        self.save_config()

    def get_config(self):
        """Return user instance of the config, items in default and not in user
        will be carried into the user config object"""
        return self.config['user']

    @staticmethod
    def prompt_boolean(message):
        """
        Prompt the user for a boolean to be saved in config.ini, exits the 
        script if the user inputs an invalid value
        :param message: Message to be displayed
        :return: string boolean for .ini files
        """
        u_input = input(message + " yes/no: ").strip().lower()
        if u_input == "yes" or u_input == "no":
            return u_input
        else:
            sys.exit("Invalid input")

    def create_menu(self):
        menu = qprompt.Menu()
        for i, item in enumerate(self.config['user']):
            menu.add(str(i+1), item)
        menu.add(0, "Exit")
        return menu

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        menu = self.create_menu()
        selection = menu.show(returns="desc")
        print(selection)

    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def reset_config(self):
        for key in self.config['user']:
            try:
                self.config['user'].pop(key, None)
            except KeyError:
                pass
        self.save_config()
