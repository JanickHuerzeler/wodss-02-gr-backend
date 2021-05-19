from rtree import index
from shapely.geometry import shape, Point
import logging
from app import geo_features

logger = logging.getLogger(__name__)

# Create the R-tree index and store the features in it (bounding box)
polygonIndex = index.Index()
for pos, geo_feature in enumerate(geo_features):
    if geo_feature['geometry']:
        polygonIndex.insert(pos, shape(geo_feature['geometry']).bounds)


class GeoDataAccess:


    @staticmethod
    def get_geodata(waypoints):

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
                        municipality['geo_shapes'] = [list(map(GeoDataAccess.__format_geoshape,
                                                               entry['geometry']['coordinates'][0]))]
                    elif geo_shape_type == 'MultiPolygon':
                        municipality['geo_shapes'] = [list(map(GeoDataAccess.__format_geoshape, polygon[0]))
                                                      for polygon in entry['geometry']['coordinates']]
                    else:
                        logger.warning(f'Unknown geo_shape type {geo_shape_type}!')
                        municipality['geo_shapes'] = []

                    municipalities_geo_data.append(municipality)

        return municipalities_geo_data

    @staticmethod
    def __format_geoshape(coord):
        return {'lat': coord[1], 'lng': coord[0]}
