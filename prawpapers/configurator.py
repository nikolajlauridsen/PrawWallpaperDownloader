import configparser
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
        self.config['DEFAULT'] = {'MinWidth' : '1280',
                                  'MinHeight': '720',
                                  'Sub'      : 'wallpapers',
                                  'Limit'    : '25',
                                  'Clean'    : 'yes',
                                  'Sort'     : 'yes',
                                  'Albums'   : 'yes'}
        self.config['user'] = {}
        self.save_config()

    def get_config(self):
        """Return user instance of the config, items in default and not in user
        will be carried into the user config object"""
        return self.config['user']

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        print('Choose setting to change')
        print('\nConfig menu:')
        print('1) Minimum width: {}\n2) Minimum height: {}\n'
              '3) Post limit: {}\n4) Default subreddit: {}\n'
              '5) Clean: {}\n6) Sort: {}\n7) Download albums: {}'
              '\n8) Reset to default\n9) Exit'
              .format(self.config['user']['MinWidth'],
                      self.config['user']['MinHeight'],
                      self.config['user']['Limit'],
                      self.config['user']['Sub'],
                      self.config['user']['Clean'],
                      self.config['user']['Sort'],
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
            self.config['user']['Clean'] = input('Clean yes/no: ')
            self.save_config()
        elif u_input == '6':
            self.config['user']['Sort'] = input('Sort yes/no: ')
            self.save_config()
        elif u_input == '7':
            self.config['user']['Albums'] = input('Download albums yes/no: ')
            self.save_config()
        elif u_input == '8':
            self.reset_config()
        elif u_input == '9':
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
