from httpx import AsyncClient

async def test_generate_slug(ac: AsyncClient):
    response = await ac.post('/cutback', json = {"url": 'https://test1.com'})
    assert response.status_code == 200
    assert "slug" in response.json() 

    response = await ac.post('/cutback', json = {"url": 'https://test1.com'})
    assert response.status_code == 208

    response = await ac.post('/cutback', json = {'url': "test"})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Input should be a valid URL, relative URL without a base" 

    response = await ac.post('/cutback', json = {'url': 'https://'.join(['w' for _ in range(3000)])})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "URL should have at most 2083 characters" 

    response = await ac.post('/cutback', json = {'url': "https://test2.com"}, params = {'length' : 6})
    assert response.status_code == 200
    assert len(response.json()['slug']) == 6 

    response = await ac.post('/cutback', json = {'url': "https://test3.com"}, params = {'length' : 100})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Input should be less than or equal to 9"

    response = await ac.post('/cutback', json = {'url': "https://test3.com"}, params = {'length' : -1})
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Input should be greater than or equal to 5"

    response = await ac.post('/cutback', json = {'url': "https://test3.com"}, params = {'custom_slug' : "test_slug"})
    assert response.status_code == 200
    assert response.json()['slug'] == 'test_slug'

    response = await ac.post('/cutback', json = {'url': "https://test3.com"}, params = {'custom_slug' : "test_slug"})
    assert response.status_code == 208

    response = await ac.get('/test_slug')
    assert response.status_code == 302

    response = await ac.get('/testnotslug111')
    assert response.status_code == 404

    response = await ac.get('/top')
    assert response.status_code == 200

    response = await ac.get('/info/test_slug')
    assert response.status_code == 200

    response = await ac.get('/info/test_slugxzasdasd')
    assert response.status_code == 404
