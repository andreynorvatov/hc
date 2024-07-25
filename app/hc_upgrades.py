import requests
from datetime import datetime
import csv
from typing import Dict, List

from hc_tap import send_request
from settings import HEADERS, UPGRADES_FOR_BUY_URL, BAD_CONDITION_TYPE, BUY_UPGRADE_URL


def write_stat_csv_in_file(file_name, data: List[Dict], suffix: str = ""):
    file_name = file_name.replace(".", f"_{suffix}.")
    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def upgrades_for_buy_request():
    return send_request(UPGRADES_FOR_BUY_URL, HEADERS)


def get_upgrades_top(data: Dict, drop_null_and_below: bool = False):
    upgrades_for_buy_response = data["upgradesForBuy"]
    top_list = []
    for upgrades_for_buy in upgrades_for_buy_response:
        res_dict = {}

        res_dict["id"] = upgrades_for_buy["id"]
        res_dict["section"] = upgrades_for_buy["section"]
        res_dict["price"] = upgrades_for_buy["price"]
        res_dict["profit_per_hour"] = upgrades_for_buy["profitPerHour"]
        res_dict["condition"] = upgrades_for_buy["condition"]
        res_dict["current_profit_per_hour"] = upgrades_for_buy["currentProfitPerHour"]
        res_dict["profit_per_hour_delta"] = upgrades_for_buy["profitPerHourDelta"]
        res_dict["level"] = upgrades_for_buy["level"]
        res_dict["is_available"] = upgrades_for_buy["isAvailable"]
        res_dict["is_expired"] = upgrades_for_buy["isExpired"]
        res_dict["cooldown_seconds"] = 0 if upgrades_for_buy.get("cooldownSeconds") is None else upgrades_for_buy.get("cooldownSeconds")

        try:
            res_dict["base_k"] = round(upgrades_for_buy["profitPerHourDelta"] / upgrades_for_buy["price"], 5)
        except ZeroDivisionError as zde:
            res_dict["base_k"] = 0

        # is_available check
        res_dict["is_available_k"] = 0 if bool(upgrades_for_buy["isAvailable"]) else 1

        # is_expired check
        res_dict["is_expired_k"] = 1 if bool(upgrades_for_buy["isExpired"]) else 0

        # is_cooldown check
        res_dict["is_cooldown_k"] = 1 if res_dict["cooldown_seconds"] > 0 else 0

        # result_k calc
        res_dict["result_k"] = round(res_dict["base_k"] - res_dict["is_available_k"] - res_dict["is_expired_k"] - res_dict["is_cooldown_k"], 5)

        top_list.append(res_dict)

    top_list = sorted(top_list, key=lambda d: d['result_k'], reverse=True)

    if drop_null_and_below:
        top_list = [d for d in top_list if d.get("result_k") > 0]

    return top_list


def buy_upgrade_request(upgrade_id: str):
    payload = {
        "upgradeId": upgrade_id,
        "timestamp": datetime.now().timestamp()
    }
    response_tap = send_request(BUY_UPGRADE_URL, headers=HEADERS, payload=payload)

    return response_tap


upgrades_data = upgrades_for_buy_request()
if upgrades_data is not None:
    top = get_upgrades_top(upgrades_data, True)
    print(top[:3])

    # write_stat_csv_in_file("statistic/upgrades_for_buy.csv", data=top, suffix=str(datetime.now().timestamp()))
    # TODO LoopUpgrade get_top -> try_by in loop check price -> get_top -> ...
    # buy_upgrade_request()
    # try:
    #     check_change_level = \
    #         [i["level"] for i in response_buy_upgrade.json()["upgradesForBuy"] if i["id"] == upgrade_id][0]
    #
    #     print(f"Upgrade success: {upgrade_id} {r['level']} -> {check_change_level}")
    # except KeyError:
    #     print(f"In updates. Can't get variables check_change_level")
    #     print(response_buy_upgrade.json())


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

# upgrade(20000, top_limit=30, is_upgrade=True)
