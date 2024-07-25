from hc_tap import send_request

from settings import HEADERS, CLAIM_DAILY_CIPHER_URL, HC_DAILY_CIPHER

payload_claim_daily_cipher = {
    "cipher": HC_DAILY_CIPHER
}

response_claim_daily_cipher = send_request(CLAIM_DAILY_CIPHER_URL, HEADERS, payload_claim_daily_cipher)

if response_claim_daily_cipher:
    print(response_claim_daily_cipher)