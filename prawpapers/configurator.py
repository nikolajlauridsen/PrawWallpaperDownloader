import configparser
import sys
import os

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
                                  'Albums'     : 'yes'}
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

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        print('Choose setting to change')
        print('\nConfig menu:')
        print('1) Minimum width: {}\n2) Minimum height: {}\n'
              '3) Post limit: {}\n4) Default subreddit: {}\n'
              '5) Clean: {}\n6) Sort: {}\n7) Max Age: {}\n'
              '8) Download albums: {}\n9) Reset to default\n10) Exit'
              .format(self.config['user']['MinWidth'],
                      self.config['user']['MinHeight'],
                      self.config['user']['Limit'],
                      self.config['user']['Sub'],
                      self.config['user']['Clean'],
                      self.config['user']['Sort'],
                      self.config['user']['MaxAge'],
                      self.config['user']['Albums']))

        u_input = input('Menu: ')
        if u_input == '1':
            self.config['user']['MinWidth'] = input('New minimum width: ')
            self.save_config()
        elif u_input == '2':
            self.config['user']['MinHeight'] = input('New minimum height: ')
            self.save_config()
        elif u_input == '3':
            self.config['user']['Limit'] = input('New post limit: ')
            self.save_config()
        elif u_input == '4':
            self.config['user']['Sub'] = input('New default subreddit: ')
            self.save_config()
        elif u_input == '5':
            self.config['user']['Clean'] = self.prompt_boolean("Clean")
            self.save_config()
        elif u_input == '6':
            self.config['user']['Sort'] = self.prompt_boolean("Sort")
            self.save_config()
        elif u_input == '7':
            self.config['user']['MaxAge'] = input('New max age: ')
            self.save_config()
        elif u_input == '8':
            self.config['user']['Albums'] = self.prompt_boolean("Download albums")
            self.save_config()
        elif u_input == '9':
            self.reset_config()
        elif u_input == '10':
            self.save_config()
        else:
            print('Invalid input')

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
