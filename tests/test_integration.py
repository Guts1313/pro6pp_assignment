import pytest
from app import create_app  # Assuming your app factory is in app.py


@pytest.fixture
def app():
    """
    Creates a test instance of the Flask app.
    """
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,  # Enable testing mode
    })
    return flask_app


@pytest.fixture
def client(app):
    """
    Provides a test client for the Flask app.
    """
    return app.test_client()


def test_get_addresses_valid_city(client):
    """
    Test /addresses endpoint with a valid city.
    """
    response = client.get("/addresses?city=Madrid")
    assert response.status_code == 200
    data = response.get_json()

    assert "city" in data
    assert "total_matches" in data
    assert "unique_addresses" in data
    assert data["city"].lower() == "madrid"
    assert isinstance(data["unique_addresses"], list)


def test_get_addresses_invalid_city(client):
    """
    Test /addresses endpoint with an invalid city (no matches).
    """
    response = client.get("/addresses?city=InvalidCity")
    assert response.status_code == 404
    data = response.get_json()

    assert "error" in data
    assert data["error"] == "No addresses found for city: InvalidCity"


def test_get_addresses_missing_city_param(client):
    """
    Test /addresses endpoint without the city parameter.
    """
    response = client.get("/addresses")
    assert response.status_code == 400
    data = response.get_json()

    assert "error" in data
    assert data["error"] == "Missing city parameter"


def test_internal_server_error(client, monkeypatch):
    """
    Simulates an internal server error for /addresses.
    """
    def mock_filter_by_city(self, city_name):
        raise Exception("Mocked exception")

    # Temporarily replace the filter_by_city method with a mock
    from data_manager import DataManager
    monkeypatch.setattr(DataManager, "filter_by_city", mock_filter_by_city)

    response = client.get("/addresses?city=Madrid")
    assert response.status_code == 500
    data = response.get_json()

    assert "error" in data
    assert data["error"] == "Mocked exception"

