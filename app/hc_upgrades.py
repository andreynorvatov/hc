from datetime import datetime
import csv
from typing import Dict, List
import deprecation

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
    if upgrades_for_buy_response:
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
            except ZeroDivisionError:
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
    return None


def buy_upgrade_request(upgrade_id: str):
    payload = {
        "upgradeId": upgrade_id,
        "timestamp": int(datetime.now().timestamp())
    }
    response_tap = send_request(BUY_UPGRADE_URL, headers=HEADERS, payload=payload)
    if response_tap:
        return response_tap
    return None


@deprecation.deprecated(details="Function is deprecated. Use by_best_upgrade_v2 instead.")
def by_best_upgrade(price_limit: int = 1, upgrades_at_time_limit: int = 1):
    upgrades_data = upgrades_for_buy_request()
    if upgrades_data:
        upgrades_top = get_upgrades_top(upgrades_data, drop_null_and_below=True)
        if upgrades_top:
            # write_stat_csv_in_file("statistic/upgrades_for_buy.csv", data=upgrades_top, suffix=str(datetime.now().timestamp()))
            upgrades_top_length = len(upgrades_top)

            for current_upgrade in upgrades_top:
                if current_upgrade["price"] <= price_limit:
                    buy_upgrade_response = buy_upgrade_request(current_upgrade['id'])
                    if buy_upgrade_response:
                        new_level = [i["level"] for i in buy_upgrade_response["upgradesForBuy"] if i["id"] == current_upgrade['id']][0]
                        balance_coins = int(buy_upgrade_response["clickerUser"]["balanceCoins"])

                        logger.info(f"[HC Upgrade] Upgrade success! id: {current_upgrade['id']}, price: {current_upgrade['price']}/{balance_coins}, top: {current_upgrade['num']}, level up: {current_upgrade['level']} -> {new_level}")
                        upgrades_at_time_limit -= 1

                        if upgrades_at_time_limit == 0:
                            logger.info(f"[HC Upgrade] Upgrade top list ended!")
                            return balance_coins

                    upgrades_top_length -= 1

                    if upgrades_top_length == 0:
                        logger.info(f"[HC Upgrade] Upgrade NOT success! No coins on balance: {price_limit}")
                        return price_limit

        else:
            logger.error(f"[HC Upgrade] upgrades_for_buy_request fail! Upgrades_data: {upgrades_data}")
            return price_limit


def by_best_upgrade_v2(price_limit: int = 1, upgrades_at_time_limit: int = 1):
    upgrades_data = upgrades_for_buy_request()

    if not upgrades_data:
        logger.error(f"[HC Upgrade] upgrades_for_buy_request failed! No upgrades data. {upgrades_data}")
        return price_limit

    upgrades_top = get_upgrades_top(upgrades_data, drop_null_and_below=True)
    # write_stat_csv_in_file("statistic/upgrades_for_buy.csv", data=upgrades_top, suffix=str(datetime.now().timestamp()))
    if not upgrades_top:
        logger.error("[HC Upgrade] No eligible upgrades found.")
        return price_limit

    for current_upgrade in upgrades_top:
        if current_upgrade["price"] > price_limit:
            continue

        try:
            buy_upgrade_response = buy_upgrade_request(current_upgrade['id'])
            if not buy_upgrade_response:
                logger.warning(f"[HC Upgrade] Failed to buy upgrade for ID: {current_upgrade['id']}.")
                continue

            new_level = [i["level"] for i in buy_upgrade_response["upgradesForBuy"] if i["id"] == current_upgrade['id']][0]
            price_limit = int(buy_upgrade_response["clickerUser"]["balanceCoins"])

            logger.info(f"[HC Upgrade] Upgrade success! ID: {current_upgrade['id']}, Price: {current_upgrade['price']}/{price_limit}, Top: {current_upgrade['num']}, Level up: {current_upgrade['level']} -> {new_level}")
            upgrades_at_time_limit -= 1

            if upgrades_at_time_limit == 0:
                logger.info("[HC Upgrade] Upgrade top list ended!")
                return price_limit

        except Exception as e:
            logger.error(f"[HC Upgrade] Error buying upgrade for ID: {current_upgrade['id']}, Price: {current_upgrade['price']}/{price_limit}: {e}")

    logger.info(f"[HC Upgrade] Upgrade NOT success! No coins on balance: {price_limit}.")
    return price_limit


def by_upgrade_in_loop(balance_limit: int, loop_limit: int = 300):
    balance_limit = by_best_upgrade_v2(price_limit=balance_limit)


# by_upgrade_in_loop(14908)
by_best_upgrade_v2(price_limit=10_000_000)
