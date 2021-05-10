import json
import pytest
from configManager import ConfigManager
from services.canton_service import CantonService

application_root = ConfigManager.get_instance().get_application_root()
# Enforce trailing slash
application_root = application_root if application_root.endswith(
    '/') else f'{application_root}/'

MOCK_CANTON = 'GR'
NUMBER_OF_MOCKED_MUNICIPALITIES = 2


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

        return switcher.get(int(bfs_nr), [])

@pytest.fixture
def mock_canton_service(monkeypatch):
    def mock_get_municipalities(canton):
        return MockCantonServiceResponse().get_municipalities(canton)

    def mock_get_municipality(canton, bfs_nr):
        return MockCantonServiceResponse().get_municipality(canton, bfs_nr)

    monkeypatch.setattr(CantonService, 'get_municipalities', mock_get_municipalities)
    monkeypatch.setattr(CantonService, 'get_municipality', mock_get_municipality)


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

    # Then
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    data = response.get_json()
    assert len(data) == NUMBER_OF_MOCKED_MUNICIPALITIES
