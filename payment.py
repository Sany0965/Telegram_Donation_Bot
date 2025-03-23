import time
import requests
from yoomoney import Quickpay, Client
from config import CRYPTOBOT_API_TOKEN, YOOMONEY_TOKEN, YOOMONEY_RECEIVER, CONVERSION_API_URL

def convert_rub_to_usd(rub_amount):
    try:
        response = requests.get(CONVERSION_API_URL)
        if response.ok:
            data = response.json()
            rate = data.get("rates", {}).get("USD")
            if rate:
                usd_amount = round(rub_amount * rate, 2)
                return usd_amount
    except Exception as e:
        print("Error converting RUB to USD:", e)
    return None

def get_cryptobot_pay_link(rub_amount):
    usd_amount = convert_rub_to_usd(rub_amount)
    if usd_amount is None:
        return None, None
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_API_TOKEN}
    data = {"asset": "USDT", "amount": usd_amount}
    try:
        response = requests.post('https://pay.crypt.bot/api/createInvoice', headers=headers, json=data)
        if response.ok:
            resp_json = response.json()
            result = resp_json.get("result")
            if result:
                return result.get("pay_url"), str(result.get("invoice_id"))
    except Exception as e:
        print("Error in Cryptobot API:", e)
    return None, None

def check_cryptobot_payment_status(invoice_id):
    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_API_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post('https://pay.crypt.bot/api/getInvoices', headers=headers, json={})
        if response.ok:
            resp_json = response.json()
            items = resp_json.get("result", {}).get("items", [])
            for item in items:
                if str(item.get("invoice_id")) == invoice_id:
                    return item.get("status")
    except Exception as e:
        print("Error checking Cryptobot payment status:", e)
    return None

def get_yoomoney_pay_link(rub_amount, chat_id):
    label = f"user_{chat_id}_{int(time.time())}"
    quickpay = Quickpay(
        receiver=YOOMONEY_RECEIVER,
        quickpay_form="shop",
        targets="Донат каналу",
        paymentType="SB",
        sum=rub_amount,
        label=label
    )
    return quickpay.base_url, label

def check_yoomoney_payment_status(label):
    try:
        client = Client(YOOMONEY_TOKEN)
        history = client.operation_history(label=label)
        for operation in history.operations:
            if operation.status == "success":
                return "success"
    except Exception as e:
        print("Error checking YooMoney payment status:", e)
    return None