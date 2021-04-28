import swagger_client
from swagger_client.rest import ApiException
from swagger_client.configuration import Configuration
from configManager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class CantonService:

    @staticmethod
    def get_municipalities(canton):
        if not CantonService.__isCantonAvailable(canton):
            return []

        try:
            logger.info(f'CantonService.get_municipalities(canton) with canton={canton}')
            client = swagger_client.MunicipalitiesApi(
                swagger_client.ApiClient(CantonService.__getClientConfig(canton)))
            municipalities = client.municipalities_get()
            result = []
            for m in municipalities:
                result.append(m.serialize)

            return result
        except ApiException as e:
            logger.warn(f'Exception when calling IncidencesApi->incidences_get: {e.status} - {e.reason}')
            return []

    @staticmethod
    def get_municipality(canton, bfs_nr):
        if not CantonService.__isCantonAvailable(canton):
            return []

        try:
            logger.info(f'CantonService.get_municipalitiy(canton, bfs_nr) with canton={canton}, bfs_nr={bfs_nr}')
            client = swagger_client.MunicipalitiesApi(
                swagger_client.ApiClient(CantonService.__getClientConfig(canton)))
            municipality = client.municipalities_bfs_nr_get(bfs_nr)
            # TODO: Handle 404 municipality not found
            return municipality.serialize

        except ApiException as e:
            logger.warn(f'Exception when calling IncidencesApi->incidences_get: {e.status} - {e.reason}')
            return []

    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        if not CantonService.__isCantonAvailable(canton):
            return []

        try:
            logger.info(
                f'CantonService.get_incidences(canton, dateFrom, dateTo, bfs_nr=None) with canton={canton}, dateFrom={dateFrom}, dateTo={dateTo}, bfs_nr={bfs_nr}')
            client = swagger_client.IncidencesApi(
                swagger_client.ApiClient(CantonService.__getClientConfig(canton)))

            if bfs_nr is None:
                incidences = client.incidences_get(date_from=dateFrom, date_to=dateTo)
            else:
                incidences = client.incidences_bfs_nr_get(bfs_nr, date_from=dateFrom, date_to=dateTo)
            result = []
            for i in incidences:
                result.append(i.serialize)

            return result
        except ApiException as e:
            logger.warn(f'Exception when calling IncidencesApi->incidences_get: {e.status} - {e.reason}')
            return []

    @staticmethod
    def __getClientConfig(canton):
        client_config = swagger_client.Configuration()
        canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()

        if CantonService.__isCantonAvailable(canton):
            client_config.host = canton_api_urls[canton]['url']
            if canton_api_urls[canton]['url'].startswith("https"):
                client_config.verify_ssl = True
                client_config.assert_hostname = False

            if canton_api_urls[canton]['ssl_ca_cert'] != "":
                client_config.ssl_ca_cert = f'certificates/{canton_api_urls[canton]["ssl_ca_cert"]}'
            else:
                client_config.ssl_ca_cert = None

        return client_config

    @staticmethod
    def __isCantonAvailable(canton):
        canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()
        if canton in canton_api_urls and canton_api_urls[canton]['url'] != "":
            return True
        else:
            logger.warn(f'Canton not available: {canton}')
            return False
