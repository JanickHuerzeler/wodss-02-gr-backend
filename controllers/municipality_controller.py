from flask import jsonify, request, Blueprint
from datetime import datetime
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from app import app
import logging
from services.canton_service import CantonService
from services.errorhandler_service import ErrorHandlerService
from flask_cors import cross_origin

logger = logging.getLogger(__name__)

municipality_controller = Blueprint('municipality_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()
default_language = ConfigManager.get_instance().get_languages()[0]


@app.route('/cantons/<canton>/municipalities/')
@cross_origin()
@municipality_controller.route('/cantons/<canton>/municipalities/', methods=['GET'])
def get_municipalities_for_canton(canton):
    """
    Returns municipalities of the given canton
    ---
    produces:
        - application/json
    parameters:
        - in: path
          name: canton
          type: string
          required: true
          description: two-char canton abbreviation
        - in: query
          name: language
          type: string
          required: false
          description: language tag (RFC 4646 format language_code-COUNTRY_CODE, e.g. "en-US")
    responses:
        200:
            description: Array of municipalityMetadataDTO
            schema:
                type: array
                items:
                    $ref: '#/definitions/municipalityMetadataDTO'
        400:
            description: Invalid canton format
        404:
            description: Canton not found
        408:
            description: Canton or municipality service timed out
        502:
            description: Canton service returned unsuccessful status code
    """

    # read query params
    language = request.args['language'] if 'language' in request.args else ''

    logger.info(
        f'GET /cantons/<canton>/municipalities/ was called. (canton: {canton}, language: {language})')

    # check canton format
    if not ErrorHandlerService.check_canton_format(canton):
        return canton_bad_request('Invalid format for parameter "canton" (required: 2 chars)', canton)

    # check language
    if not ErrorHandlerService.check_supported_language(language):
        logger.debug(f'Invalid language ({language}), using default language instead ({default_language}).')
        language = default_language

    result, status = CantonService.get_municipalities(canton)

    if status == 408:
        return f'Canton service {canton} timed out', 408
    elif status == 404:
        return f'No canton found for "{canton}".', 404

    if result is None:
        error_message = f'Could not get data from canton service "{canton}".'
        logger.debug(error_message)
        return error_message, 502
    elif not result:
        error_message = f'No municipalities found for canton "{canton}".'
        logger.debug(error_message)
        return error_message, 404

    return jsonify(result)


@app.route('/cantons/<canton>/municipalities/<bfsNr>/')
@cross_origin()
@municipality_controller.route('/cantons/<canton>/municipalities/<bfsNr>/', methods=['GET'])
def get_municipalitiy_for_canton(canton, bfsNr):
    """
    Returns municipality of the given canton and bfs-nr
    ---
    produces:
        - application/json
    parameters:
        - in: path
          name: canton
          type: string
          required: true
          description: two-char canton abbreviation
        - in: path
          name: bfsNr
          type: string
          required: true
          description: bfsNr
        - in: query
          name: language
          type: string
          required: false
          description: language tag (RFC 4646 format language_code-COUNTRY_CODE, e.g. "en-US")
    responses:
        200:
            description: municipalityMetadataDTO
            schema:
                $ref: '#/definitions/municipalityMetadataDTO'
        400:
            description: Invalid canton or bfsNr format
        404:
            description: Canton or municipality not found
        408:
            description: Canton or municipality service timed out
        502:
            description: Canton service returned unsuccessful status code
    """

    # read query params
    language = request.args['language'] if 'language' in request.args else ''

    logger.info(
        f'GET /cantons/<canton>/municipalities/<bfsNr>/ was called. (canton: {canton}, bfsNr: {bfsNr}, language: {language})')

    # check canton format
    if not ErrorHandlerService.check_canton_format(canton):
        return canton_bad_request('Invalid format for parameter "canton" (required: 2 chars)', canton)

    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfsNr):
        return bfs_nr_bad_request('Invalid format for parameter "bfsNr" (required: 4-digit number)', bfsNr)

    # check language
    if not ErrorHandlerService.check_supported_language(language):
        logger.debug(f'Invalid language ({language}), using default language instead ({default_language}).')
        language = default_language

    result, status = CantonService.get_municipality(canton, bfsNr)

    if status == 408:
        return f'Canton service {canton} timed out', 408
    elif status == 404:
        return f'No canton found for "{canton}".', 404

    if result is None:
        error_message = f'Could not get data from canton service "{canton}" for bfsNr "{bfsNr}".'
        logger.debug(error_message)
        return error_message, 502
    elif not result:
        error_message = f'No municipality found for canton "{canton}" and bfsNr "{bfsNr}".'
        logger.debug(error_message)
        return error_message, 404

    return result


def bfs_nr_bad_request(error_message, bfs_nr):
    logger.debug(f'{error_message}. (bfs_nr: {bfs_nr})')
    return error_message, 400


def canton_bad_request(error_message, canton):
    logger.debug(f'{error_message}. (canton: {canton})')
    return error_message, 400
