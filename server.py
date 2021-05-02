import redis
from app import app
from configManager import ConfigManager

from controllers.waypoint_controller import waypoint_controller
from controllers.incidence_controller import incidence_controller
from controllers.municipality_controller import municipality_controller

from flask_cors import CORS, cross_origin

import logging
from werkzeug.exceptions import InternalServerError, NotFound

logger = logging.getLogger(__name__)

server_config = ConfigManager.get_instance().get_server_config()
application_root = ConfigManager.get_instance().get_application_root()

app.register_blueprint(waypoint_controller, url_prefix=application_root)
app.register_blueprint(incidence_controller, url_prefix=application_root)
app.register_blueprint(municipality_controller, url_prefix=application_root)


@app.errorhandler(Exception)
def handle_excpetion(e):
    if isinstance(e, NotFound):
        # Not found exception also contains automatic calls from browsers, e.g. to /favicon.ico
        logger.debug('A NotFound exception occurred.', exc_info=e)
        return e
    elif isinstance(e, redis.exceptions.ConnectionError):
        logger.critical('Could not connect to redis server. Make sure it is started!', exc_info=e)
        return InternalServerError(description='An instance of this application seems to be not running. Please contact the administrator of this app.')
    else:
        logger.critical('Unhandled Exception occurred', exc_info=e)
        return InternalServerError(description='An InternalServerError occurred. Please contact the administrator of this app.', original_exception=e)


if __name__ == '__main__':
    app.config['DEVELOPMENT'] = server_config["development"]

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.run(debug=server_config["debug"],
            host=server_config["host"], port=server_config["port"])
