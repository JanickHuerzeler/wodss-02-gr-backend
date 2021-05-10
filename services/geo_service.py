from rtree import index
import json
from shapely.geometry import shape, GeometryCollection, Point
import requests
from configManager import ConfigManager
import logging
from app import geo_features

logger = logging.getLogger(__name__)

use_local_geo_data = ConfigManager.get_instance().get_use_local_geo_data()
if use_local_geo_data:
    # Create the R-tree index and store the features in it (bounding box)
    polygonIndex = index.Index()
    for pos, geo_feature in enumerate(geo_features):
        if geo_feature['geometry']:
            polygonIndex.insert(pos, shape(geo_feature['geometry']).bounds)


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
            response = requests.get(geoservice_url, params=params)
            response_data = response.json()['records']

            result = []
            for entry in response_data:
                municipality = {}
                municipality['bfs_nr'] = entry['fields']['bfsnr']
                municipality['canton'] = entry['fields']['kanton']
                municipality['plz'] = entry['fields']['postleitzahl']
                municipality['name'] = entry['fields']['ortbez27']

                geo_shape_type = entry['fields']['geo_shape']['type']
                if geo_shape_type == 'Polygon':
                    municipality['geo_shapes'] = [list(map(GeoService.__format_geoshape,
                                                           entry['fields']['geo_shape']['coordinates'][0]))]
                elif geo_shape_type == 'MultiPolygon':
                    municipality['geo_shapes'] = [list(map(GeoService.__format_geoshape, polygon[0]))
                                                  for polygon in entry['fields']['geo_shape']['coordinates']]
                else:
                    logger.warning(f'Unknown geo_shape type {geo_shape_type}!')
                    municipality['geo_shapes'] = []

                result.append(municipality)

            return result

        except requests.exceptions.HTTPError as errh:
            log_msg = f'HTTPError when calling external Geoservice at {geoservice_url}: {errh.response.status_code} - {errh.response.reason}'
            logger.exception(log_msg)
            return None
        except requests.exceptions.RequestException:
            logger.exception(
                f'RequestException when calling external Geoservice at {geoservice_url}')
            return None

    @staticmethod
    def get_local_geodata(waypoints):

        if not use_local_geo_data:
            raise RuntimeError('Local geo data usage is not configured in config.json - data not initialized!')

        municipalities_geo_data = []

        # Create shapely Points
        points = [Point(waypoint['lng'], waypoint['lat']) for waypoint in waypoints]

        # iterate through points
        for i, pt in enumerate(points):
            point = shape(pt)
            # iterate through spatial index
            for j in polygonIndex.intersection(point.coords[0]):
                if point.within(shape(geo_features[j]['geometry'])):
                    entry = geo_features[j]

                    municipality = {}
                    municipality['bfs_nr'] = entry['properties']['bfsnr']
                    municipality['canton'] = entry['properties']['kanton']
                    municipality['plz'] = entry['properties']['postleitzahl']
                    municipality['name'] = entry['properties']['ortbez27']

                    geo_shape_type = entry['geometry']['type']
                    if geo_shape_type == 'Polygon':
                        municipality['geo_shapes'] = [list(map(GeoService.__format_geoshape,
                                                               entry['geometry']['coordinates'][0]))]
                    elif geo_shape_type == 'MultiPolygon':
                        municipality['geo_shapes'] = [list(map(GeoService.__format_geoshape, polygon[0]))
                                                      for polygon in entry['geometry']['coordinates']]
                    else:
                        logger.warning(f'Unknown geo_shape type {geo_shape_type}!')
                        municipality['geo_shapes'] = []

                    municipalities_geo_data.append(municipality)

        return municipalities_geo_data

    @staticmethod
    def __format_geoshape(coord):
        return {'lat': coord[1], 'lng': coord[0]}
