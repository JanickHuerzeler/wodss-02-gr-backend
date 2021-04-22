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
            municipalities = CantonService.__getClient(canton).municipalities_get()
            result = []
            for m in municipalities:
                result.append(m.serialize)

            return result
        except ApiException as e:
            print("Exception when calling MunicipalitiesApi->municipalities_get: %s\n" % e)

    @staticmethod
    def get_municipalitiy(canton, bfs_nr):
        try:
            logger.info(f'CantonService.get_municipalitiy(canton, bfs_nr) with canton={canton}, bfs_nr={bfs_nr}')
            municipality = CantonService.__getClient(canton).municipalities_bfs_nr_get(bfs_nr)
            return municipality.serialize

        except ApiException as e:
            print("Exception when calling MunicipalitiesApi->municipalities_bfs_nr_get: %s\n" % e)

    @staticmethod
    def __getClient(canton):
        client_config = swagger_client.Configuration()
        canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()

        # TODO: Perhaps not the best way
        client_config.verify_ssl = False

        if canton in canton_api_urls and canton_api_urls[canton]['url'] != "":
            client_config.host = canton_api_urls[canton]['url']
            if canton_api_urls[canton]['ssl_ca_cert'] != "":
                client_config.ssl_ca_cert = f'certificates/{canton_api_urls[canton]["ssl_ca_cert"]}'
            else:
                client_config.ssl_ca_cert = None

        return swagger_client.MunicipalitiesApi(swagger_client.ApiClient(client_config))
