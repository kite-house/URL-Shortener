import requests

class Request:
    def __init__(self):
        self.backend_url = 'https://backend:8000'
    
    def cutback(self, url: str):
        response = requests.get(url = f'{self.backend_url}/cutback', json = {
            "url" : url
        })
        return response