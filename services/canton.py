from configManager import ConfigManager
import logging
import requests
from service_models.municipality import Municipality
from service_models.incidence import Incidence

logger = logging.getLogger(__name__)


class CantonService:

    canton_api_urls = ConfigManager.get_instance().get_cantonservice_urls()

    @staticmethod
    def get_municipalities(canton):
        if not CantonService.__isCantonAvailable(canton):
            return []

        try:
            logger.info(f'CantonService.get_municipalities(canton) with canton={canton}')
                       
            municipalities = CantonService.__getMunicipalities(canton, None)
            
            logger.debug(f'Got {len(municipalities)} municipalities from CantonService {canton}.')
            
            result = []
            for m in municipalities:
                result.append(Municipality(**m).as_dict)

            return result
        except requests.exceptions.RequestException as e:            
            logger.exception("Exception when calling CantonService.__getMunicipalities or processing its response.")
            return []

    @staticmethod
    def get_municipality(canton, bfs_nr):
        if not CantonService.__isCantonAvailable(canton):
            return {}

        try:
            logger.info(f'CantonService.get_municipalitiy(canton, bfs_nr) with canton={canton}, bfs_nr={bfs_nr}')
         
            municipality = CantonService.__getMunicipalities(canton, bfs_nr)            
            # TODO: Handle 404 municipality not found
            return Municipality(**municipality).as_dict
        except requests.exceptions.RequestException as e:
            logger.exception("Exception when calling CantonService.__getMunicipalities or processing its response.")
            return {}

    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        if not CantonService.__isCantonAvailable(canton):
            return []

        try:
            logger.info(
                f'CantonService.get_incidences(canton, dateFrom, dateTo, bfs_nr=None) with canton={canton}, dateFrom={dateFrom}, dateTo={dateTo}, bfs_nr={bfs_nr}')            

            if bfs_nr is None:                
                incidences = CantonService.__getIncidences(canton, dateFrom, dateTo)
            else:
                # TODO: Handle 404 municipality not found
                incidences = CantonService.__getIncidences(canton, dateFrom, dateTo, bfs_nr)            
            
            logger.debug(f'Got {len(incidences)} incidences from CantonService {canton}.')

            result = []
            for i in incidences:
                result.append(Incidence(**i).as_dict)

            return result
        except requests.exceptions.RequestException as e:
            logger.exception("Exception when calling CantonService.__getIncidences or processing its response")
            return []

    @staticmethod
    def __getIncidences(canton: str, dateFrom, dateTo, bfs_nr=None):
        resource_path = '/incidences/'
        query_params = {'dateFrom': dateFrom, 'dateTo': dateTo}
       
        response = CantonService.__getResponse(canton, resource_path, bfs_nr, query_params)
        return response.json()

    @staticmethod
    def __getMunicipalities(canton: str, bfs_nr=None):
        resource_path = '/municipalities/'
       
        response = CantonService.__getResponse(canton, resource_path, bfs_nr)
        return response.json()

    @staticmethod
    def __getResponse(canton: str, resource_path: str, path_param: str=None, query_params: dict=None):
        host, ssl_cert_path = CantonService.__getRequestInfo(canton)
        
        url = f'{host}{resource_path}' + (f'{path_param}/' if path_param is not None else '')
        
        logger.debug(f'Going to call url: {url}')

        if ssl_cert_path != '':            
            return requests.get(url, verify=ssl_cert_path, params=query_params)
        else:
            return requests.get(url, params=query_params)

    @staticmethod
    def __getRequestInfo(canton: str):
        
        host: str = None
        canton_ssl_cert_path: str = None

        if CantonService.__isCantonAvailable(canton):
            host = CantonService.canton_api_urls[canton]['url']
            canton_ssl_cert_name = CantonService.canton_api_urls[canton]['ssl_ca_cert']
            if canton_ssl_cert_name != "":
                canton_ssl_cert_path = f'certificates/{canton_ssl_cert_name}'        

        return host, canton_ssl_cert_path

    @staticmethod
    def __isCantonAvailable(canton: str):        
        if canton in CantonService.canton_api_urls and CantonService.canton_api_urls[canton]['url'] != "":
            return True
        else:
            logger.warn(f'Canton not available: {canton}')
            return False
