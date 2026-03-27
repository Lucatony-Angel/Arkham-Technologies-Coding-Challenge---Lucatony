from __future__ import annotations

import os
from typing import Any

import requests

class EIAClient:
    def __init__(self):
        self.api_key = os.getenv("EIA_API_KEY")

        if self.api_key is None:
            raise ValueError("Missing EIA_API_KEY enviorment variable")
        
        self.base_url = "https://api.eia.gov/v2"
        self.endpoint = "/nuclear-outages/us=nuclear-outages/data/"
        self.timeout = 30

    def fetch_page(self, offset = 0, length = 1000):
        url = self.base_url + self.endpoint

        params = {
            "api_key": self.api_key,
            "frequency": "daily",
            "data[]": ["capacity", "outage", "percentOutage"],
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": offset,
            "length": length,
        }

        try:
            response = requests.get(url, params = params, timeout = 30)

        except requests.exceptions.Timeout:
            raise RuntimeError("Request to EIA API timed out")
        
        except requests.exceptions.ConnectionError:
            raise RuntimeError("could not connect to EIA API")
        
        if response.status_code == 401 or response.status_code == 403:
            raise RuntimeError("Authentication failed.; Check EIA API key")