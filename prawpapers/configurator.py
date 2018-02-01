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
        """
        Creates a qprompt menu and adds all items from config
        :return: qprompt menu
        """
        menu = qprompt.Menu()
        for i, item in enumerate(self.config['user']):
            menu.add(str(i+1), item)
        menu.add("0", "Exit")
        return menu

    def update_value(self, value):
        """
        Prompt the user to input a new value, then save the updated config
        and return to menu.
        Determines how to prompt the user by finding the value name passed as
        argument in one of the lists in the type map.
        :param value: value name to be updated e.g. minwidth
        """
        desc_str = "Enter new {} (currently {})".format(value, self.config['user'][value])
        if value in self.type_map["int"]:
            self.config['user'][value] = str(qprompt.ask_int(desc_str))
        elif value in self.type_map["string"]:
            self.config['user'][value] = qprompt.ask_str(desc_str)
        elif value in self.type_map["bool"]:
            desc_str += " yes/no"
            if qprompt.ask_yesno(desc_str):
                self.config['user'][value] = "yes"
            else:
                self.config['user'][value] = "no"

        self.save_config()
        self.clear_screen()
        print('Config saved...')
        self.menu()

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        menu = self.create_menu()
        selection = menu.show(returns="desc")
        if selection != "Exit":
            self.update_value(selection)

    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

