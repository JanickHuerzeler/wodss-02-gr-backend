from datetime import datetime
import json
import logging
import pandas as pd
import pytest
from configManager import ConfigManager
from services.canton_service import CantonService

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


class MockCantonServiceResponse:
    @staticmethod
    def get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        assert canton == 'GR'
        incidences = json.load(open(f'{testdata_path}test_incidences_GR_20210420_20210430.json', 'r'))
        print(len(incidences))

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

        return df_incidences.to_dict('records'), None


@pytest.fixture
def mock_canton_service(monkeypatch):
    def mock_get_incidences(canton, dateFrom, dateTo, bfs_nr=None):
        return MockCantonServiceResponse().get_incidences(canton, dateFrom, dateTo, bfs_nr)

    monkeypatch.setattr(CantonService, 'get_incidences', mock_get_incidences)    


"""
GET '/cantons/<canton>/incidences/'
"""


def test_incidences_without_datefrom_dateto_params(client, app, mock_canton_service):
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


"""
GET /cantons/<canton>/municipalities/<bfsNr>/incidences/
"""


def test_incidences_for_bfs_nr_without_datefrom_dateto_params(client, app, mock_canton_service):
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
    assert len(data) == NUMBER_OF_MOCKED_INCIDENCES_BFSNR    
    for i in range(0, NUMBER_OF_MOCKED_INCIDENCES_BFSNR):
        assert data[i]['bfsNr'] == bfs_nr
        assert data[i]['date'] is not None
        assert data[i]['incidence'] is not None