from configManager import ConfigManager
from datetime import datetime
import logging
import requests
from dto.municipality import Municipality
from dto.incidence import Incidence

logger = logging.getLogger(__name__)


class CantonDataAccess:

    canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()

    @staticmethod
    def get_default_date():
        return datetime.now()

    @staticmethod
    def get_municipalities(canton):
        logger.info(
            f'CantonDataAccess.get_municipalities(canton) with canton={canton}')

        if not CantonDataAccess.__is_canton_available(canton):
            return [], 404

        try:

            municipalities = CantonDataAccess.__get_municipalities(canton, None)

            logger.debug(
                f'Got {len(municipalities)} municipalities from Canton Service {canton}.')

            result = [Municipality(**m).as_dict for m in municipalities]

            return result, 200
        except requests.exceptions.Timeout as errh:
            logger.warning(
                'Timeout when calling CantonDataAccess.__get_municipalities or processing its response')
            return None, 408

        except requests.exceptions.HTTPError as errh:
            log_msg = f'HTTPError when calling CantonDataAccess.__get_municipalities: {errh.response.status_code} - {errh.response.reason}'
            if errh.response.status_code < 500:
                logger.warning(log_msg)
            else:
                logger.exception(log_msg)
            return None, errh.response.status_code
        except requests.exceptions.RequestException:
            logger.exception(
                'Exception when calling CantonDataAccess.__get_municipalities or processing its response.')
            return None, None

    @staticmethod
    def get_municipality(canton, bfs_nr):
        logger.info(
            f'CantonDataAccess.get_municipalitiy(canton, bfs_nr) with canton={canton}, bfs_nr={bfs_nr}')

        if not CantonDataAccess.__is_canton_available(canton):
            return None, 404

        try:
            municipality = CantonDataAccess.__get_municipalities(canton, bfs_nr)
            return Municipality(**municipality).as_dict, 200
        except requests.exceptions.Timeout as errh:
            logger.warning(
                'Timeout when calling CantonDataAccess.__get_municipalities or processing its response')
            return None, 408
        except requests.exceptions.HTTPError as errh:
            log_msg = f'HTTPError when calling CantonDataAccess.__get_municipalities: {errh.response.status_code} - {errh.response.reason}'
            if errh.response.status_code < 500:
                logger.warning(log_msg)
            else:
                logger.exception(log_msg)
            return None, errh.response.status_code
        except requests.exceptions.RequestException:
            logger.exception(
                'Exception when calling CantonDataAccess.__get_municipalities or processing its response.')
            return None, None

    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        logger.info(
            f'CantonDataAccess.get_incidences(canton, dateFrom, dateTo, bfs_nr=None) with canton={canton}, dateFrom={dateFrom}, dateTo={dateTo}, bfs_nr={bfs_nr}')

        if not CantonDataAccess.__is_canton_available(canton):
            return None, 404

        try:
            if bfs_nr is None:
                incidences = CantonDataAccess.__get_incidences(
                    canton, dateFrom, dateTo)
            else:
                incidences = CantonDataAccess.__get_incidences(
                    canton, dateFrom, dateTo, bfs_nr)

            logger.debug(
                f'Got {len(incidences)} incidences from Canton Service {canton}.')

            result = []
            for i in incidences:
                result.append(Incidence(**i).as_dict)

            return result, 200
        except requests.exceptions.Timeout as errh:
            logger.warning(
                'Timeout when calling CantonDataAccess.__get_incidences or processing its response')
            return None, 408
        except requests.exceptions.HTTPError as errh:
            log_msg = f'HTTPError when calling CantonDataAccess.__get_incidences: {errh.response.status_code} - {errh.response.reason}'
            if errh.response.status_code < 500:
                logger.warning(log_msg)
            else:
                logger.exception(log_msg)
            return None, errh.response.status_code
        except requests.exceptions.RequestException:
            logger.exception(
                'Exception when calling CantonDataAccess.__get_incidences or processing its response')
            return None, None

    @staticmethod
    def __get_incidences(canton: str, dateFrom, dateTo, bfs_nr=None):
        resource_path = '/incidences/'
        query_params = {'dateFrom': dateFrom, 'dateTo': dateTo}

        response = CantonDataAccess.__get_response(
            canton, resource_path, bfs_nr, query_params)
        return response.json()

    @staticmethod
    def __get_municipalities(canton: str, bfs_nr=None):
        resource_path = '/municipalities/'

        response = CantonDataAccess.__get_response(canton, resource_path, bfs_nr)
        return response.json()

    @staticmethod
    def __get_response(canton: str, resource_path: str, path_param: str = None, query_params: dict = None):
        host, ssl_cert_path = CantonDataAccess.__get_request_info(canton)

        url = f'{host}{resource_path}' + \
            (f'{path_param}/' if path_param is not None else '')

        logger.debug(f'Going to call url: {url}')

        if ssl_cert_path != '':
            response = requests.get(
                url, verify=ssl_cert_path, params=query_params, timeout=(3.05, 15))
        else:
            response = requests.get(url, params=query_params, timeout=(3.05, 15))

        response.raise_for_status()

        logger.debug(
            f'Got response from Canton Service {canton}. (url: {url}, from_cache: {response.from_cache if hasattr(response, "from_cache") else "nocache"}, has SSL cert file: {(ssl_cert_path != "")})')

        return response

    @staticmethod
    def __get_request_info(canton: str):

        host: str = ''
        canton_ssl_cert_path: str = ''

        if CantonDataAccess.__is_canton_available(canton):
            host = CantonDataAccess.canton_api_urls[canton]['url']
            canton_ssl_cert_name = CantonDataAccess.canton_api_urls[canton]['ssl_ca_cert']
            if canton_ssl_cert_name != '':
                canton_ssl_cert_path = f'certificates/{canton_ssl_cert_name}'

        return host, canton_ssl_cert_path

    @staticmethod
    def __is_canton_available(canton: str):
        if canton in CantonDataAccess.canton_api_urls and CantonDataAccess.canton_api_urls[canton]['url'] != '':
            return True
        else:
            logger.warning(f'Canton not available: {canton}')
            return False
