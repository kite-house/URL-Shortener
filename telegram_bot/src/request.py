import requests

class Request:
    def __init__(self, backend_host: str = 'backend', backend_port: str = "8000"):
        self.backend_url = f'http://{backend_host}:{backend_port}/api'
    
    def cutback(self, url: str):
        response = requests.post(url = f'{self.backend_url}/cutback', json = {
            "url" : url
        })


        return response.status_code, response.json()
    
    def info(self, url: str):
        response = requests.get(url = f'{self.backend_url}/info/{url}')
        return response.status_code, response.json()
    
request = Request()