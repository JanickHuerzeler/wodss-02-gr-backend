import json
import logging
import pickle
import pytest
from configManager import ConfigManager
from services.waypoint_service import WaypointService

application_root = ConfigManager.get_instance().get_application_root()
# Enforce trailing slash
application_root = application_root if application_root.endswith(
    '/') else f'{application_root}/'

testdata_path = 'tests/api_blackbox/testdata/'
content_type_text_utf8 = 'text/html; charset=utf-8'
content_type_json = 'application/json'
canton_service_timeout_header = 'X-Cantons-Timeout'
access_control_expose_headers = 'Access-Control-Expose-Headers'
default_language = 'de-DE'

bad_waypoints_format_message = b'Array of waypoints must be of format: ["lat": 42.1234, "lng": 8.1234]'


class MockWaypointServiceResponse:
    @staticmethod
    def get_waypoints_data(waypoints) -> (dict, set):
        with open(f'{testdata_path}mock_waypoint_service_result.pkl', 'rb') as fh:
            result = pickle.load(fh)

        return result, set()

    @staticmethod
    def get_waypoints_data_no_response(waypoints) -> (dict, set):
        return {}, None

    @staticmethod
    def get_waypoints_data_single_timed_out_canton(waypoints) -> (dict, set):
        return {}, set(["AG"])

    @staticmethod
    def get_waypoints_data_multiple_timed_out_cantons(waypoints) -> (dict, set):
        return {}, set(["AG", "ZH", "TG"])


@pytest.fixture
def mock_waypoint_service_no_response(monkeypatch):
    def mock_get_waypoints_data(waypoints):
        return MockWaypointServiceResponse().get_waypoints_data_no_response(waypoints)

    monkeypatch.setattr(WaypointService, 'get_waypoints_data', mock_get_waypoints_data)


@pytest.fixture
def mock_waypoint_service_single_timedout_canton(monkeypatch):
    def mock_get_waypoints_data(waypoints):
        return MockWaypointServiceResponse().get_waypoints_data_single_timed_out_canton(waypoints)

    monkeypatch.setattr(WaypointService, 'get_waypoints_data', mock_get_waypoints_data)


@pytest.fixture
def mock_waypoint_service_multiple_timedout_cantons(monkeypatch):
    def mock_get_waypoints_data(waypoints):
        return MockWaypointServiceResponse().get_waypoints_data_multiple_timed_out_cantons(waypoints)

    monkeypatch.setattr(WaypointService, 'get_waypoints_data', mock_get_waypoints_data)


@pytest.fixture
def mock_waypoint_service(monkeypatch):
    def mock_get_waypoints_data(waypoints):
        return MockWaypointServiceResponse().get_waypoints_data(waypoints)

    monkeypatch.setattr(WaypointService, 'get_waypoints_data', mock_get_waypoints_data)


