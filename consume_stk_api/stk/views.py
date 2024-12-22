from django.contrib.auth.views import login_required
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

###########models####################
from .models import Account, MpesaRequest, MpesaPayment
from decimal import Decimal

##########endimportmodels############

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


@login_required(login_url='/auth/login')
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
        "CallBackURL": "https://codius.tech/lnmo-callback",
        "AccountReference": "TestPay",
        "TransactionDesc": "HelloTest",
        "Amount": amount
    }
    res = requests.post(endpoint, json=data, headers=headers)
    response = res.json()
    response_data = response
    context = { "response":response }

    if response_data.get("ResponseCode") == '0':
        MpesaRequest.objects.create(
            user=request.user,
            amount=amount,
            phone_number=phone,
            description=response_data["ResponseDescription"],
            merchant=response_data["MerchantRequestID"],
            status=response_data["CustomerMessage"],
        )
        context = {"response": response_data}
    else:
        MpesaRequest.objects.create(
            user=request.user,
            amount=amount,
            phone_number=phone,
            description=response_data.get("errorMessage", "Unknown error"),
            status="Failed",
        )

    return render(request, 'stkresult.html', context)   

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


    if result_code == 0:
        print(data)
        callback_metadata = items
        # Extracting the necessary data from the callback metadata
        amount = next(item['Value'] for item in callback_metadata if item['Name'] == 'Amount')
        print(amount)
        mpesa_receipt_number = next(item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber')
        print(mpesa_receipt_number)
        transaction_date = next(item['Value'] for item in callback_metadata if item['Name'] == 'TransactionDate')
        print(transaction_date)
        phone_number = next(item['Value'] for item in callback_metadata if item['Name'] == 'PhoneNumber')
        print(phone_number)

        # check for macthing merchant and save the amount to the user with the matching merchant

        # saved merchant
        user = MpesaRequest.objects.get(merchant=merchant_request_id).user
        print(user)
        # get the account associated with the user
        account = Account.objects.get(username=user)
        account.balance += Decimal(amount)
        account.save()

        d = json.loads(request.body.decode('utf-8'))
        body = d.get('Body', {})
        stk_callback = body.get('stkCallback', {})

        # Creating the MpesaPayment entry
        MpesaPayment.objects.create(
                amount=amount,
                description= result_desc,
                type="CustomerPayBillOnline",  # Assuming type from the initial request
                reference=mpesa_receipt_number,
                first_name="",  # If available, extract from another part of the callback or request
                middle_name="",
                last_name="",
                phone_number=phone_number,
                organization_balance=0.00,  # Assuming no balance provided in the callback
                is_finished=True,
                is_successful=True,
                trans_id=mpesa_receipt_number,
                order_id="",  # If available, extract from another part of the callback or request
                checkout_request_id= checkout_request_id,
                # merchant = data["Body"]["stkCallback"]["MerchantRequestID"]
                merchant = stk_callback.get('MerchantRequestID', '')
                )

        print("saved successfully in the database")

    else:
        # Handle failed transaction
        MpesaPayment.objects.create(
                amount=0.00,
                description= result_desc,
                type="CustomerPayBillOnline",
                reference="",
                first_name="",
                middle_name="",
                last_name="",
                phone_number="",
                organization_balance=0.00,
                is_finished=True,
                is_successful=False,
                trans_id="",
                order_id="",
                checkout_request_id= checkout_request_id,
                merchant = "",
                )
        print('error') 

    return HttpResponse(data)

####################### END STK ###############################
