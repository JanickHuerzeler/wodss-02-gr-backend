import json
import logging
import pytest
from configManager import ConfigManager
from services.canton_service import CantonService

application_root = ConfigManager.get_instance().get_application_root()
# Enforce trailing slash
application_root = application_root if application_root.endswith(
    '/') else f'{application_root}/'

MOCK_CANTON = 'GR'
NUMBER_OF_MOCKED_MUNICIPALITIES = 2
default_language = 'de-DE'


class MockCantonServiceResponse:
    @staticmethod
    def get_municipalities(canton):
        # Mocking only (parts of) canton GR
        assert canton == MOCK_CANTON
        return [{"area": 42.51, "bfsNr": 3506, "canton": "GR", "name": "Vaz/Obervaz", "population": 2780},
                {"area": 190.14, "bfsNr": 3544, "canton": "GR", "name": "Berg\u00fcn Filisur", "population": 905}], None

    @staticmethod
    def get_municipality(canton, bfs_nr) -> object:
        switcher = {
            3506: {"area": 42.51, "bfsNr": 3506, "canton": "GR", "name": "Vaz/Obervaz", "population": 2780},
            3544: {"area": 190.14, "bfsNr": 3544, "canton": "GR", "name": "Berg\u00fcn Filisur", "population": 905}
        }

        return switcher.get(int(bfs_nr), []), None


    @staticmethod
    def get_municipalities_unavailable_canton(canton):
        return [], None

    @staticmethod
    def get_municipality_unavailable_canton(canton, bfs_nr):
        return {}, None

    @staticmethod
    def get_municipalities_timedout(canton):
        return None, 408

    @staticmethod
    def get_municpality_timedout(canton, bfs_nr):
        return None, 408


@pytest.fixture
def mock_canton_service(monkeypatch):
    def mock_get_municipalities(canton):
        return MockCantonServiceResponse().get_municipalities(canton)

    def mock_get_municipality(canton, bfs_nr):
        return MockCantonServiceResponse().get_municipality(canton, bfs_nr)

    monkeypatch.setattr(CantonService, 'get_municipalities', mock_get_municipalities)
    monkeypatch.setattr(CantonService, 'get_municipality', mock_get_municipality)


@pytest.fixture
def mock_canton_service_unavailable_canton(monkeypatch):
    def mock_get_municipalities(canton):
        return MockCantonServiceResponse().get_municipalities_unavailable_canton(canton)

    def mock_get_municipality(canton, bfs_nr):
        return MockCantonServiceResponse().get_municipality_unavailable_canton(canton, bfs_nr)

    monkeypatch.setattr(CantonService, 'get_municipalities', mock_get_municipalities)
    monkeypatch.setattr(CantonService, 'get_municipality', mock_get_municipality)


@pytest.fixture
def mock_canton_service_timedout(monkeypatch):
    def mock_get_municipalities(canton):
        return MockCantonServiceResponse().get_municipalities_timedout(canton)

    def mock_get_municipality(canton, bfs_nr):
        return MockCantonServiceResponse().get_municpality_timedout(canton, bfs_nr)

    monkeypatch.setattr(CantonService, 'get_municipalities', mock_get_municipalities)
    monkeypatch.setattr(CantonService, 'get_municipality', mock_get_municipality)


"""
GET /cantons/<canton>/municipalities/
"""


def test_municipalities_base_route(client, app, mock_canton_service):
    """
    Check if /cantons/{canton}/municipalities/ route returns
    - correct content-type "application/json"
    - status code 200
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == NUMBER_OF_MOCKED_MUNICIPALITIES


def test_municipalities_unavailable_canton(client, app, mock_canton_service_unavailable_canton):
    # Given
    unavailable_canton = 'VD'
    url = application_root+'cantons/'+unavailable_canton+'/municipalities/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'No municipalities found for canton "{unavailable_canton}".', encoding='utf8') in response.get_data()


def test_municipalities_invalid_canton_format(client, app, mock_canton_service):
    # Given
    invalid_canton = 'GRR'
    url = application_root+'cantons/'+invalid_canton+'/municipalities/'

    # When
    response = client.get(url)    

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "canton" (required: 2 chars)', encoding='utf8') in response.get_data()


def test_municipalities_canton_service_timedout(client, app, mock_canton_service_timedout):
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 408
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Canton service {MOCK_CANTON} timed out', encoding='utf8') in response.get_data()


def test_municipalities_wrong_language_still_works(client, app, mock_canton_service, caplog):
    # Given    
    url = application_root+'cantons/' + MOCK_CANTON + '/municipalities/'

    # When
    response = client.get(url, query_string={'language': 'it-CH'})
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(data) == NUMBER_OF_MOCKED_MUNICIPALITIES
    # Language param does nothing, but we can check the log!
    assert ('controllers.municipality_controller', logging.DEBUG, f'Invalid language (it-CH), using default language instead ({default_language}).') in caplog.record_tuples


"""
GET /cantons/<canton>/municipalities/<bfsNr>/
"""


def test_municipality_base_route_with_bfs_nr(client, app, mock_canton_service):
    """
    Check if /cantons/{canton}/municipalities/{bfsNr} route returns
    - correct content-type "application/json"
    - status code 200
    """
    # Given
    bfs_nr = 3506  # Vaz/Obervaz
    url = application_root+'cantons/' + MOCK_CANTON + '/municipalities/' + str(bfs_nr) + '/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert 'bfsNr' in data.keys()
    assert data['bfsNr'] == bfs_nr


def test_municipality_unavailable_canton_with_bfs_nr(client, app, mock_canton_service_unavailable_canton):
    # Given
    unavailable_canton = 'VD'
    unavailable_bfs_nr = 5401  # Aigle
    url = application_root+'cantons/'+unavailable_canton+'/municipalities/' + str(unavailable_bfs_nr) + '/'

    # When
    response = client.get(url)    

    # Then
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'No municipality found for canton "{unavailable_canton}" and bfsNr "{unavailable_bfs_nr}".', encoding='utf8') in response.get_data()


def test_municipality_invalid_canton_format(client, app, mock_canton_service):
    # Given
    invalid_canton = 'AGR'
    bfs_nr = 3544  # Bergün Filisur
    url = application_root+'cantons/'+invalid_canton+'/municipalities/' + str(bfs_nr) + '/'

    # When
    response = client.get(url)    

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "canton" (required: 2 chars)', encoding='utf8') in response.get_data()


def test_municipality_canton_service_timedout(client, app, mock_canton_service_timedout):
    # Given
    bfs_nr = 3544  # Bergün Filisur
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/' + str(bfs_nr) + '/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 408
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Canton service {MOCK_CANTON} timed out', encoding='utf8') in response.get_data()


def test_municipality_wrong_bfs_nr_format(client, app, mock_canton_service):
    # Given
    bfs_nr = '3544-12'
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/' + bfs_nr + '/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes('Invalid format for parameter "bfsNr" (required: 4-digit number)', encoding='utf8') in response.get_data()


def test_municipality_wrong_language_still_works(client, app, mock_canton_service, caplog):
    # Given
    bfs_nr = 3506  # Vaz/Obervaz
    url = application_root+'cantons/' + MOCK_CANTON + '/municipalities/' + str(bfs_nr) + '/'

    # When
    response = client.get(url, query_string={'language': 'it-CH'})
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert 'bfsNr' in data.keys()
    assert data['bfsNr'] == bfs_nr
    # Language param does nothing, but we can check the log!
    assert ('controllers.municipality_controller', logging.DEBUG, f'Invalid language (it-CH), using default language instead ({default_language}).') in caplog.record_tuples
