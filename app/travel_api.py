import requests

class travel_info():

    def __init__(self, name, base_url, api_key=None):
        self.name = name
        self.base_url = base_url
        self._api_key = api_key
    
        

