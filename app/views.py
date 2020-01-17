from paytm.payments import PaytmPaymentPage, VerifyPaytmResponse
from paytm.paymentstatus import get_paytm_payment_transactions_details
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from app.models import PaymentHolder

from paytm import Checksum

@csrf_exempt
def response(request):
    resp = VerifyPaytmResponse(request)
    payment_holder = PaymentHolder.objects.get(paytm_order_id=resp['paytm']['ORDERID'])
    if resp['verified']:
        payment_holder.paid = True
        payment_holder.payment_datetime = resp['paytm']['TXNDATE']
        payment_holder.save()
        data = get_paytm_payment_transactions_details(resp['paytm']['ORDERID'])
        return HttpResponse(f"""<h1>{data['STATUS']}</h1>
                                <h2>{data['RESPMSG']}</h2>""")
    else:
        payment_holder.paytm_order_id = None
        payment_holder.save()
        return HttpResponse("Verification Failed")
    return HttpResponse(status=200)


def payment(request):
    payment_holder = PaymentHolder.objects.get(payment_id=24)
    order_id = Checksum.__id_generator__()
    payment_holder.paytm_order_id = order_id
    payment_holder.save()
    bill_amount = str(payment_holder.amount_owed)
    cust_id = payment_holder.user.contact
    data_dict = {
                    'ORDER_ID':order_id,
                    'TXN_AMOUNT': bill_amount,
                    'CUST_ID': cust_id,
                }
    return PaytmPaymentPage(data_dict)