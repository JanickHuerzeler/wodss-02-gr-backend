from flask import jsonify, request, Blueprint
from datetime import datetime
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from setup import app
import logging
from flask_cors import cross_origin
from services.waypoint import WayPointService
from services.geo import GeoService
from services.canton import CantonService
from services.ErrorHandlerService import ErrorHandlerService
import pandas as pd
import matplotlib
import matplotlib.pyplot as pyplot

logger = logging.getLogger(__name__)
waypoint_controller = Blueprint(
    'waypoint_controller', __name__, template_folder='templates')
df = ConfigManager.get_instance().get_required_date_format()
search_radius: int = ConfigManager.get_instance().get_geoservice_search_radius()
nth_waypoint_filter: int = ConfigManager.get_instance().get_nth_waypoint_filter()


@app.route('/helloworld/')
@cross_origin()
@waypoint_controller.route("/helloworld/", methods=['GET'])
def helloworld():
    """
    A demo route for helloworld.
    ---
    description: helloworld
    produces: "application/json"
    definitions:
        helloworldtype:
            type: object
            properties:
                municipality:
                    type: object
                    properties:
                        area:
                            type: number
                        bfs_nr:
                            type: integer
                        incidence:
                            type: integer
                        population:
                            type: number
                polygon:
                    type: array
                    items:
                        $ref: '#/definitions/polygon'
        polygon:
            type: array
            items:
                type: array
                items:
                    type: integer
    responses:
        200:
            description: A helloworld to be returned
            schema:
                $ref: '#/definitions/helloworldtype'

    """
    logger.info(f'GET /helloworld/ was called.')

    return jsonify([{'polygon': [[[6.12354, 45.58797], [6.52425, 45.5874524597], [6.5345, 45.4524], [6.12000, 45.04520]]], 'municipality': {'bfs_nr': 1234, 'incidence': 123.12, 'population': 10_000, 'area': 120.75}}])


@app.route('/geo/<lat>/<lng>/<distance>/')
@cross_origin()
@waypoint_controller.route("/geo/<lat>/<lng>/<distance>/", methods=['GET'])
def get_geodata(lat, lng, distance):
    # TODO: Input param checks
    result = WayPointService.get_waypoint_data(lat, lng, distance)
    return jsonify(result)


@app.route('/waypoints/')
@cross_origin()
@waypoint_controller.route('/waypoints/', methods=['POST'])
def post_waypoints():
    """
    Gets Municipalities and their corona- and geo-information where the given waypoints lay in.
    ---
    description: Municipalities with corona and geo-information
    definitions:
        municipalityDTO:
            type: object
            properties:
                bfs_nr:
                    type: integer
                canton:
                    type: string
                name:
                    type: string
                plz:
                    type: integer
                incidence:
                    type: number
                incidence_date:
                    type: string
                    format: date
                incidence_color:
                    type: string
                geo_shapes:
                    type: array
                    items:
                        type: array
                        items:
                            $ref: '#/definitions/coordinateDTO'
        coordinateDTO:            
            type: object
            properties:
                lat:
                    type: number
                lng:
                    type: number      
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

# Probably OpenAPI 3.0 spec, maybe useful if we should change to some proper swagger documentaion
#  requestBody:
#         descriptions: Array of waypoints from route
#         required: true
#         content:
#             application/json:
#                 schema:
#                     type: array
#                     items:
#                         $ref: '#/definitions/coordinateDTO'

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

    # Take only every n-th waypoint
    waypoints = waypoints[::nth_waypoint_filter]

    logger.info(
        f'Only working with subset of waypoints. (new length: {len(waypoints)}, nth_waypoint_filter: {nth_waypoint_filter})')

    result = WayPointService.get_waypoints_data(waypoints)

    return jsonify(result)
