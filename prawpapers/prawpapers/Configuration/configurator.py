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

        self.type_map = {int: ["minwidth", "minheight", "limit", "threads",
                               "maxage"],
                         float: ["ratiolock"],
                         str: ["sub", "section"],
                         bool: ["clean", "sort", "albums"]
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
                                  'Threads'    : '10',
                                  'Section'    : 'hot',
                                  'RatioLock'  : '0.95'}
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
        menu.add("-1", "List settings")
        menu.add("-2", "Reset config")
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
        if value in self.type_map[int]:
            self.config['user'][value] = str(qprompt.ask_int(desc_str))
        elif value in self.type_map[float]:
            self.config['user'][value] = str(qprompt.ask_float(desc_str))
        elif value in self.type_map[str]:
            self.config['user'][value] = qprompt.ask_str(desc_str)
        elif value in self.type_map[bool]:
            desc_str += " y/n"
            if qprompt.ask_yesno(desc_str):
                self.config['user'][value] = "yes"
            else:
                self.config['user'][value] = "no"

        self.save_config()
        self.clear_screen()
        print('Config saved...')

    def list_settings(self):
        # Find the length of the longest key name
        pad = 0
        for key in self.config['user'].keys():
            if len(key) > pad:
                pad = len(key)
        pad += 1  # Add one to the padding, a little air is pretty
        # Clear screen and print all the settings as a pretty list.
        self.clear_screen()
        print('Current settings: ')
        for key in self.config['user']:
            print('{:{align}}: {}'.format(key, self.config['user'][key], align=pad))
        # Pause for the user to be able to read the settings.
        input('\nPress enter to return to menu.')

    def menu(self):
        """Run the configurator menu allowing user to edit config"""
        menu = self.create_menu()
        selection = menu.show(returns="desc")

        if selection == "Reset config":
            answer = qprompt.ask_yesno("Are you sure you want to reset your config? y/n")
            if answer:
                self.create_default_config()
                print("Config reset.")
            else:
                print('Reset canceled')
        elif selection == "List settings":
            self.list_settings()
            self.clear_screen()
            self.menu()
        elif selection == "Exit":
            pass
        else:
            self.update_value(selection)
            self.menu()

    def save_config(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

