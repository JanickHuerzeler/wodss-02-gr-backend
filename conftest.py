import pytest

from app import get_app
from configManager import ConfigManager
from controllers.waypoint_controller import waypoint_controller
from controllers.incidence_controller import incidence_controller
from controllers.municipality_controller import municipality_controller


@pytest.fixture
def app():
    app = get_app()

    server_config = ConfigManager.get_instance().get_server_config()
    application_root = ConfigManager.get_instance().get_application_root()

    app.register_blueprint(waypoint_controller, url_prefix=application_root)
    app.register_blueprint(incidence_controller, url_prefix=application_root)
    app.register_blueprint(municipality_controller, url_prefix=application_root)

    app.config['DEVELOPMENT'] = server_config["development"]

    yield app


@pytest.fixture
def client(app):
    """
    A test client for the app.

    See: https://github.com/pallets/flask/blob/1.1.2/examples/tutorial/tests/conftest.py
    """
    return app.test_client()
