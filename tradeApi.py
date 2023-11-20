import requests
import hashlib
import hmac
import time

api_key = 'XXXXXXXXXXXXXXXXXXXX'
secret_key = 'XXXXXXXXXXXXXXXXXXXXXX'

def trade(symbol, side, type, quantity):
    timestamp = int(time.time() * 1000)
    
    query_string = f'symbol={symbol}&side={side}&type={type}&quantity={quantity}&timestamp={timestamp}'

    # Create the signature
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Construct the request URL
    #url = f'https://api.binance.com/api/v3/order/test?{query_string}&signature={signature}'
    url = f'https://api.binance.com/api/v3/order?{query_string}&signature={signature}'

    # Set the request headers
    headers = {
        'X-MBX-APIKEY': api_key
    }

    # Send the request
    response = requests.post(url, headers=headers)

    # Process the response
    if response.status_code == 200:
        order_info = response.json()
        print(order_info)
        print("Order placed successfully.")
        print("Order ID:", order_info['orderId'])
        return "success"
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "fail"    


def tradeLimit(symbol, side, type, quantity, price):
    time_in_force = 'GTC'  # Specify the desired time in force value
    timestamp = int(time.time() * 1000)

    # Construct the query string
    query_string = f'symbol={symbol}&side={side}&type={type}&quantity={quantity}&price={price}&timeInForce={time_in_force}&timestamp={timestamp}'

    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()    

    # Construct the request URL
    url = f'https://api.binance.com/api/v3/order?{query_string}&signature={signature}'

    # Set the request headers
    headers = {
        'X-MBX-APIKEY': api_key
    }

    # Send the request
    response = requests.post(url, headers=headers)

    # Process the response
    if response.status_code == 200:
        order_info = response.json()
        print("Order placed successfully.")
        print("Order ID:", order_info['orderId'])
    else:
        print(f"Error: {response.status_code}, {response.text}")

'''
symbol = 'BNBUSDT'
side = 'SELL'
type = 'MARKET'
quantity = 1.0
trade(symbol, side, type, quantity)
'''

'''
symbol = 'BNBUSDT'
side = 'SELL'
type = 'LIMIT'
quantity = 1.0
price = 300.0
tradeLimit(symbol, side, type, quantity, price)
'''