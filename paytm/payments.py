from paytm import Checksum
import paytm_config
from django.http import HttpResponse
import json

MERCHANT_KEY = paytm_config.PAYTM_MERCHANT_KEY
MERCHANT_ID = paytm_config.PAYTM_MERCHANT_ID
COMPANY_NAME = paytm_config.PAYTM_MERCHANT_COMPANY_NAME
CALLBACK_URL = paytm_config.PAYTM_CALLBACK_URL
PAYTM_PAYMENT_GATEWAY_URL = paytm_config.PAYTM_PAYMENT_GATEWAY_URL
PAYTM_TRANSACTION_STATUS_URL = paytm_config.PAYTM_TRANSACTION_STATUS_URL
PAYTM_INDUSTRY_TYPE_ID = paytm_config.PAYTM_INDUSTRY_TYPE_ID
PAYTM_WEBSITE = paytm_config.PAYTM_WEBSITE
PAYTM_CHANNEL_ID = paytm_config.PAYTM_CHANNEL_ID
PAYTM_EMAIL = paytm_config.PAYTM_EMAIL
PAYTM_MOBILE = paytm_config.PAYTM_MOBILE

def GeneratePaymentPage(paytmParams):
    HTML = f"""
    <html>
    <head>
    <title>Merchant Check Out Page</title>
    </head>
    <center>
    <h1>Please do not refresh this page...</h1>
    </center>
    <form method="post" action="{PAYTM_PAYMENT_GATEWAY_URL}" name="paytm">
    <table border="1">
    <tbody>"""    
    for name,value in paytmParams.items():
        HTML += f"""<input type="hidden" name="{name}" value="{value}">"""
    HTML +="""
    </tbody>
    </table>
    <script type="text/javascript">
    document.paytm.submit();
    </script>
    </form>
    </html>"""
    return HttpResponse(HTML)
    # return HTML


def PaytmPaymentPage(paytmParams):
    paytmParams['MID'] = MERCHANT_ID
    paytmParams['WEBSITE'] = PAYTM_WEBSITE   
    paytmParams['INDUSTRY_TYPE_ID'] = PAYTM_INDUSTRY_TYPE_ID
    paytmParams['CHANNEL_ID'] = PAYTM_CHANNEL_ID
    paytmParams['MOBILE_NO'] = PAYTM_MOBILE
    paytmParams['EMAIL'] = PAYTM_EMAIL
    paytmParams['CALLBACK_URL'] = CALLBACK_URL
    paytmParams['CHECKSUMHASH'] = Checksum.generate_checksum(paytmParams, MERCHANT_KEY)
    return GeneratePaymentPage(paytmParams)


def VerifyPaytmResponse(response):
    response_dict = {}
    if response.method == "POST":
        data_dict = {}
        for key in response.POST:
            data_dict[key] = response.POST[key]
        verify = Checksum.verify_checksum(data_dict, MERCHANT_KEY, data_dict['CHECKSUMHASH'])
        if verify:
            response_dict['verified'] = True
            response_dict['paytm'] = data_dict
            return response_dict
        else:
            response_dict['verified'] = False
            return response_dict
    response_dict['verified'] = False
    return response_dict