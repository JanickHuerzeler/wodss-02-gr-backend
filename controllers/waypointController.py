from flask import jsonify, Blueprint
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from setup import app
import logging
from flask_cors import cross_origin
from services.canton import CantonService


logger = logging.getLogger(__name__)


waypoint_controller = Blueprint(
    'waypoint_controller', __name__, template_folder='templates')

logger.info(f'I am in the waypointController!')


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


@app.route('/cantons/<canton>/municipalities/')
@cross_origin()
@waypoint_controller.route('/cantons/<canton>/municipalities/', methods=['GET'])
def get_municipalities_for_canton(canton):
    result = CantonService.get_municipalities(canton)
    return jsonify(result)


@app.route('/cantons/<canton>/municipalities/<bfs_nr>/')
@cross_origin()
@waypoint_controller.route('/cantons/<canton>/municipalities/<bfs_nr>', methods=['GET'])
def get_municipalitiy_for_canton(canton, bfs_nr):
    result = CantonService.get_municipalitiy(canton, bfs_nr)
    return result
