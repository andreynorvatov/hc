import requests
from typing import Dict


def send_request(url: str, headers: Dict, payload: dict = None) -> Dict | None:
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error response from server: {response.status_code}, {response.text}")
            return None
        else:
            return response.json()
    except Exception as e:
        print(f"Error send request: {e}.")
        return None


