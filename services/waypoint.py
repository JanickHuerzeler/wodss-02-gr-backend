import requests
from datetime import datetime, timedelta
from configManager import ConfigManager
import logging
from services.geo import GeoService
from services.canton import CantonService


logger = logging.getLogger(__name__)
df = ConfigManager.get_instance().get_required_date_format()
incidence_retry_days: int = ConfigManager.get_instance().get_incidence_retry_days()


class WayPointService:

    @staticmethod
    def get_waypoint_data(lat, lng, distance):
        # TODO: Error handling for geo data fetching
        geo_data = GeoService.get_geodata(lat, lng, distance)
        if geo_data:
            # TODO: Error handling for incidence data fetching
            # TODO: If current date does not return incidences, go back 1, 2, 3 and request data for then
            incidence_data = CantonService.get_incidences(geo_data['canton'], datetime.now().strftime(
                df), datetime.now().strftime(df), geo_data['bfs_nr'])

            retry_count = 0

            while retry_count < 3 and not incidence_data:
                retry_count += 1
                logger.debug(f'Retrying to get incidence. (retry_count: {retry_count}, bfs_nr: {geo_data["bfs_nr"]}, canton: {geo_data["canton"]})')

                delta_days = timedelta(days=retry_count)

                incidence_data = CantonService.get_incidences(geo_data['canton'], (datetime.now() - delta_days).strftime(
                    df), (datetime.now() - delta_days).strftime(df), geo_data['bfs_nr'])

            result = geo_data


            print (incidence_data)

            if incidence_data:
                # We only request data for one day, therefor always the first element is of interest
                result['incidence_date'] = incidence_data[0]['date']
                result['incidence'] = incidence_data[0]['incidence']
            else:
                logger.warn(f'No incidence found after some retrys. (retry_count: {retry_count}, bfs_nr: {geo_data["bfs_nr"]}, canton: {geo_data["canton"]})')
                result['incidence_date'] = None
                result['incidence'] = None
        else:
            logger.warn(
                f'GeoService could not return any data for a given waypoint. (lat: {lat}, lng: {lng}, distance: {distance})')
            result = None

        return result
