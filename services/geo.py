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

        logger.info(
            f'GeoService.get_geodata(lat, lng, distance) with lat={lat}, lng={lng}, distance={distance}')

        geoservice_url = ConfigManager.get_instance().get_geoservice_url()

        try:
            # TODO: Handle request errors
            response = requests.get(geoservice_url, params=params)
            response_data = response.json()['records']

            result = []
            for entry in response_data:
                municipality = {}
                municipality['bfs_nr'] = entry['fields']['bfsnr']
                municipality['canton'] = entry['fields']['kanton']
                municipality['plz'] = entry['fields']['postleitzahl']
                municipality['name'] = entry['fields']['ortbez27']
                municipality['geo_shape'] = list(
                    map(GeoService.__format_geoshape, entry['fields']['geo_shape']['coordinates'][0]))

                logger.info(
                    f"Found bfs_nr={municipality['bfs_nr']}, plz={municipality['plz']}, name={municipality['name']}")

                result.append(municipality)

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
