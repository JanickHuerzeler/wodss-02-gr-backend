from flask import jsonify, request, Blueprint
from datetime import datetime
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from app import app
import logging
from services.canton import CantonService
from services.ErrorHandlerService import ErrorHandlerService


logger = logging.getLogger(__name__)
municipality_controller = Blueprint(
    'municipality_controller', __name__, template_folder='templates')
df = ConfigManager.get_instance().get_required_date_format()


@app.route('/cantons/<canton>/municipalities/')
@municipality_controller.route('/cantons/<canton>/municipalities/', methods=['GET'])
def get_municipalities_for_canton(canton):
    result = CantonService.get_municipalities(canton)
    return jsonify(result)


@app.route('/cantons/<canton>/municipalities/<bfs_nr>/')
@municipality_controller.route('/cantons/<canton>/municipalities/<bfs_nr>', methods=['GET'])
def get_municipalitiy_for_canton(canton, bfs_nr):
    result = CantonService.get_municipality(canton, bfs_nr)
    return result
