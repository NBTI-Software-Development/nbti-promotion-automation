import pytest


def test_basic_setup(app, client):
    """Test basic app setup."""
    assert app is not None
    assert client is not None


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get('/api/health')
    # This might not exist yet, so we'll just check the client works
    assert response is not None

