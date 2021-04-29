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
nth_waypoint_filter: int = ConfigManager.get_instance().get_nth_waypoint_filter()


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

    try:
        waypoints = request.json  # forces use of 'application/json' content type!
    except Excpetion:
        return 'Could not parse body as JSON.', 400

    logger.info(f'Got {len(waypoints)} waypoints.')

    # TODO: Validate waypoints (not just simply the first as here)
    if len(waypoints) == 0:
        return 'Please provide some waypoints.', 204
    elif waypoints[0] is None:
        return 'Invalid waypoint.', 400
    elif 'lat' not in waypoints[0].keys():
        return 'Waypoint must include "lat" key.', 400
    elif 'lng' not in waypoints[0].keys():
        return 'Waypoint must include "lng" key.', 400

    logger.info(f'Waypoints passed some easy validation. (only looked at first waypoint)')

    # TODO: Should we still have this option? Currently we are always process all waypoints
    # Take only every n-th waypoint
    waypoints = waypoints[::nth_waypoint_filter]

    logger.info(
        f'Only working with subset of waypoints. (new length: {len(waypoints)}, nth_waypoint_filter: {nth_waypoint_filter})')

    result = WaypointService.get_waypoints_data(waypoints)

    logger.info(
        f'Found {len(result)} unique municipalities for {len(waypoints)} waypoints')

    return jsonify(result)
