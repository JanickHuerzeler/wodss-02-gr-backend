import json
import logging
import os

""" ConfigManager handles the configuration files and provides access where needed. """


class ConfigManager:
    __instance = None

    __configFilePath = None    
    __secret = None
    __server_config = None    
    __application_root = None

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ConfigManager.__instance is None:
            ConfigManager("config.json")
        return ConfigManager.__instance

    def __init__(self, config_path_string):
        if ConfigManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ConfigManager.__instance = self            
        self.logger = logging.getLogger('pywall.' + __name__)

        self.load_config(config_path_string)

    def load_config(self, config_path_string):
        self.__configFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_path_string)        

        with open(self.__configFilePath, 'r') as json_data:
            config = json.load(json_data)            
            self.__secret = config['secret']
            self.__server_config = config['server']            
            self.__application_root = config['application_root']


    def log_configfile_path(self):
        self.logger.info("ConfigFile-Path is: " + str(self.__configFilePath))    

    def get_secret(self):
        return self.__secret

    def get_server_config(self):
        return self.__server_config

    def get_application_root(self):
        return self.__application_root
