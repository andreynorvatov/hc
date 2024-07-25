import requests
from datetime import datetime
import time
import random
from typing import Dict

from hc_tap import clicker_tap, get_statistic, print_statistic
from hc_upgrades import upgrade
from hc_boost import boost_full_available_taps


def main():
    tap_count = 1
    available_taps = 6000
    sleep_time_sec = 2
    upgrade_skill = True
    do_boost_full_available_taps = True

    summary_tap_coins = 0
    summary_passive_coins = 0
    try:
        time_start = datetime.now()
        while True:
            # tap_count = random.randint(4200, 4500) # TODO
            # sleep_time_sec = random.randint(1300, 1500) # TODO
            current_timestamp = datetime.now()

            statistic = clicker_tap(tap_count, available_taps)


            # statistic = get_statistic(response_clicker_tap)

            summary_tap_coins += tap_count
            # summary_passive_coins += statistic.get('last_passive_earn')

            # print_statistic(current_timestamp, tap_count, available_taps, statistic)

            upgrade(statistic.get('balance_coins'), top_limit=30, is_upgrade=upgrade_skill)
            boost_full_available_taps(do_boost_full_available_taps)

            time.sleep(sleep_time_sec)

    except KeyboardInterrupt:
        print(
            f"Process finished. Tap coins: {summary_tap_coins}, Passive coins: {summary_passive_coins}, Coins: {summary_tap_coins + summary_passive_coins}, time: {datetime.now() - time_start}")


if __name__ == '__main__':
    main()
