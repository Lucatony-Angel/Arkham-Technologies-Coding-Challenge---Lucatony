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
        self.endpoint = "/nuclear-outages/us-nuclear-outages/data/"
        self.timeout = 30

    def fetch_page(self, offset = 0, length = 1000) -> dict[str, Any]:
        url = f"{self.base_url}{self.endpoint}"

        params = [
            ("api_key", self.api_key),
            ("frequency", "daily"),
            ("data[]", "capacity"),
            ("data[]", "outage"),
            ("data[]", "percentOutage"),
            ("sort[0][column]", "period"),
            ("sort[0][direction]", "desc"),
            ("offset", offset),
            ("length", length),
        ]

        try:
            response = requests.get(url, params = params, timeout = self.timeout)

        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Request to EIA API timed out") from exc
        
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("could not connect to EIA API") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Request to EIA API failed: {exc}") from exc
        
        if response.status_code in (401, 403):
            raise RuntimeError("Authentication failed.; Check EIA API key.")
        if response.status_code != 200:
            raise RuntimeError(f"EIA returned status {response.status_code}: {response.text}")
        
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError("EIA API returned invalid JSON.") from exc
        
        response_block = payload.get("response")
        if not isinstance(response_block, dict):
            raise RuntimeError("Malformed API response: missing 'response; object.")
        
        rows = response_block.get("data")
        if not isinstance(rows, list):
            raise RuntimeError("Malformed API response: missing 'response.data' list.")
            
        total_raw = response_block.get("total")
        try:
            if total_raw is not None:
                total = int(total_raw)
            else:
                total = None
        except (TypeError, ValueError):
            total = None

        return {
            "rows": rows,
            "total": total,
            "warinings": payload.get("warnings", []),
        }