import requests
from datetime import datetime, timedelta
from configManager import ConfigManager
import logging
from services.geo import GeoService
from services.canton import CantonService
import pandas as pd
import json
import matplotlib
import matplotlib.pyplot as pyplot


logger = logging.getLogger(__name__)
df = ConfigManager.get_instance().get_required_date_format()
incidence_retry_days: int = ConfigManager.get_instance().get_incidence_retry_days()
search_radius: int = ConfigManager.get_instance().get_geoservice_search_radius()
nth_waypoint_filter: int = ConfigManager.get_instance().get_nth_waypoint_filter()


class WayPointService:

    @staticmethod
    def get_waypoints_data(waypoints) -> dict:

        # Loop all given waypoints and find municipalities for them
        # One Waypoint can return multiple municipalities due to search_radius
        municipalities_geo_data = []
        for waypoint in waypoints:
            result = GeoService.get_geodata(waypoint['lat'], waypoint['lng'], search_radius)
            if result:
                municipalities_geo_data.extend(result)

        df_municipalities_geo_data = pd.DataFrame.from_dict(municipalities_geo_data)
        df_municipalities_geo_data.drop_duplicates(subset=['plz'], inplace=True)

        unique_municipalities = df_municipalities_geo_data.drop_duplicates(subset=['bfs_nr']).to_dict('records')

        if unique_municipalities:
            df_municipalities_incidence_data = pd.DataFrame()
            # For every found municipality, try to fetch corona data
            for municipality in unique_municipalities:
                # TODO: Error handling for incidence data fetching
                incidence_data = CantonService.get_incidences(municipality['canton'], datetime.now().strftime(
                    df), datetime.now().strftime(df), municipality['bfs_nr'])

                retry_count = 0

                # If there was no data for 'today' go back one or two days and try to load those
                while retry_count < 3 and not incidence_data:
                    retry_count += 1
                    logger.debug(
                        f'Retrying to get incidence. (retry_count: {retry_count}, bfs_nr: {municipality["bfs_nr"]}, canton: {municipality["canton"]})')

                    delta_days = timedelta(days=retry_count)

                    incidence_data = CantonService.get_incidences(municipality['canton'], (datetime.now() - delta_days).strftime(
                        df), (datetime.now() - delta_days).strftime(df), municipality['bfs_nr'])

                if incidence_data:
                    df_incidence_data = pd.DataFrame.from_dict(incidence_data)
                    df_municipalities_incidence_data = df_municipalities_incidence_data.append(df_incidence_data)
                else:
                    df_municipalities_incidence_data = pd.DataFrame(columns={'bfsNr', 'date', 'incidence'})
                    logger.warn(
                        f'No incidence found after some retrys. (retry_count: {retry_count}, bfs_nr: {municipality["bfs_nr"]}, canton: {municipality["canton"]})')

            print('df_municipalities_incidence_data: ')
            print(df_municipalities_incidence_data)
        else:
            # TODO: How do we handle waypoints we did not find a municipality for?
            logger.warn(f'GeoService could not return any data for a given waypoints.')
            return None

        result = df_municipalities_geo_data.merge(
            df_municipalities_incidence_data, left_on='bfs_nr', right_on='bfsNr', how='left')
        result.drop(columns={'bfsNr'}, inplace=True)
        result.rename(columns={'date': 'incidence_date'}, inplace=True)
        # TODO: Is this correct to fill NA with 0? What is our indicator if no data was found?
        result.fillna(0, inplace=True)

        # Color maps from: https://matplotlib.org/stable/tutorials/colors/colormaps.html#sequential
        color_map = pyplot.cm.get_cmap('RdYlGn_r')

        # Normalize values from 0 to 750 into 0 to 1
        norm = matplotlib.colors.Normalize(vmin=0, vmax=750)

        # Make gray when incidence it 0 or below or any other thing (should mark that it's missing)
        result['incidence_color'] = result['incidence'].apply(
            lambda incidence: matplotlib.colors.rgb2hex(color_map(norm(incidence))) if incidence > 0 else '#70706e')

        print('return:')
        print(result)

        return result.to_dict('records')
