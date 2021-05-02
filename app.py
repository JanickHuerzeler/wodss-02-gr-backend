import logging.config
import logging
from flask import Flask
from configManager import ConfigManager
from os import path
import requests_cache
import json
import redis
from flasgger import Swagger
from swagger_metadata import template

app = Flask(__name__)

# Setup swagger
swagger = Swagger(app, template=template)

# Setup logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
logging.config.fileConfig(log_file_path)

logger = logging.getLogger(__name__)


redis_server = ConfigManager.get_instance().get_redis_server_config()
secret_key = ConfigManager.get_instance().get_secret()

redis_conn = redis.Redis(
    host=redis_server['host'],
    port=redis_server['port'],
    password=redis_server['password']
)

# Setup request_cache with redis backend
requests_cache.install_cache(cache_name='cantonservice_cache', backend='redis',
                             connection=redis_conn, secret_key=secret_key, expire_after=3600*4)  # 4h

# Setup request_cache with sqlite backend
# requests_cache.install_cache(cache_name='cantonservice_cache', backend='sqlite', expire_after=3600*4)  # 4h


# Read local geojson data
use_local_geo_data = ConfigManager.get_instance().get_use_local_geo_data()
geolocal_filepath = ConfigManager.get_instance().get_geolocal_filepath()
if use_local_geo_data:
    with open(geolocal_filepath) as f:
        logger.info(f'Loading geojson data from {geolocal_filepath}')
        geo_features = json.load(f)["features"]

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def get_app():
    return app
