from flask import jsonify, request, Blueprint
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
import logging

logger = logging.getLogger(__name__)

waypoint_controller = Blueprint(
    'waypoint_controller', __name__, template_folder='templates')


@waypoint_controller.route("/helloworld/", methods=['GET'])
def helloworld():

    logger.info(f'GET /helloworld/ was called.')

    return jsonify([{'polygon': [[[6.12354, 45.58797], [6.52425, 45.5874524597], [6.5345, 45.4524], [6.12000, 45.04520]]], 'municipality': {'bfs_nr': 1234, 'incidence': 123.12, 'population': 10_000, 'area': 120.75}}])
