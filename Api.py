import requests

API_KEY = "5015ef49-3bba-4a38-ab4a-aade26ac84eb"

url = "https://api.nowpayments.io/v1/invoice"
headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}

payload = {
    "price_amount": 10,
    "price_currency": "usd",
    "pay_currency": "usdt",
    "order_id": "123456",
    "order_description": "Test Payment",
    "ipn_callback_url": "https://your-webhook-url.com/webhook"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
