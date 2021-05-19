from datetime import datetime
import pickle
import pytest
from configManager import ConfigManager
from services.waypoint_service import WaypointService
from data_access.canton_data_access import CantonDataAccess


testdata_path = 'tests/services/testdata/'

df = ConfigManager.get_instance().get_required_date_format()


class MockCantonDataAccessResponse:
    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        # Mocking only canton GR
        assert canton == 'GR'

        with open(f'{testdata_path}GR_get_incidences_20210420_20210427.pkl', 'rb') as fh:
            result = pickle.load(fh)

        dateFrom_date = datetime.strptime(dateFrom, df)
        dateTo_date = datetime.strptime(dateTo, df)

        filtered_result = [i for i in result if (i['bfsNr'] == bfs_nr or bfs_nr is None) and datetime.strptime(
            i['date'], df) >= dateFrom_date and datetime.strptime(i['date'], df) <= dateTo_date]
        return filtered_result, None

    @staticmethod
    def get_incidences_error():
        return None, None

    @staticmethod
    def get_incidences_timeout():
        return None, 408

    @staticmethod
    def get_default_date():
        return datetime(2021, 4, 23)

    @staticmethod
    def get_default_date_one_day_back():
        return datetime(2021, 4, 28)

    @staticmethod
    def get_default_date_two_days_back():
        return datetime(2021, 4, 29)

    @staticmethod
    def get_default_date_three_days_back():
        return datetime(2021, 4, 30)

    @staticmethod
    def get_default_date_four_days_back():
        return datetime(2021, 5, 1)


