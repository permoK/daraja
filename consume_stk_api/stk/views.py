from django.shortcuts import render

from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse

############# api libraries#############
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import base64

import uuid

########################################

########## global variable #######
base_url = 'https://codius.tech'
key = 'nAbuuqCD0dMH3uhXSO5A2yY7rd1HACYE'
secret = '3ZnvWnVqFqPgvUXF'
####################################

######################### ACCESS TOKEN ##################################
def get_access_token():
    consumer_key = key
    consumer_secret = secret
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']

########################## END ACCESS TOKEN #############################



######################### STK #################################
def stkpush(request):
    phone = request.POST.get('phone')
    amount = request.POST.get('amount')

    # if form.is_valid():
        

    return render(request, 'stk.html', )


def init_stk(request):

    if request.method == 'GET':
        phone = request.GET.get('phone')
        amount = request.GET.get('amount')
    else:
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
    
    print(phone, amount)

    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = get_access_token()
    headers = { "Authorization": f"Bearer {access_token}" }
    my_endpoint = base_url 
    Timestamp = datetime.now()
    times = Timestamp.strftime("%Y%m%d%H%M%S")
    password = "174379" + "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" + times
    datapass = base64.b64encode(password.encode('utf-8')).decode('utf-8')  # Decode to string
    # print(datapass)

    data = {
        "BusinessShortCode": "174379",
        "Password": datapass,
        "Timestamp": times,
        "TransactionType": "CustomerPayBillOnline", # for paybill - CustomerPayBillOnline
        "PartyA": phone,
        "PartyB": "174379",
        "PhoneNumber": phone, # fill with your phone number
        "CallBackURL": my_endpoint + "/lnmo-callback",
        "AccountReference": "TestPay",
        "TransactionDesc": "HelloTest",
        "Amount": amount
    }
    res = requests.post(endpoint, json=data, headers=headers)
    response = res.json()
    # print(response)
    # error = response["errorMessage"]
    # print("success")
    context = { "response":response }

    return render(request, 'stkresult.html', context)   
    # if response['ResponseCode'] == 0:
    #     return HttpResponse("success")
    # else:
    #     return HttpResponse(response['errorMessage'])

@csrf_exempt
def incoming(request):
    data = json.loads(request.body.decode('utf-8'))
    body = data.get('Body', {})
    stk_callback = body.get('stkCallback', {})
    merchant_request_id = stk_callback.get('MerchantRequestID', '')
    checkout_request_id = stk_callback.get('CheckoutRequestID', '')
    result_code = stk_callback.get('ResultCode', '')
    result_desc = stk_callback.get('ResultDesc', '')
    callback_metadata = stk_callback.get('CallbackMetadata', {})
    items = callback_metadata.get('Item', [])
    # data = json.loads(request.body)['Body']['stkCallback']

    # print(data['ResultCode'])
    print(result_code)
    print(data)


    return HttpResponse(data)

####################### END STK ###############################
