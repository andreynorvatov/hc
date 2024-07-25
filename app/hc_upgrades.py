import requests
from datetime import datetime
import csv

from hc_tap import send_request
from settings import HEADERS, UPGRADES_FOR_BUY_URL, BAD_CONDITION_TYPE, BUY_UPGRADE_URL


def upgrade(test_balance: int, top_limit: int = 3, is_upgrade: bool = False):
    response = send_request(UPGRADES_FOR_BUY_URL, HEADERS)

    upgrades_for_buy_response = response["upgradesForBuy"]
    len_of_upgrades = len(upgrades_for_buy_response)

    res = []

    for upgrades_for_buy in upgrades_for_buy_response:
        res_dict = {}

        id = upgrades_for_buy["id"]
        section = upgrades_for_buy["section"]
        price = upgrades_for_buy["price"]
        profit_per_hour = upgrades_for_buy["profitPerHour"]
        condition = upgrades_for_buy["condition"]
        current_profit_per_hour = upgrades_for_buy["currentProfitPerHour"]
        profit_per_hour_delta = upgrades_for_buy["profitPerHourDelta"]
        level = upgrades_for_buy["level"]
        is_available = upgrades_for_buy["isAvailable"]
        is_expired = upgrades_for_buy["isExpired"]
        cooldown_seconds = upgrades_for_buy.get("cooldownSeconds")

        res_dict["id"] = id
        res_dict["section"] = section
        res_dict["price"] = price
        res_dict["profit_per_hour"] = profit_per_hour
        res_dict["condition"] = condition

        bad_condition_type_coefficient = 0
        if condition is not None:
            res_dict["condition_type"] = condition["_type"]
            if condition["_type"] in BAD_CONDITION_TYPE:
                bad_condition_type_coefficient = 1
        else:
            res_dict["condition_type"] = None

        res_dict["current_profit_per_hour"] = current_profit_per_hour
        res_dict["profit_per_hour_delta"] = profit_per_hour_delta
        res_dict["level"] = level
        res_dict["is_available"] = is_available
        res_dict["is_expired"] = is_expired
        res_dict["cooldown_seconds"] = cooldown_seconds

        is_available_coefficient = 0 if bool(is_available) else 1
        is_expired_coefficient = 1 if bool(is_expired) else 0

        if cooldown_seconds is None:
            is_cooldown_seconds = 0
        else:
            is_cooldown_seconds = 0 if cooldown_seconds == 0 else 1

        try:
            res_dict["k"] = round(
                profit_per_hour_delta / price - bad_condition_type_coefficient - is_available_coefficient - is_expired_coefficient - is_cooldown_seconds,
                3)
        except ZeroDivisionError as zde:
            res_dict["k"] = round(
                0 - bad_condition_type_coefficient - is_available_coefficient - is_expired_coefficient - is_cooldown_seconds, 3)

        res.append(res_dict)

    res = sorted(res, key=lambda d: d['k'], reverse=True)
    top = sorted(res[:top_limit], key=lambda d: d['price'], reverse=False)

    print(f"Top {top_limit}: {[(i['id'], i['section'], i['price'], i['k']) for i in top]}")
    # with open('upgrades_for_buy.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=list(res[0].keys()))
    #     writer.writeheader()
    #     for r in res:
    #         writer.writerow(r)

    for r in top:
        # print(r)
        if r["price"] <= test_balance:
            if is_upgrade:
                # upgrade_id = top_3[0]["id"]
                upgrade_id = r["id"]

                payload_buy_upgrade = {
                    "upgradeId": upgrade_id,
                    "timestamp": datetime.now().timestamp()
                }
                response_buy_upgrade = requests.post(BUY_UPGRADE_URL, headers=HEADERS, json=payload_buy_upgrade)

                try:
                    check_change_level = \
                    [i["level"] for i in response_buy_upgrade.json()["upgradesForBuy"] if i["id"] == upgrade_id][0]

                    print(f"Upgrade success: {upgrade_id} {r['level']} -> {check_change_level}")
                except KeyError:
                    print(f"In updates. Can't get variables check_change_level")
                    print(response_buy_upgrade.json())
            break
        else:
            print("no")



upgrade(20000, top_limit=30, is_upgrade=True)
