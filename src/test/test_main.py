from fastapi.testclient import TestClient
from src.app.main import app


client = TestClient(app)


def test_create_link():
    response = client.post('/cutback', json= {
        'url' : 'https://test.com'
    })

    assert response.status_code == 200

    response = client.post('/cutback', json= {
        'url' : 'https://test.com'
    })

    assert response.status_code == 208
    