def test_invalid_content_type(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request when conent type not 'application/json'
    """
    # Given
    url = f'{application_root}waypoints/'
    data = []

    # When
    response = client.post(url, data=data, content_type='multipart/form-data')

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert b'Only accept body as JSON with content-type: application/json' in response.get_data()


def test_empty_waypoints_array(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request when passing empty array
    """

    # Given
    url = f'{application_root}waypoints/'

    # When
    response = client.post(url, json=[])

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert b'Please provide some waypoints, empty array is not allowed.' in response.get_data()


def test_multiple_wrong_lat_objects(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where its objects have not correct "lat" properties
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_multiple_wrong_lat_objects.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_multiple_wrong_lng_objects(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where its objects have not correct "lng" properties
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_multiple_wrong_lng_objects.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_single_wrong_lat_objects(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where one single object has no correct "lat" property
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_single_wrong_lat_objects.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_single_wrong_lng_objects(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where one single object has no correct "lng" property
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_single_wrong_lng_objects.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_lng_wrong_format(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where one single object has no correct format for "lng" property
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_lng_wrong_format.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_lat_wrong_format(client, app):
    """
    Check if POST /waypoints/ returns 400 bad request for passing an array
    where one single object has no correct format for "lat" property
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_lat_wrong_format.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 400
    assert response.headers['Content-Type'] == content_type_text_utf8
    assert bad_waypoints_format_message in response.get_data(
    )


def test_no_waypoints_response_still_returns_result(client, app, mock_waypoint_service_no_response):
    """
    Check if POST /waypoints/ still returns 200 (empty result) if Waypoint Service did not return any data
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_waypoints.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type_json
    assert response.json == {}
    assert canton_service_timeout_header not in response.headers


def test_unknown_language(client, app, mock_waypoint_service_no_response, caplog):
    """
    Check if POST /waypoints/ with unknown language parameter still return 200
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_waypoints.json', 'r'))

    # When
    with caplog.at_level(logging.DEBUG):
        response = client.post(url, json=waypoints, query_string={'language': 'it-CH'})

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type_json
    # Language param does nothing, but we can check the log!
    assert ('controllers.waypoint_controller', logging.DEBUG, f'Invalid language (it-CH), using default language instead ({default_language}).') in caplog.record_tuples
    assert response.json == {}
    assert canton_service_timeout_header not in response.headers


def test_single_timedout_canton(client, app, mock_waypoint_service_single_timedout_canton):
    """
    Check if POST /waypoints/ returns correct header for single timedout canton
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_waypoints.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type_json
    assert response.json == {}
    assert canton_service_timeout_header in response.headers
    assert response.headers[canton_service_timeout_header] == "AG"
    # Test if header is correctly exposed
    assert access_control_expose_headers in response.headers
    assert canton_service_timeout_header in response.headers[access_control_expose_headers]


def test_multiple_timedout_cantons(client, app, mock_waypoint_service_multiple_timedout_cantons):
    """
    Check if POST /waypoints/ returns correct header for multiple timedout cantons
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_waypoints.json', 'r'))

    # When
    response = client.post(url, json=waypoints)

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type_json
    assert response.json == {}
    assert canton_service_timeout_header in response.headers
    # Set us unordered, so test with string contains:
    assert "AG" in response.headers[canton_service_timeout_header]
    assert "TG" in response.headers[canton_service_timeout_header]
    assert "ZH" in response.headers[canton_service_timeout_header]
    # Test if header is correctly exposed
    assert access_control_expose_headers in response.headers
    assert canton_service_timeout_header in response.headers[access_control_expose_headers]


def test_successful_request(client, app, mock_waypoint_service):
    """
    Check if POST /waypoints/ with correct body returns correct result
    """
    # Given
    url = f'{application_root}waypoints/'
    waypoints = json.load(
        open(f'{testdata_path}test_waypoints.json', 'r'))

    # When
    response = client.post(url, json=waypoints)
    data = response.get_json()  # data = Array of Municipalities with geo_shapes

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type_json
    # Aarau
    assert data[0]['bfs_nr'] == 4001
    assert data[0]['canton'] == 'AG'
    assert data[0]['incidence'] == 316.91
    assert data[0]['incidence_color'] == "#e2f397"
    assert data[0]['incidence_date'] == "2021-05-03"
    assert data[0]['name'] == "Aarau"
    assert data[0]['plz'] == 5000
    # Unterentfelden
    assert data[1]['bfs_nr'] == 4013
    assert data[1]['canton'] == 'AG'
    assert data[1]['incidence'] == 447.16
    assert data[1]['incidence_color'] == "#fee18d"
    assert data[1]['incidence_date'] == "2021-05-03"
    assert data[1]['name'] == "Unterentfelden"
    assert data[1]['plz'] == 5035
    # Oberentfelden
    assert data[2]['bfs_nr'] == 4010
    assert data[2]['canton'] == 'AG'
    assert data[2]['incidence'] == 376.03
    assert data[2]['incidence_color'] == "#fffebe"
    assert data[2]['incidence_date'] == "2021-05-03"
    assert data[2]['name'] == "Oberentfelden"
    assert data[2]['plz'] == 5036
    # Muhen
    assert data[3]['bfs_nr'] == 4009
    assert data[3]['canton'] == 'AG'
    assert data[3]['incidence'] == 460.71
    assert data[3]['incidence_color'] == "#fed884"
    assert data[3]['incidence_date'] == "2021-05-03"
    assert data[3]['name'] == "Muhen"
    assert data[3]['plz'] == 5037
    # Kölliken
    assert data[4]['bfs_nr'] == 4276
    assert data[4]['canton'] == 'AG'
    assert data[4]['incidence'] == 261.95
    assert data[4]['incidence_color'] == "#bfe47a"
    assert data[4]['incidence_date'] == "2021-05-03"
    assert data[4]['name'] == "Kölliken"
    assert data[4]['plz'] == 5742
    # Hirschthal
    assert data[5]['bfs_nr'] == 4007
    assert data[5]['canton'] == 'AG'
    assert data[5]['incidence'] == 869.03
    assert data[5]['incidence_color'] == "#a50026"
    assert data[5]['incidence_date'] == "2021-05-03"
    assert data[5]['name'] == "Hirschthal"
    assert data[5]['plz'] == 5042
    # Schöftland
    assert data[6]['bfs_nr'] == 4144
    assert data[6]['canton'] == 'AG'
    assert data[6]['incidence'] == 271.06
    assert data[6]['incidence_color'] == "#c5e67e"
    assert data[6]['incidence_date'] == "2021-05-03"
    assert data[6]['name'] == "Schöftland"
    assert data[6]['plz'] == 5040
    # Geo Shapes
    for i in range(0, 6):
        polygons = data[i]['geo_shapes']
        for j in range(0, len(polygons)):
            geo_shapes = polygons[j]
            for k in range(0, len(geo_shapes)):
                coord = geo_shapes[k]
                assert 'lat' in coord.keys()
                assert coord['lat'] > 45.7 and coord['lat'] < 47.9
                assert 'lng' in coord.keys()
                assert coord['lng'] > 5.9 and coord['lng'] < 10.6
