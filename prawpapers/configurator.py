import configparser
import os
import qprompt

class Configurator:
    def __init__(self):
        self.config = configparser.ConfigParser()

        if not os.path.isfile('config.ini'):
            self.create_default_config()
        else:
            self.config.read('config.ini')

        self.type_map = {"int": ["minwidth", "minheight", "limit", "threads",
                                 "maxage"],
                         "string": ["sub"],
                         "bool": ["clean", "sort", "albums"]
                         }

    def create_default_config(self):
        """Create a default config file in the current working directory"""
        self.config['DEFAULT'] = {'MinWidth'   : '1280',
                                  'MinHeight'  : '720',
                                  'Sub'        : 'wallpapers',
                                  'Limit'      : '25',
                                  'Clean'      : 'yes',
                                  'Sort'       : 'yes',
                                  'MaxAge'     : '0',
                                  'Albums'     : 'yes',
                                  'Threads'    : '10'}
        self.config['user'] = {}
        self.save_config()

    def get_config(self):
        """Return user instance of the config, items in default and not in user
        will be carried into the user config object"""
        return self.config['user']

    @staticmethod
    def clear_screen():
        """Clears the commandline window"""
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def create_menu(self):
        menu = qprompt.Menu()
        for i, item in enumerate(self.config['user']):
            menu.add(str(i+1), item)
        menu.add("0", "Exit")
        return menu

    def update_value(self, value):
        desc_str = "Enter new {} (currently {})".format(value, self.config['user'][value])
        if value in self.type_map["int"]:
            self.config['user'][value] = str(qprompt.ask_int(desc_str))
        elif value in self.type_map["string"]:
            self.config['user'][value] = qprompt.ask_str(desc_str)
        elif value in self.type_map["bool"]:
            if qprompt.ask_yesno(desc_str):
                self.config['user'][value] = "yes"
            else:
                self.config['user'][value] = "no"
        self.save_config()
        print('Config saved...')
        self.clear_screen()
        self.menu()

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        menu = self.create_menu()
        selection = menu.show(returns="desc")
        print(selection)
        if selection != "Exit":
            self.update_value(selection)

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
