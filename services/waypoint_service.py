import requests
from datetime import datetime, timedelta
from configManager import ConfigManager
import logging
from services.geo_service import GeoService
from services.canton_service import CantonService
import pandas as pd
import json
import math
import matplotlib
import matplotlib.pyplot as pyplot
from shapely.geometry import shape, GeometryCollection, Point


logger = logging.getLogger(__name__)
df = ConfigManager.get_instance().get_required_date_format()
incidence_retry_days: int = ConfigManager.get_instance().get_incidence_retry_days()
search_radius: int = ConfigManager.get_instance().get_geoservice_search_radius()
use_local_geo_data: bool = ConfigManager.get_instance().get_use_local_geo_data()
no_incidence_color: str = ConfigManager.get_instance().get_no_incidence_color()


class WaypointService:

    @staticmethod
    def get_waypoints_data(waypoints) -> (dict, set):

        municipalities_geo_data = []
        timedout_cantons = set()

        if use_local_geo_data:
            logger.info(
                'Use local geo data to retreive municipalities for coordinates')
            municipalities_geo_data = GeoService.get_local_geodata(waypoints)
        else:
            # Loop all given waypoints and find municipalities for them
            # One Waypoint can return multiple municipalities due to search_radius
            logger.info(
                'Use webservice geo data to retreive municipalities for coordinates')
            for waypoint in waypoints:
                result = GeoService.get_geodata(
                    waypoint['lat'], waypoint['lng'], search_radius)
                if result:
                    municipalities_geo_data.extend(result)

        df_municipalities_geo_data = pd.DataFrame.from_dict(
            municipalities_geo_data)
        df_municipalities_geo_data.drop_duplicates(
            subset=['plz'], inplace=True)

        unique_municipalities = df_municipalities_geo_data.drop_duplicates(
            subset=['bfs_nr']).to_dict('records')

        if unique_municipalities:
            df_municipalities_incidence_data = pd.DataFrame()
            # For every found municipality, try to fetch corona data
            for municipality in unique_municipalities:
                incidence_data, status = CantonService.get_incidences(municipality['canton'], CantonService.get_default_date().strftime(
                    df), CantonService.get_default_date().strftime(df), municipality['bfs_nr'])

                retry_count = 0

                # If there was no data for 'today' go back one or two days and try to load those
                # If incidence_data was None, the canton is not available (or threw an error), do not retry
                while retry_count < 3 and incidence_data == []:
                    retry_count += 1
                    logger.debug(
                        f'Retrying to get incidence. (retry_count: {retry_count}, bfs_nr: {municipality["bfs_nr"]}, canton: {municipality["canton"]})')

                    delta_days = timedelta(days=retry_count)

                    incidence_data, status = CantonService.get_incidences(municipality['canton'], (CantonService.get_default_date() - delta_days).strftime(
                        df), (CantonService.get_default_date() - delta_days).strftime(df), municipality['bfs_nr'])

                if incidence_data:
                    df_incidence_data = pd.DataFrame.from_dict(incidence_data)
                    df_municipalities_incidence_data = df_municipalities_incidence_data.append(
                        df_incidence_data)
                else:
                    df_incidence_data = pd.DataFrame(
                        columns={'bfsNr', 'date', 'incidence'})
                    df_municipalities_incidence_data = df_municipalities_incidence_data.append(
                        df_incidence_data)

                    logger.warning(
                        f'No incidence found. (retry_count: {retry_count}, bfs_nr: {municipality["bfs_nr"]}, canton: {municipality["canton"]})')

                if status == 408:
                    timedout_cantons.add(municipality['canton'])
                    logger.warning(
                        f'Timeout occured for canton: {municipality["canton"]}')

        else:
            logger.warning(
                f'GeoService could not return any data for the given waypoints.')
            return {}, None

        result = df_municipalities_geo_data.merge(
            df_municipalities_incidence_data, left_on='bfs_nr', right_on='bfsNr', how='left')
        result.drop(columns={'bfsNr'}, inplace=True)
        result.rename(columns={'date': 'incidence_date'}, inplace=True)

        # Color maps from: https://matplotlib.org/stable/tutorials/colors/colormaps.html#sequential
        color_map = pyplot.cm.get_cmap('RdYlGn_r')

        # Normalize values from 0 to 750 into 0 to 1
        norm = matplotlib.colors.Normalize(vmin=0, vmax=750)

        # Make gray when incidence is 0 or below or any other thing (should mark that it's missing)
        result['incidence_color'] = result['incidence'].apply(
            lambda incidence: matplotlib.colors.rgb2hex(color_map(norm(incidence))) if not math.isnan(incidence) else no_incidence_color)

        # Replace NaN values with None to ensure jsonify sets it to null
        result = result.where(pd.notnull(result), None)

        print(result)

        return result.to_dict('records'), timedout_cantons
