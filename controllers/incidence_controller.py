from flask import jsonify, request, Blueprint
from datetime import datetime
from configManager import ConfigManager
from werkzeug.exceptions import InternalServerError
from app import app
import logging
from services.canton_service import CantonService
from services.errorhandler_service import ErrorHandlerService

logger = logging.getLogger(__name__)

incidence_controller = Blueprint('incidence_controller', __name__)

df = ConfigManager.get_instance().get_required_date_format()
default_language = ConfigManager.get_instance().get_languages()[0]


@app.route('/cantons/<canton>/incidences/')
@incidence_controller.route('/cantons/<canton>/incidences/', methods=['GET'])
def get_incidences_for_canton(canton):
    """
    Returns incidences of the given canton with given date filter
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
          name: dateFrom
          type: string
          example: "2021-03-01"
          description: dateFrom - dateFrom is inclusive. If not given, all datasets since beginning.
        - in: query
          name: dateTo
          type: string
          example: "2021-03-31"
          description: dateTo - dateTo is inclusive. If not given, all datasets till today.
        - in: query
          name: language
          type: string
          required: false
          description: language tag (RFC 4646 format language_code-COUNTRY_CODE, e.g. "en-US")
    responses:
        200:
            description: Array of incidenceDTO
            schema:
                type: array
                items:
                    $ref: '#/definitions/incidenceDTO'
        400:
            description: Invalid date or canton format
        404:
            description: Canton not found
    """

    # read query params
    language = request.args['language'] if 'language' in request.args else ''
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(
        0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today(
    ).strftime(df)

    logger.info(
        f'GET /cantons/<canton>/incidences/ was called. (canton: {canton}, date_from: {date_from}, date_to: {date_to}, language: {language})')

    # check canton format
    if not ErrorHandlerService.check_canton_format(canton):
        return canton_bad_request('Invalid format for parameter "canton" (required: 2 chars)', canton)

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return date_bad_request(f'Invalid format for parameter "dateFrom" (required: {df})', None, date_from, None)
    if not ErrorHandlerService.check_date_format(date_to):
        return date_bad_request(f'Invalid format for parameter "dateTo" (required: {df})', None, None, date_to)
    if not ErrorHandlerService.check_date_semantic(date_from, date_to):
        return date_bad_request('Invalid semantic in dates (required: dateFrom <= dateTo))', None, date_from, date_to)

    # check language
    if not ErrorHandlerService.check_supported_language(language):
        logger.debug(f'Invalid language ({language}), using default language instead ({default_language}).')
        language = default_language

    result = CantonService.get_incidences(canton, date_from, date_to)

    if result is None:
        error_message = f'No canton found for "{canton}".'
        logger.debug(error_message)
        return error_message, 404

    return jsonify(result)


@app.route('/cantons/<canton>/municipalities/<bfsNr>/incidences/')
@incidence_controller.route('/cantons/<canton>/municipalities/<bfsNr>/incidences/', methods=['GET'])
def get_incidences_for_canton_and_bfs_nr(canton, bfsNr):
    """
    Returns incidences of the given canton and bfs-nr with given date filter
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
          name: dateFrom
          type: string
          example: "2021-03-01"
          description: dateFrom - dateFrom is inclusive. If not given, all datasets since beginning.
        - in: query
          name: dateTo
          type: string
          example: "2021-03-31"
          description: dateTo - dateTo is inclusive. If not given, all datasets till today.
        - in: query
          name: language
          type: string
          required: false
          description: language tag (RFC 4646 format language_code-COUNTRY_CODE, e.g. "en-US")
    responses:
        200:
            description: Array of incidenceDTO
            schema:
                type: array
                items:
                    $ref: '#/definitions/incidenceDTO'
        400:
            description: Invalid date, canton or bfsNr format
        404:
          description: Canton or bfsNr not found
    """

    # read query params
    language = request.args['language'] if 'language' in request.args else ''
    date_from = request.args['dateFrom'] if 'dateFrom' in request.args else datetime.fromtimestamp(
        0).strftime(df)
    date_to = request.args['dateTo'] if 'dateTo' in request.args else datetime.today(
    ).strftime(df)

    logger.info(
        f'GET /cantons/<canton>/municipalities/<bfsNr>/incidences/ was called. (canton: {canton}, bfsNr: {bfsNr}, date_from: {date_from}, date_to: {date_to}, language: {language})')

    # check canton format
    if not ErrorHandlerService.check_canton_format(canton):
        return canton_bad_request('Invalid format for parameter "canton" (required: 2 chars)', canton)

    # check bfs_nr format
    if not ErrorHandlerService.check_bfs_nr_format(bfsNr):
        return bfs_nr_bad_request('Invalid format for parameter "bfsNr" (required: 4-digit number)', bfsNr)

    # check from- and to date
    if not ErrorHandlerService.check_date_format(date_from):
        return date_bad_request(f'Invalid format for parameter "dateFrom" (required: {df})', bfsNr, date_from, None)
    if not ErrorHandlerService.check_date_format(date_to):
        return date_bad_request(f'Invalid format for parameter "dateTo" (required: {df})', bfsNr, None, date_to)
    if not ErrorHandlerService.check_date_semantic(date_from, date_to):
        return date_bad_request('Invalid semantic in dates (required: dateFrom <= dateTo))', bfsNr, date_from, date_to)

    # check language
    if not ErrorHandlerService.check_supported_language(language):
        logger.debug(f'Invalid language ({language}), using default language instead ({default_language}).')
        language = default_language

    result = CantonService.get_incidences(canton, date_from, date_to, bfsNr)

    if result is None:
        error_message = f'No municipality found for bfsNr {bfsNr}.'
        logger.debug(error_message)
        return error_message, 404

    return jsonify(result)


def bfs_nr_bad_request(error_message, bfs_nr):
    logger.debug(f'{error_message}. (bfs_nr: {bfs_nr})')
    return error_message, 400


def canton_bad_request(error_message, canton):
    logger.debug(f'{error_message}. (canton: {canton})')
    return error_message, 400


def date_bad_request(error_message, bfs_nr, date_from, date_to):
    params = (f'bfs_nr: {bfs_nr}, ' if bfs_nr else '') + \
        (f'date_from: {date_from}, ' if date_from else '') + \
        (f'date_to: {date_to}), ' if date_to else '')

    params = params[:-2] if params.endswith(', ') else params

    logger.debug(f'{error_message}. ({params})')
    return error_message, 400
