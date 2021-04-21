from setup import app # Order matters, e.g. for logger!
from configManager import ConfigManager
from controllers.waypointController import waypoint_controller
from flasgger import Swagger
#from controllers.swaggerUIController import swaggerui_controller
import logging
from werkzeug.exceptions import InternalServerError, NotFound
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

server_config = ConfigManager.get_instance().get_server_config()
application_root = ConfigManager.get_instance().get_application_root()

app.register_blueprint(waypoint_controller, url_prefix=application_root)
#app.register_blueprint(swaggerui_controller, url_prefix=application_root)


@app.errorhandler(Exception)
def handle_excpetion(e):
    if isinstance(e, NotFound):
        # Not found exception also contains automatic calls from browsers, e.g. to /favicon.ico
        logger.debug('A NotFound exception occurred.', exc_info=e)
        return e
    else:
        logger.critical('Unhandled Exception occurred', exc_info=e)
        return InternalServerError(description='An InternalServerError occurred. Please contact the administrator of this app.', original_exception=e)


if __name__ == '__main__':
    app.config['DEVELOPMENT'] = server_config["development"]
    swagger = Swagger(app)
    app.run(debug=server_config["debug"],
            host=server_config["host"], port=server_config["port"])
