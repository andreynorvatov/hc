import time
from datetime import datetime
import random
# import configparser

from hc_tap import clicker_tap
from hc_boost import boost_full_available_taps
from hc_upgrades import by_best_upgrade_v2

from logger import logging


# TODO
# 1 Upgrade in loop
# 2 Log file rotation
# 3 Get params without restart
# 4 Add hc_daily_cipher in loop
# 5 Recalc loop time

def main():
    time_start = datetime.now()
    try:
        available_taps = 11000  # TODO to env
        start_response = clicker_tap(tap_count=1, available_taps=available_taps)

        balance_coins = start_response["balance_coins"] if start_response else 1
        available_taps = start_response["available_taps_response"] if start_response else 1
        max_taps = start_response["max_taps"] if start_response else 1
        logger.info(f'Init params. balance_coins: {balance_coins}, available_taps: {available_taps}, max_taps: {max_taps}')

        while True:
            # tap_count = 1  # TODO to env
            # sleep_time_sec = 2  # TODO to env
            tap_count = random.randint(4200, 4500) # TODO
            # sleep_time_sec = random.randint(1300, 1500) # TODO
            sleep_time_sec = random.randint(5 * 60, 5 * 60) # TODO

            do_boost_full_available_taps = True  # TODO to env
            do_upgrade_in_loop = True  # TODO to env

            # Send taps
            send_taps_response = clicker_tap(tap_count=tap_count, available_taps=available_taps)
            if send_taps_response:
                balance_coins = send_taps_response["balance_coins"]

                # Check and do boost
                boost_full_available_taps(do_boost_full_available_taps)

                # Check and do upgrades
                if do_upgrade_in_loop:
                    balance_coins = by_best_upgrade_v2(balance_coins)

            time.sleep(sleep_time_sec)

    except KeyboardInterrupt:
        logger.info(f'HC Loop finished. Time: {datetime.now() - time_start}')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('HC Loop started')
    main()
