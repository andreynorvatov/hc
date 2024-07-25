from datetime import datetime

from hc_tap import send_request, clicker_tap_request
from settings import HEADERS, BOOSTS_FOR_BUY_URL, BUY_BOOSTS_URL


def get_cooldown_seconds_boost_full_available_taps():
    check_boost_response = send_request(BOOSTS_FOR_BUY_URL, HEADERS)

    if check_boost_response:
        boost_full_available_taps = \
            [i for i in check_boost_response["boostsForBuy"] if i["id"] == "BoostFullAvailableTaps"][0]
        print(boost_full_available_taps)
        id = boost_full_available_taps["id"]
        max_level = boost_full_available_taps["maxLevel"]
        cooldown_seconds = boost_full_available_taps["cooldownSeconds"]

        return int(cooldown_seconds) if cooldown_seconds != 0 else 0
    else:
        return 999999


def get_available_taps():
    tap_response = clicker_tap_request(1, 6000)
    if tap_response:
        available_taps = tap_response["clickerUser"]["availableTaps"]

        return available_taps
    else:
        return 0


def boost_full_available_taps(do_boost: bool = False):
    cooldown_seconds = get_cooldown_seconds_boost_full_available_taps()
    if cooldown_seconds != 0:
        print(f"Boost is not ready yet. Cooldown: {cooldown_seconds}sec")
    else:
        if do_boost:
            print("Do Boost")
            available_taps = get_available_taps()

            drop_all_available_taps = clicker_tap_request(available_taps, 4500)
            check_drop = drop_all_available_taps["clickerUser"]["availableTaps"]
            print(f"Drop all available taps: {available_taps} -> {check_drop}")

            data = {"boostId": "BoostFullAvailableTaps", "timestamp": datetime.now().timestamp()}
            buy_boosts = send_request(BUY_BOOSTS_URL, HEADERS, data)

            available_taps = get_available_taps()
            drop_all_available_taps = clicker_tap_request(available_taps, 4500)
            check_drop = drop_all_available_taps["clickerUser"]["availableTaps"]
            print(f"Drop all boosted taps: {available_taps} -> {check_drop}")

        else:
            print(f"Only check do_boost = {do_boost}")

# boost_full_available_taps(True)
