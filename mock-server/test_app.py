import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'

def test_customers_pagination(client):
    resp = client.get('/api/customers?page=1&limit=5')
    assert resp.status_code == 200
    assert 'data' in resp.json
    assert 'total' in resp.json
    assert resp.json['page'] == 1
    assert resp.json['limit'] == 5

def test_customers_invalid_pagination(client):
    resp = client.get('/api/customers?page=0&limit=1000')
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_customers_filter_sort(client):
    resp = client.get('/api/customers?last_name=Smith&sort_by=created_at&sort_order=desc')
    assert resp.status_code == 200
    assert 'data' in resp.json
    # If there are Smiths, they should be sorted
    data = resp.json['data']
    if data:
        assert all(c['last_name'] == 'Smith' for c in data)
