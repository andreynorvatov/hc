from dotenv import load_dotenv
import os

load_dotenv()

HC_DAILY_CIPHER = os.getenv("DAILY_CIPHER")
HC_TOKEN = os.getenv("TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36",
    "Authorization": HC_TOKEN
}

CLICKER_TAP_URL = "https://api.hamsterkombatgame.io/clicker/tap"
CLICKER_SYNC_URL = "https://api.hamsterkombatgame.io/clicker/sync"
CLAIM_DAILY_CIPHER_URL = "https://api.hamsterkombatgame.io/clicker/claim-daily-cipher"

UPGRADES_FOR_BUY_URL = "https://api.hamsterkombatgame.io/clicker/upgrades-for-buy"
BUY_UPGRADE_URL = "https://api.hamsterkombatgame.io/clicker/buy-upgrade"

ALL_CONDITION_TYPE = ['ByUpgrade', 'MoreReferralsCount', 'ReferralCount', 'SubscribeTelegramChannel', 'LinkWithoutCheck', 'LinksToUpgradeLevel']
BAD_CONDITION_TYPE = ['MoreReferralsCount', 'ReferralCount', 'SubscribeTelegramChannel', 'LinkWithoutCheck', 'LinksToUpgradeLevel']

BOOSTS_FOR_BUY_URL = "https://api.hamsterkombatgame.io/clicker/boosts-for-buy"
BUY_BOOSTS_URL = "https://api.hamsterkombatgame.io/clicker/buy-boost"
