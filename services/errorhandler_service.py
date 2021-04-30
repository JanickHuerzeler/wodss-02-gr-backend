from datetime import datetime
from configManager import ConfigManager
import re


class ErrorHandlerService:
    # check if bfs_nr contains only numbers and does not exceed the length of 4
    @staticmethod
    def check_bfs_nr_format(bfs_nr):
        return bfs_nr.isdecimal() and len(bfs_nr) <= 4

    # check if canton contains only two chars
    @staticmethod
    def check_canton_format(canton):
        return True if re.fullmatch(r'[a-zA-Z]{2}', canton) else False

    # check if date is in the correct format (yyyy-MM-dd)
    @staticmethod
    def check_date_format(date):
        if not date:
            return True

        try:
            datetime.strptime(
                date, ConfigManager.get_instance().get_required_date_format())
            return True
        except ValueError:
            return False

    # check if dateFrom is smaller or equal to dateTo
    @staticmethod
    def check_date_semantic(date_from, date_to):
        if not date_from or not date_to:
            return True

        return date_from <= date_to

    @staticmethod
    def check_waypoints_array_format(waypoints):
        # Expected: [{"lat": 40.123, "lng": 8.123}]
        is_valid = all(
            map(ErrorHandlerService.__check_waypoint_format, waypoints))

        return is_valid

    @staticmethod
    def __check_waypoint_format(waypoint):
        return isinstance(waypoint, dict) and 'lat' in waypoint.keys() and isinstance(waypoint.get('lat'), float) and 'lng' in waypoint.keys() and isinstance(waypoint.get('lng'), float)
