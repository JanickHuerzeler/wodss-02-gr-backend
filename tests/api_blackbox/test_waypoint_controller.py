import pytest
from configManager import ConfigManager

application_root = ConfigManager.get_instance().get_application_root()
# Enforce trailing slash
application_root = application_root if application_root.endswith('/') else f'{application_root}/'


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
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
    assert b'Please provide some waypoints, empty array is not allowed.' in response.get_data()
