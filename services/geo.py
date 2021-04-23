import requests
from configManager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class GeoService:

    @staticmethod
    def get_geodata(lat, lng, distance):
        params = (
            ('dataset', 'plz_verzeichnis_v2'),
            ('geofilter.distance', f'{lat},{lng},{distance}')
        )

        geoservice_url = ConfigManager.get_instance().get_geoservice_url()

        try:
            # TODO: Handle request errors
            response = requests.get(geoservice_url, params=params)
            response_data = response.json()['records'][0]

            # TODO: Handle multiple municipality result for given coordinates
            result = {}
            result['bfs_nr'] = response_data['fields']['bfsnr']
            result['canton'] = response_data['fields']['kanton']
            result['plz'] = response_data['fields']['postleitzahl']
            result['name'] = response_data['fields']['ortbez27']
            result['geo_shape'] = list(map(GeoService.__format_geoshape,
                                       response_data['fields']['geo_shape']['coordinates'][0]))

            return result
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            raise SystemExit(errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
            raise SystemExit(errh)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            raise SystemExit(errh)
        except requests.exceptions.RequestException as err:
            print("Oops: Something Else", err)
            raise SystemExit(errh)
        except:
            print("exception")
            return None

    @staticmethod
    def __format_geoshape(coord):
        return {'lat': coord[1], 'lng': coord[0]}
