from flask import jsonify, request, Blueprint
from configManager import ConfigManager
from app import app
import logging
from flask_cors import cross_origin
from services.waypoint_service import WaypointService
from services.errorhandler_service import ErrorHandlerService
from flask import make_response

logger = logging.getLogger(__name__)

waypoint_controller = Blueprint('waypoint_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()
search_radius: int = ConfigManager.get_instance().get_geoservice_search_radius()
default_language = ConfigManager.get_instance().get_languages()[0]


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
        - in: query
          name: language
          type: string
          required: false
          description: language tag (RFC 4646 format language_code-COUNTRY_CODE, e.g. "en-US")
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

    # read query params
    language = request.args['language'] if 'language' in request.args else ''

    logger.info(f'POST /waypoints/ was called. (language: {language})')

    try:
        waypoints = request.get_json(force=True)  # forces use of 'application/json' content type!
    except Exception:
        error_message = f'Only accept body as JSON with content-type: application/json'
        logger.debug(error_message)
        return error_message, 400

    # Validate waypoints
    if len(waypoints) == 0:
        return 'Please provide some waypoints, empty array is not allowed.', 400
    elif not ErrorHandlerService.check_waypoints_array_format(waypoints):
        logger.debug(f'Invalid waypoints array format.')
        return 'Array of waypoints must be of format: ["lat": 42.1234, "lng": 8.1234]', 400

    # check language
    if not ErrorHandlerService.check_supported_language(language):
        logger.debug(f'Invalid language ({language}), using default language instead ({default_language}).')
        language = default_language

    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    logger.debug(
        f'Found {len(result)} unique municipalities for {len(waypoints)} waypoints')

    response = make_response(jsonify(result))
    if timedout_cantons:
        response.headers.set('Access-Control-Expose-Headers', 'X-Cantons-Timeout')
        response.headers.set('X-Cantons-Timeout', (", ").join(timedout_cantons))

    return response
