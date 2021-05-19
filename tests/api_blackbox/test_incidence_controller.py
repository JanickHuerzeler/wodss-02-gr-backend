from datetime import datetime
import json
import logging
import pandas as pd
import pytest
from configManager import ConfigManager
from services.incidence_service import IncidenceService

application_root = ConfigManager.get_instance().get_application_root()
# Enforce trailing slash
application_root = application_root if application_root.endswith(
    '/') else f'{application_root}/'

testdata_path = 'tests/api_blackbox/testdata/'

df = ConfigManager.get_instance().get_required_date_format()

MOCK_CANTON = 'GR'
NUMBER_OF_MOCKED_INCIDENCES = 1111
NUMBER_OF_MOCKED_INCIDENCES_BFSNR = 11
default_language = 'de-DE'


class MockIncidenceServiceResponse:
    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        assert canton == 'GR'
        incidences = json.load(open(f'{testdata_path}test_incidences_GR_20210420_20210430.json', 'r'))        

        df_incidences = pd.DataFrame(incidences)

        if(bfs_nr is not None):
            df_incidences = df_incidences[df_incidences['bfsNr'] == int(bfs_nr)]        

        dateFrom_date = datetime.strptime(dateFrom, df)
        dateTo_date = datetime.strptime(dateTo, df)

        df_incidences['real_date'] = df_incidences['date'].apply(lambda d: datetime.strptime(d, df))

        if(dateFrom is not None):
            df_incidences = df_incidences[df_incidences['real_date'] >= dateFrom_date]            

        if(dateTo is not None):
            df_incidences = df_incidences[df_incidences['real_date'] <= dateTo_date]

        df_incidences.drop(columns=['real_date'], inplace=True)

        return df_incidences.to_dict('records'), 200

    @staticmethod
    def get_incidences_timedout(canton, dateFrom, dateTo, bfs_nr=None):
        return None, 408


    @staticmethod
    def get_incidences_canton_unavailable(canton, dateFrom, dateTo, bfs_nr=None):
        return None, 404


    @staticmethod
    def get_incidences_incidence_service_error(canton, dateFrom, dateTo, bfs_nr=None):
        return None, None


    @staticmethod
    def get_incidences_incidence_service_500_error(canton, dateFrom, dateTo, bfs_nr=None):
        return None, 500


