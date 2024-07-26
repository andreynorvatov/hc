from datetime import datetime
import csv
from typing import Dict, List

from hc_tap import send_request
from settings import HEADERS, UPGRADES_FOR_BUY_URL, BAD_CONDITION_TYPE, BUY_UPGRADE_URL

from logger import logging

logger = logging.getLogger(__name__)

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
        res_dict = {
            "id": upgrades_for_buy["id"],
            "section": upgrades_for_buy["section"],
            "price": upgrades_for_buy["price"],
            "profit_per_hour": upgrades_for_buy["profitPerHour"],
            "condition": upgrades_for_buy["condition"],
            "current_profit_per_hour": upgrades_for_buy["currentProfitPerHour"],
            "profit_per_hour_delta": upgrades_for_buy["profitPerHourDelta"],
            "level": upgrades_for_buy["level"],
            "is_available": upgrades_for_buy["isAvailable"],
            "is_expired": upgrades_for_buy["isExpired"],
            "cooldown_seconds": 0 if upgrades_for_buy.get("cooldownSeconds") is None else upgrades_for_buy.get("cooldownSeconds")
        }

        try:
            res_dict["base_k"] = round(upgrades_for_buy["profitPerHourDelta"] / upgrades_for_buy["price"], 5)
        except ZeroDivisionError as zde:
            res_dict["base_k"] = 0

        # is_bad_condition_type check
        if upgrades_for_buy["condition"] is not None:
            res_dict["is_bad_condition_type_k"] = 1 if upgrades_for_buy["condition"]["_type"] in BAD_CONDITION_TYPE else 0
        else:
            res_dict["is_bad_condition_type_k"] = 0

        # is_available check
        res_dict["is_available_k"] = 0 if bool(upgrades_for_buy["isAvailable"]) else 1

        # is_expired check
        res_dict["is_expired_k"] = 1 if bool(upgrades_for_buy["isExpired"]) else 0

        # is_cooldown check
        res_dict["is_cooldown_k"] = 1 if res_dict["cooldown_seconds"] > 0 else 0

        # result_k calc
        res_dict["result_k"] = round(res_dict["base_k"] - res_dict["is_available_k"] - res_dict["is_expired_k"] - res_dict["is_cooldown_k"] - res_dict["is_bad_condition_type_k"], 5)

        top_list.append(res_dict)

    top_list = sorted(top_list, key=lambda d: d['result_k'], reverse=True)

    if drop_null_and_below:
        top_list = [d for d in top_list if d.get("result_k") > 0]

    top_list = [{**d, "num": n + 1} for n, d in enumerate(top_list)]
    return top_list


def buy_upgrade_request(upgrade_id: str):
    payload = {
        "upgradeId": upgrade_id,
        "timestamp": datetime.now().timestamp()
    }
    response_tap = send_request(BUY_UPGRADE_URL, headers=HEADERS, payload=payload)

    return response_tap


def by_best_upgrade(price_limit: int, upgrades_at_time_limit: int = 1):
    upgrades_data = upgrades_for_buy_request()
    if upgrades_data:
        upgrades_top = get_upgrades_top(upgrades_data, drop_null_and_below=True)

        # write_stat_csv_in_file("statistic/upgrades_for_buy.csv", data=upgrades_top, suffix=str(datetime.now().timestamp()))

        upgrades_top_length = len(upgrades_top)

        for current_upgrade in upgrades_top:
            if current_upgrade["price"] <= price_limit:
                buy_upgrade_response = buy_upgrade_request(current_upgrade['id'])

                new_level = [i["level"] for i in buy_upgrade_response["upgradesForBuy"] if i["id"] == current_upgrade['id']][0]
                balance_coins = int(buy_upgrade_response["clickerUser"]["balanceCoins"])
                # print(f"Upgrade success! id: {current_upgrade['id']}, price: {current_upgrade['price']}/{balance_coins}, top: {current_upgrade['num']}, level up: {current_upgrade['level']} -> {new_level}")
                logger.info(f"[HC Upgrade] Upgrade success! id: {current_upgrade['id']}, price: {current_upgrade['price']}/{balance_coins}, top: {current_upgrade['num']}, level up: {current_upgrade['level']} -> {new_level}")
                upgrades_at_time_limit -= 1
                if upgrades_at_time_limit == 0:
                    break

            upgrades_top_length -= 1
            if upgrades_top_length == 0:
                # print(f"Upgrade NOT success! No coins on balance: {price_limit}")
                logger.info(f"[HC Upgrade] Upgrade NOT success! No coins on balance: {price_limit}")
                return price_limit

        return balance_coins

def by_upgrade_in_loop(balance_limit: int, loop_limit: int = 300):

    balance_limit = by_best_upgrade(price_limit=balance_limit)


# by_upgrade_in_loop(14908)
