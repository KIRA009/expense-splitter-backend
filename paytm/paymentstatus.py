import requests
import json
from paytm import Checksum
import paytm_config

MERCHANT_ID = paytm_config.PAYTM_MERCHANT_ID
URL = paytm_config.PAYTM_TRANSACTION_STATUS_URL
MERCHANT_KEY = paytm_config.PAYTM_MERCHANT_KEY


def get_paytm_payment_transactions_details(paytm_order_id):
	paytmParams = dict()
	paytmParams["MID"] = MERCHANT_ID
	paytmParams["ORDERID"] = paytm_order_id 
	checksum = Checksum.generate_checksum(paytmParams, MERCHANT_KEY)
	paytmParams["CHECKSUMHASH"] = checksum
	post_data = json.dumps(paytmParams)
	response = requests.post(URL, data = post_data, headers = {"Content-type": "application/json"}).json()

	return response	