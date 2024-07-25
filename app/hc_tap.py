import requests
from typing import Dict
from datetime import datetime

from settings import HEADERS, CLICKER_TAP_URL


def send_request(url: str, headers: Dict, payload: dict = None) -> Dict | None:
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error from send_request: {response.status_code}, {response.text}")
            return None
        else:
            return response.json()
    except Exception as e:
        print(f"Error from send_request: {e}")
        return None


def get_statistic(data: Dict) -> Dict:
    result = {}

    clicker_user = data["clickerUser"]
    result["total_coins"] = int(clicker_user["totalCoins"])
    result["balance_coins"] = int(clicker_user["balanceCoins"])
    result["level"] = clicker_user["level"]
    result["available_taps_response"] = clicker_user["availableTaps"]
    result["max_taps"] = clicker_user["maxTaps"]
    result["earn_passive_per_sec"] = clicker_user["earnPassivePerSec"]
    result["taps_recover_per_sec"] = clicker_user["tapsRecoverPerSec"]
    result["last_passive_earn"] = int(clicker_user["lastPassiveEarn"])

    return result


def clicker_tap(count, taps):
    payload_clicker_tap = {
        "count": count,
        "availableTaps": taps - count,
        "timestamp": datetime.now().timestamp()
    }

    response_tap = send_request(CLICKER_TAP_URL, HEADERS, payload_clicker_tap)

    return response_tap


def print_statistic(current_timestamp, tap_count, available_taps, statistic):
    print(f"{current_timestamp}] "
          f"send: {tap_count}/{available_taps} | "
          f"+{statistic.get('last_passive_earn')} last_passive_earn | "
          f"available: {statistic.get('available_taps_response')}/{statistic.get('max_taps')} | "
          f"rec_per_sec: {statistic.get('taps_recover_per_sec')} | "
          f"passive_per_sec {statistic.get('earn_passive_per_sec')} | "
          f"balance: {statistic.get('balance_coins')} | "
          f"lvl: {statistic.get('level')} | "
          f"total: {statistic.get('total_coins')}"

          )


# current_timestamp = datetime.now()
# tap_count = 1
# available_taps = 4500
# response_clicker_tap = clicker_tap(tap_count, available_taps)
# if response_clicker_tap is not None:
#     statistic = get_statistic(response_clicker_tap)
#     print_statistic(current_timestamp, tap_count, available_taps, statistic)
