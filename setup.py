from flask import Flask
from configManager import ConfigManager
import logging
import logging.config
from os import path

app = Flask(__name__)

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
logging.config.fileConfig(log_file_path)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def create_app():
    return app


def get_test_app():
    global db, app
        
    return app
