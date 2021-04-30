from flask import jsonify, request, Blueprint
from datetime import datetime
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from app import app
import logging
from flask_cors import cross_origin
from services.waypoint_service import WaypointService
from services.geo_service import GeoService
from services.canton_service import CantonService
from services.errorhandler_service import ErrorHandlerService
import pandas as pd
import matplotlib
import matplotlib.pyplot as pyplot

logger = logging.getLogger(__name__)

waypoint_controller = Blueprint('waypoint_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()
search_radius: int = ConfigManager.get_instance().get_geoservice_search_radius()

@app.route('/waypoints/', methods=['POST'])
@cross_origin()
@waypoint_controller.route('/waypoints/', methods=['POST'])
def post_waypoints():
    """
    Returns municipalities and their corona- and geo-information where the given waypoints lay in.
    ---
    description: Municipalities with corona and geo-information
    produces:
        - application/json
    consumes:
        - application/json
    parameters:
        - in: body
          name: waypoints
          description: Array of waypoints from route
          schema:
            type: array
            items:
                $ref: '#/definitions/coordinateDTO'
    responses:
        200:
            description: Array of with unique MunicipalityDTOs that could be matched with the provided waypoint coordinates
            schema:
                type: array
                items:
                    $ref: '#/definitions/municipalityDTO'
        204:
            description: Empty array was passed
        400:
            description: Invalid format of the body or could not even parse it (needs application/json as Content-Type, hence body must be valid JSON too)
    """

    logger.info(f'POST /waypoints/ was called.')

    try:
        waypoints = request.json  # forces use of 'application/json' content type!
    except Excpetion:
        error_message = f'Could not parse request body as JSON.'
        logger.debug(error_message)
        return error_message, 400

    # Validate waypoints
    if len(waypoints) == 0:
        return 'Please provide some waypoints, empty array is not allowed.', 400
    elif not ErrorHandlerService.check_waypoints_array_format(waypoints):
        logger.debug(f'Invalid waypoints array format.')
        return 'Array of waypoints must be of format: ["lat": 42.1234, "lng": 8.1234]', 400           
    
    result = WaypointService.get_waypoints_data(waypoints)

    logger.debug(
        f'Found {len(result)} unique municipalities for {len(waypoints)} waypoints')

    return jsonify(result)
