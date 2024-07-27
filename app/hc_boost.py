from datetime import datetime

from hc_tap import send_request, clicker_tap_request
from settings import HEADERS, BOOSTS_FOR_BUY_URL, BUY_BOOSTS_URL

from logger import logging

logger = logging.getLogger(__name__)


def get_cooldown_seconds_boost_full_available_taps():
    check_boost_response = send_request(BOOSTS_FOR_BUY_URL, HEADERS)

    if check_boost_response:
        boosts_for_buy_response = [i for i in check_boost_response["boostsForBuy"] if i["id"] == "BoostFullAvailableTaps"][0]
        cooldown_seconds = boosts_for_buy_response["cooldownSeconds"]

        return int(cooldown_seconds) if cooldown_seconds != 0 else 0
    else:
        return 999999


def get_available_taps():
    tap_response = clicker_tap_request(1, 6000)
    if tap_response:
        available_taps = tap_response["clickerUser"]["availableTaps"]
        return available_taps
    else:
        return None


def boost_full_available_taps(do_boost: bool = False):
    cooldown_seconds = get_cooldown_seconds_boost_full_available_taps()
    if cooldown_seconds != 0:
        # print(f"Boost is not ready yet. Cooldown: {cooldown_seconds}sec")
        logger.info(f"[HC Boost] Boost is not ready yet. Cooldown: {cooldown_seconds}sec")
    else:
        if do_boost:
            available_taps = get_available_taps()
            if available_taps:
                drop_all_available_taps = clicker_tap_request(available_taps, 4500)
                check_drop = drop_all_available_taps["clickerUser"]["availableTaps"]
                # print(f"Do Boost. Drop all available taps: {available_taps} -> {check_drop}")
                logger.info(f"[HC Boost] Do Boost. Drop all available taps: {available_taps} -> {check_drop}")

            data = {"boostId": "BoostFullAvailableTaps", "timestamp": datetime.now().timestamp()}
            buy_boosts = send_request(BUY_BOOSTS_URL, HEADERS, data)
            if buy_boosts:
                available_taps = get_available_taps()
                drop_all_available_taps = clicker_tap_request(available_taps, 4500)
                check_drop = drop_all_available_taps["clickerUser"]["availableTaps"]
                # print(f"Do Boost. Drop all boosted taps: {available_taps} -> {check_drop}")
                logger.info(f"[HC Boost] Do Boost. Drop all boosted taps: {available_taps} -> {check_drop}")

        else:
            # print(f"[HC Boost] No Boost. Only check do_boost = {do_boost}. Cooldown seconds = {cooldown_seconds}")
            logger.warning(f"[HC Boost] No Boost. Only check do_boost = {do_boost}. Cooldown seconds = {cooldown_seconds}")

# boost_full_available_taps(True)
