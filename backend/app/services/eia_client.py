from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_DELAY = 2  # seconds between retries


class EIAClient:
    def __init__(self):
        self.api_key = os.getenv("EIA_API_KEY")

        if self.api_key is None:
            raise ValueError("Missing EIA_API_KEY environment variable")

        self.base_url = "https://api.eia.gov/v2"
        self.endpoint = "/nuclear-outages/us-nuclear-outages/data/"
        self.timeout = 30

    def fetch_page(self, offset = 0, length = 1000, start_date: str | None = None) -> dict[str, Any]:
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

        if start_date:
            params.append(("filter[period][gte]", start_date))

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                break  # success, exit retry loop
            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    logger.warning("Request timed out, retrying (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    time.sleep(RETRY_DELAY)
                    continue
                raise RuntimeError("Request to EIA API timed out after retries")
            except requests.exceptions.ConnectionError:
                if attempt < MAX_RETRIES - 1:
                    logger.warning("Connection error, retrying (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                    time.sleep(RETRY_DELAY)
                    continue
                raise RuntimeError("Could not connect to EIA API after retries")
            except requests.exceptions.RequestException as exc:
                raise RuntimeError(f"Request to EIA API failed: {exc}") from exc

        if response.status_code in (401, 403):
            raise RuntimeError("Authentication failed. Check EIA API key.")
        if response.status_code != 200:
            raise RuntimeError(f"EIA returned status {response.status_code}: {response.text}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError("EIA API returned invalid JSON.") from exc

        response_block = payload.get("response")
        if not isinstance(response_block, dict):
            raise RuntimeError("Malformed API response: missing 'response' object.")

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
            "warnings": payload.get("warnings", []),
        }
