import configparser
import os

class Configurator():

    def __init__(self):
        self.config = configparser.ConfigParser()

        if not os.path.isfile('config.ini'):
            self.create_default_config()
        else:
            self.config.read('config.ini')

    def create_default_config(self):
        self.config['DEFAULT'] = {'MinWidth':  '1280',
                                  'MinHeight': '720',
                                  'Sub':       'wallpapers',
                                  'Limit':     '25',
                                  'Clean':     'yes',
                                  'Sort':      'yes'}
        self.config['user'] = {}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_config(self):
        return self.config['user']

    def menu(self):
        print('Choose setting to change')
        print('\nConfig menu:')
        print('1) Minimum width: {}\n2) Minimum height: {}\n'
              '3) Post limit: {}\n4) Default subreddit: {}\n'
              '5) Reset to default\n6) Exit'
              .format(self.config['user']['MinWidth'],
                      self.config['user']['MinHeight'],
                      self.config['user']['Limit'],
                      self.config['user']['Sub']))

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
            self.reset_config()
        elif u_input == '6':
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
