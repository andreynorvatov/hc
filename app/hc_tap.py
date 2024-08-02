from typing import Dict
from datetime import datetime

from request_default import send_request
from settings import HEADERS, CLICKER_TAP_URL

from logger import logging

logger = logging.getLogger(__name__)


def clicker_tap_request(count, taps):
    payload = {
        "count": count,
        "availableTaps": taps - count,
        "timestamp": int(datetime.now().timestamp())
    }
    response_tap = send_request(CLICKER_TAP_URL, HEADERS, payload)

    return response_tap


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


def print_statistic(tap_count, available_taps, statistic):
    logger.info(f"[HC TAP] "
                f"send: {tap_count}/{available_taps} | "
                f"+{statistic.get('last_passive_earn')} last_passive_earn | "
                f"available: {statistic.get('available_taps_response')}/{statistic.get('max_taps')} | "
                f"rec_per_sec: {statistic.get('taps_recover_per_sec')} | "
                f"passive_per_sec {statistic.get('earn_passive_per_sec')} | "
                f"balance: {statistic.get('balance_coins')} | "
                f"lvl: {statistic.get('level')} | "
                f"total: {statistic.get('total_coins')}"
                )


def clicker_tap(tap_count: int, available_taps: int):
    current_timestamp = datetime.now()
    response_clicker_tap = clicker_tap_request(tap_count, available_taps)
    if response_clicker_tap:
        statistic = get_statistic(response_clicker_tap)
        print_statistic(tap_count, available_taps, statistic)
        return statistic
    return None

# clicker_tap(tap_count=1, available_taps=6500)
