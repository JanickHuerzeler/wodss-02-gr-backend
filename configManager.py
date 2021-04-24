import json
import logging
import os

""" ConfigManager handles the configuration files and provides access where needed. """


class ConfigManager:
    __instance = None

    __configFilePath = None
    __secret = None
    __server_config = None
    __required_date_format = None
    __application_root = None
    __cantonservice_urls = None
    __geoservice_url = None
    __geoservice_search_radius = None
    __incidence_retry_days = None
    __nth_waypoint_filter = None
    __use_local_geo_data = None

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
            self.__required_date_format = str(config['requiredDateFormat'])
            self.__application_root = config['application_root']
            self.__cantonservice_urls = config['cantonservice_urls']
            self.__geoservice_url = config['geoservice_url']
            self.__geoservice_search_radius = config['geoservice_search_radius']
            self.__incidence_retry_days = config['incidence_retry_days']
            self.__nth_waypoint_filter = config['nth_waypoint_filter']
            self.__use_local_geo_data = config['use_local_geo_data']

    def log_configfile_path(self):
        self.logger.info("ConfigFile-Path is: " + str(self.__configFilePath))

    def get_secret(self):
        return self.__secret

    def get_server_config(self):
        return self.__server_config

    def get_required_date_format(self):
        return self.__required_date_format

    def get_application_root(self):
        return self.__application_root

    def get_cantonservice_urls(self):
        return self.__cantonservice_urls

    def get_geoservice_url(self):
        return self.__geoservice_url

    def get_geoservice_search_radius(self):
        return self.__geoservice_search_radius

    def get_incidence_retry_days(self):
        return self.__incidence_retry_days

    def get_nth_waypoint_filter(self):
        return self.__nth_waypoint_filter

    def get_use_local_geo_data(self):
        return self.__use_local_geo_data