@pytest.fixture
def mock_incidence_service(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockIncidenceServiceResponse().get_incidences(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(IncidenceService, 'get_incidences', mock_get_incidences)    


@pytest.fixture
def mock_incidence_service_timedout(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockIncidenceServiceResponse().get_incidences_timedout(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(IncidenceService, 'get_incidences', mock_get_incidences)


@pytest.fixture
def mock_incidence_service_canton_unavailable(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockIncidenceServiceResponse().get_incidences_canton_unavailable(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(IncidenceService, 'get_incidences', mock_get_incidences)


@pytest.fixture
def mock_incidence_service_error(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockIncidenceServiceResponse().get_incidences_incidence_service_error(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(IncidenceService, 'get_incidences', mock_get_incidences)


@pytest.fixture
def mock_incidence_service_500_error(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockIncidenceServiceResponse().get_incidences_incidence_service_500_error(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(IncidenceService, 'get_incidences', mock_get_incidences)


"""
GET '/cantons/<canton>/incidences/'
"""


def test_incidences_without_datefrom_dateto_params(client, app, mock_incidence_service):
    """
    Check if cantons/<canton>/incidences/ returns 
    - a list of all mocked incidences
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date is given
    - each bfsNr is given
    - each incidence is given
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert len(data) == NUMBER_OF_MOCKED_INCIDENCES    
    for i in range(0, NUMBER_OF_MOCKED_INCIDENCES):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None


@pytest.mark.parametrize("canton", ["AGG", "GRR", "Basel", "A1"])
def test_incidences_wrong_canton_format(client, app, canton):
    """
    Check if falsely formatted canton returns 
    - status code 400 bad request 
    - error message describing wrong canton format
    """
    # Given
    url = application_root+'cantons/'+canton+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid format for parameter "canton" (required: 2 chars)' in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('2020-02-28', '2020-02-27'), ('2021-02-14', '2021-02-13')])
def test_incidences_datefrom_bigger_than_dateTo(client, app, dateFrom, dateTo):
    """
    Check if we get a 400 status code if dateFrom is bigger than dateTo
    - 400 status code
    - error message explaining required semantic
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo)' in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('28.02.2020', '2020-02-27'), ('20210214', '2021-02-13')])
def test_incidences_datefrom_invalid_format(client, app, dateFrom, dateTo):
    """
    Check if invalid dateFrom format returns
    - status code 400
    - error message explaining required format
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "dateFrom" (required: {df})', encoding='UTF-8') in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('2020-03-01', '27.03.2020'), ('2021-04-15', '20210513')])
def test_incidences_dateto_invalid_format(client, app, dateFrom, dateTo):
    """
    Check if invalid dateTo format returns
    - status code 400
    - error message explaining required format
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "dateTo" (required: {df})', encoding='UTF-8') in response.get_data()


def test_incidences_unsupported_language(client, app, mock_incidence_service, caplog):
    """
    Check if request with unsupported language returns
    - still status code 200
    - still expected json data
    - made entry into log switching to default language
    """
    # Given
    unsupported_language = 'fr-FR'
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/?language=' + unsupported_language

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    # Language param does nothing, but we can check the log!
    assert ('controllers.incidence_controller', logging.DEBUG, f'Invalid language (fr-FR), using default language instead ({default_language}).') in caplog.record_tuples
    assert len(data) == NUMBER_OF_MOCKED_INCIDENCES    
    for i in range(0, NUMBER_OF_MOCKED_INCIDENCES):
        assert data[i]['bfsNr'] is not None
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None


def test_incidences_incidence_service_timedout(client, app, mock_incidence_service_timedout):
    """
    Check if timeout in canton service returns
    - status code 408
    - error message describing timeout in canton service
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 408
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Canton service {MOCK_CANTON} timed out', encoding='utf8') in response.get_data()


def test_incidences_incidence_service_canton_unavailable(client, app, mock_incidence_service_canton_unavailable):
    """
    Check if request with unavailable canton returns
    - status code 404
    - message describe that no implementation for given canton is available
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'No canton found for "{MOCK_CANTON}".', encoding='utf8') in response.get_data()


def test_incidences_incidence_service_error(client, app, mock_incidence_service_error):
    """
    Check if error in canton service returns
    - status code 502
    - error message describing which canton service had an error
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 502
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Could not get data from canton service "{MOCK_CANTON}".', encoding='utf8') in response.get_data()


def test_incidences_incidence_service_500_error(client, app, mock_incidence_service_500_error):
    """
    Check if error in canton service returns
    - status code 502
    - error message describing which canton service had an error including its status code
    """
    # Given
    url = application_root+'cantons/'+MOCK_CANTON+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 502
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Could not get data from canton service "{MOCK_CANTON}" (status 500).', encoding='utf8') in response.get_data()



"""
GET /cantons/<canton>/municipalities/<bfsNr>/incidences/
"""


def test_incidences_for_bfs_nr_without_datefrom_dateto_params(client, app, mock_incidence_service):
    """
    Check if /cantons/<canton>/municipalities/<bfsNr>/incidences/ returns 
    - a list of all mocked incidences of the given bfsNr
    - each incidence list item with 
        - bfsNr [integer]
        - date [date]
        - incidence [float]
    - each date is given
    - each bfsNr equals given bfsNr
    - each incidence is given
    """
    # Given
    bfs_nr = 3981
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    assert len(data) == NUMBER_OF_MOCKED_INCIDENCES_BFSNR    
    for i in range(0, NUMBER_OF_MOCKED_INCIDENCES_BFSNR):
        assert data[i]['bfsNr'] == bfs_nr
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None


def test_incidences_for_bfs_nr_unsupported_language(client, app, mock_incidence_service, caplog):
    """
    Check if request with unsupported language returns
    - still status code 200
    - still expected json data
    - made entry into log switching to default language
    """
    # Given
    unsupported_language = 'fr-FR'
    bfs_nr = 3981
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/?language=' + unsupported_language

    # When
    response = client.get(url)
    data = response.get_json()

    # Then
    assert response.status_code == 200
    # Language param does nothing, but we can check the log!
    assert ('controllers.incidence_controller', logging.DEBUG, f'Invalid language (fr-FR), using default language instead ({default_language}).') in caplog.record_tuples
    assert len(data) == NUMBER_OF_MOCKED_INCIDENCES_BFSNR    
    for i in range(0, NUMBER_OF_MOCKED_INCIDENCES_BFSNR):
        assert data[i]['bfsNr'] == bfs_nr
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None


def test_incidences_for_bfs_nr_incidence_service_timedout(client, app, mock_incidence_service_timedout):
    """
    Check if timeout in canton service returns
    - status code 408
    - error message describing timeout in canton service
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 408
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Canton service {MOCK_CANTON} timed out', encoding='utf8') in response.get_data()


def test_incidences_for_bfs_nr_incidence_service_canton_unavailable(client, app, mock_incidence_service_canton_unavailable):
    """
    Check if request with unavailable canton returns
    - status code 404
    - message describe that no implementation for given canton is available
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'No canton found for "{MOCK_CANTON}".', encoding='utf8') in response.get_data()


@pytest.mark.parametrize("canton", ["AGG", "GRR", "Basel", "A1"])
def test_incidences_for_bfs_nr_wrong_canton_format(client, app, canton):
    """
    Check if falsely formatted canton returns 
    - status code400 bad request
    - error message describing wrong canton format
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+canton+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid format for parameter "canton" (required: 2 chars)' in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('2020-02-28', '2020-02-27'), ('2021-02-14', '2021-02-13')])
def test_incidences_for_bfs_nr_datefrom_bigger_than_dateTo(client, app, dateFrom, dateTo):
    """
    Check if we get a 400 status code if dateFrom is bigger than dateTo
    - 400 status code
    - correct content-type
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b'Invalid semantic in dates (required: dateFrom <= dateTo)' in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('28.02.2020', '2020-02-27'), ('20210214', '2021-02-13')])
def test_incidences_for_bfs_nr_datefrom_invalid_format(client, app, dateFrom, dateTo):
    """
    Check if invalid dateFrom format returns
    - status code 400
    - error message explaining required format
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "dateFrom" (required: {df})', encoding='UTF-8') in response.get_data()


@pytest.mark.parametrize("dateFrom, dateTo", [('2020-03-01', '27.03.2020'), ('2021-04-15', '20210513')])
def test_incidences_for_bfs_nr_dateto_invalid_format(client, app, dateFrom, dateTo):
    """
    Check if invalid dateTo format returns
    - status code 400
    - error message explaining required format
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/?dateFrom='+dateFrom+'&dateTo='+dateTo

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Invalid format for parameter "dateTo" (required: {df})', encoding='UTF-8') in response.get_data()


def test_incidences_for_bfs_nr_incidence_service_error(client, app, mock_incidence_service_error):
    """
    Check if error in canton service returns
    - status code 502
    - error message describing which canton service had an error
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 502
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Could not get data from canton service "{MOCK_CANTON}".', encoding='utf8') in response.get_data()


def test_incidences_for_bfs_nr_incidence_service_500_error(client, app, mock_incidence_service_500_error):
    """
    Check if error in canton service returns
    - status code 502
    - error message describing which canton service had an error including its status code
    """
    # Given
    bfs_nr = 3561
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+str(bfs_nr)+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 502
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes(f'Could not get data from canton service "{MOCK_CANTON}" (status 500).', encoding='utf8') in response.get_data()


def test_incidences_for_bfs_nr_wrong_bfs_nr_format(client, app, mock_incidence_service):
    """
    Check if wrong bfsNr format returns
    - status code 400
    - error message describing expected bfsNr format
    """
    # Given
    bfs_nr = '3561-12'
    url = application_root+'cantons/'+MOCK_CANTON+'/municipalities/'+bfs_nr+'/incidences/'

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert bytes('Invalid format for parameter "bfsNr" (required: 4-digit number)', encoding='utf8') in response.get_data()
