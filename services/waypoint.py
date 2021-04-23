import requests
from datetime import datetime
from configManager import ConfigManager
import logging
from services.geo import GeoService
from services.canton import CantonService


logger = logging.getLogger(__name__)
df = ConfigManager.get_instance().get_required_date_format()


class WayPointService:

    @staticmethod
    def get_waypoint_data(lat, lng, distance):
        # TODO: Error handling for geo data fetching
        geo_data = GeoService.get_geodata(lat, lng, distance)
        # TODO: Error handling for incidence data fetching
        # TODO: If current date does not return incidences, go back 1, 2, 3 and request data for then
        incidence_data = CantonService.get_incidences(geo_data['canton'], datetime.now().strftime(
            df), datetime.now().strftime(df), geo_data['bfs_nr'])
        result = geo_data
        # We only request data for one day, therefor always the first element is of interest
        result['incidence_date'] = incidence_data[0]['date']
        result['incidence'] = incidence_data[0]['incidence']

        return result
