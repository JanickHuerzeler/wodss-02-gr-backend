import swagger_client
from swagger_client.rest import ApiException
from swagger_client.configuration import Configuration
from configManager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class CantonService:

    @staticmethod
    def get_municipalities(canton):
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
            print("Exception when calling MunicipalitiesApi->municipalities_get: %s\n" % e)

    @staticmethod
    def get_municipality(canton, bfs_nr):
        try:
            logger.info(f'CantonService.get_municipalitiy(canton, bfs_nr) with canton={canton}, bfs_nr={bfs_nr}')
            client = swagger_client.MunicipalitiesApi(
                swagger_client.ApiClient(CantonService.__getClientConfig(canton)))
            municipality = client.municipalities_bfs_nr_get(bfs_nr)
            # TODO: Handle 404 municipality not found
            return municipality.serialize

        except ApiException as e:
            print("Exception when calling MunicipalitiesApi->municipalities_bfs_nr_get: %s\n" % e)

    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        try:
            logger.info(
                f'CantonService.get_incidences(canton, dateFrom, dateTo, bfs_nr=None) with canton={canton}, dateFrom={dateFrom}, dateTo={dateTo}, bfs_nr={bfs_nr}')
            client = swagger_client.IncidencesApi(
                swagger_client.ApiClient(CantonService.__getClientConfig(canton)))

            if bfs_nr is None:
                incidences = client.incidences_get(date_from=dateFrom, date_to=dateTo)
            else:
                # TODO: Handle 404 municipality not found
                incidences = client.incidences_bfs_nr_get(bfs_nr, date_from=dateFrom, date_to=dateTo)
            result = []
            for i in incidences:
                result.append(i.serialize)

            return result
        except ApiException as e:
            print("Exception when calling IncidencesApi->incidences_get: %s\n" % e)

    @staticmethod
    def __getClientConfig(canton):
        client_config = swagger_client.Configuration()
        canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()

        # TODO: Perhaps not the best way
        client_config.verify_ssl = False

        # TODO: Handle canton not available
        if canton in canton_api_urls and canton_api_urls[canton]['url'] != "":
            client_config.host = canton_api_urls[canton]['url']
            if canton_api_urls[canton]['ssl_ca_cert'] != "":
                client_config.ssl_ca_cert = f'certificates/{canton_api_urls[canton]["ssl_ca_cert"]}'
            else:
                client_config.ssl_ca_cert = None

        return client_config
