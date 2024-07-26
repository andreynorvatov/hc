import requests
from typing import Dict

from logger import logging

logger = logging.getLogger(__name__)

def send_request(url: str, headers: Dict, payload: dict = None) -> Dict | None:
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"[SendRequest] Error response from server: {response.status_code}, {response.text}")
            return None
        else:
            return response.json()
    except Exception as e:
        logger.error(f'[SendRequest] Error send request: {e}.')
        return None


