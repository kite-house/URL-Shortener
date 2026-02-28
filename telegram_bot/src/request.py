import requests

class Request:
    def __init__(self, backend_host: str = 'backend', backend_port: str = "8000"):
        self.backend_url = f'http://{backend_host}:{backend_port}/api'
    
    def shorten(self, url: str):
        response = requests.post(url = f'{self.backend_url}/shorten', json = {
            "url" : url
        })

        if response.status_code == 200:
            return response.json()
        
        else:
            response_data = response.json()["detail"]
            return {"message": response_data["message"], "body": {"slug": response_data["slug"], "long_url" : response_data['long_url']}}

    def info(self, url: str):
        response = requests.get(url = f'{self.backend_url}/info/{url}')
        
        if response.status_code == 200:
            return response.json()
        
        else:
            response = response.json()['detail']
            return {"message": response['message'], "body" : {"slug": "-", "long_url" : "-", "count_clicks": "-", "date_created": "-"}}
    
request = Request()