@pytest.fixture
def mock_canton_data_access(monkeypatch):
    pytest.mock_get_incidences_count = 0

    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        pytest.mock_get_incidences_count += 1
        return MockCantonDataAccessResponse().get_incidences(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(CantonDataAccess, 'get_incidences', mock_get_incidences)

@pytest.fixture
def mock_canton_data_access_error(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockCantonDataAccessResponse().get_incidences_error()

    monkeypatch.setattr(CantonDataAccess, 'get_incidences', mock_get_incidences)

@pytest.fixture
def mock_canton_data_access_timeout(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockCantonDataAccessResponse().get_incidences_timeout()

    monkeypatch.setattr(CantonDataAccess, 'get_incidences', mock_get_incidences)

@pytest.fixture
def mock_canton_data_access_date(monkeypatch):
    def mock_get_default_date():
        return MockCantonDataAccessResponse().get_default_date()

    monkeypatch.setattr(CantonDataAccess, 'get_default_date',
                        mock_get_default_date)


@pytest.fixture
def mock_canton_data_access_date_one_day_back(monkeypatch):
    def mock_get_default_date():
        return MockCantonDataAccessResponse().get_default_date_one_day_back()

    monkeypatch.setattr(CantonDataAccess, 'get_default_date',
                        mock_get_default_date)


@pytest.fixture
def mock_canton_data_access_date_two_days_back(monkeypatch):
    def mock_get_default_date():
        return MockCantonDataAccessResponse().get_default_date_two_days_back()

    monkeypatch.setattr(CantonDataAccess, 'get_default_date',
                        mock_get_default_date)



@pytest.fixture
def mock_canton_data_access_date_three_days_back(monkeypatch):
    def mock_get_default_date():
        return MockCantonDataAccessResponse().get_default_date_three_days_back()

    monkeypatch.setattr(CantonDataAccess, 'get_default_date',
                        mock_get_default_date)

@pytest.fixture
def mock_canton_data_access_date_four_days_back(monkeypatch):
    def mock_get_default_date():
        return MockCantonDataAccessResponse().get_default_date_four_days_back()

    monkeypatch.setattr(CantonDataAccess, 'get_default_date',
                        mock_get_default_date)


def test_single_waypoint_in_kueblis_gr(client, app, mock_canton_data_access, mock_canton_data_access_date):
    """
    Test a single waypoint which lies in Küblis GR returns expected municipality and incidence data
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'canton' in result[0].keys()
    assert result[0]['canton'] == 'GR'
    assert 'plz' in result[0].keys()
    assert result[0]['plz'] == 7240
    assert 'name' in result[0].keys()
    assert result[0]['name'] == 'Küblis'
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] == '2021-04-23'
    assert 'incidence' in result[0].keys()
    assert 'incidence_color' in result[0].keys()
    assert 'geo_shapes' in result[0].keys()


def test_single_waypoint_in_kueblis_gr_retry_1_time(client, app, mock_canton_data_access, mock_canton_data_access_date_one_day_back):
    """
    Test a single waypoint which lies in Küblis GR return expected municipality data and one time retries to get incidence data
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert pytest.mock_get_incidences_count == 2
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] == '2021-04-27'
    assert 'incidence' in result[0].keys()
    assert 'incidence_color' in result[0].keys()

def test_single_waypoint_in_kueblis_gr_retry_2_times(client, app, mock_canton_data_access, mock_canton_data_access_date_two_days_back):
    """
    Test a single waypoint which lies in Küblis GR return expected municipality data and two times retries to get incidence data
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert pytest.mock_get_incidences_count == 3
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] == '2021-04-27'
    assert 'incidence' in result[0].keys()
    assert 'incidence_color' in result[0].keys()

def test_single_waypoint_in_kueblis_gr_retry_3_times(client, app, mock_canton_data_access, mock_canton_data_access_date_three_days_back):
    """
    Test a single waypoint which lies in Küblis return expected municipality data and three times retries to get incidence data
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] == '2021-04-27'
    assert 'incidence' in result[0].keys()
    assert 'incidence_color' in result[0].keys()

def test_single_waypoint_in_kueblis_gr_no_incidence_data(client, app, mock_canton_data_access, mock_canton_data_access_date_four_days_back):
    """
    Test a single waypoint which lies in Küblis return expected municipality data but stops after three retries and return no incidence data
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert pytest.mock_get_incidences_count == 4
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] is None
    assert 'incidence' in result[0].keys()
    assert result[0]['incidence'] is None
    assert 'incidence_color' in result[0].keys() 

def test_still_returning_municipality_data_when_canton_data_access_has_error(client, app, mock_canton_data_access_error, mock_canton_data_access_date):
    """
    Test return values when canton data access had an error (i.e. the incidence_color) and that municipality data still gets returned
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert timedout_cantons == set()
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] is None
    assert 'incidence' in result[0].keys()
    assert result[0]['incidence'] is None
    assert 'incidence_color' in result[0].keys()
    assert result[0]['incidence_color'] == '#000000'

def test_still_returning_municipality_data_when_canton_data_access_has_timeout(client, app, mock_canton_data_access_timeout, mock_canton_data_access_date):
    """
    Test return values when a canton data access had a timeout (i.e. the timedout_cantons set) and that municipality data still gets returned
    """
    # Given
    waypoints = [{"lat": 46.91455411444433,
                  "lng": 9.776835128169601}]  # Küblis

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert len(timedout_cantons) == 1
    assert 'GR' in timedout_cantons
    # Municipality data:
    assert len(result) == 1  # Only Küblis
    assert 'bfs_nr' in result[0].keys()
    assert result[0]['bfs_nr'] == 3882
    assert 'incidence_date' in result[0].keys()
    assert result[0]['incidence_date'] is None
    assert 'incidence' in result[0].keys()
    assert result[0]['incidence'] is None
    assert 'incidence_color' in result[0].keys()
    assert result[0]['incidence_color'] == '#000000'

def test_waypoints_outside_switzerland(client, app, mock_canton_data_access, mock_canton_data_access_date):
    """
    Test that waypoints outside Switzerland do not break the waypoint service, but return an empty result
    """
    # Given
    waypoints = [{"lat": 52.51668151528021,
                  "lng": 13.37775078600967}]  # Berlin

    # When
    result, timedout_cantons = WaypointService.get_waypoints_data(waypoints)

    # Then
    assert result == {}
    assert timedout_cantons is None
