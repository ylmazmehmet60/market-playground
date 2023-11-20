import requests
import hashlib
import hmac
import time
import tradeApi
import math

def request():
    api_key = 'XXXXXXXXXXXX'
    secret_key = 'XXXXXXXXXXXXX'
    timestamp = int(time.time() * 1000)

    # Create the query string
    query_string = f'timestamp={timestamp}'

    # Create the signature
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # Construct the request URL for account information
    account_url = f'https://api.binance.com/api/v3/account?{query_string}&signature={signature}'

    # Set the request headers
    headers = {
        'X-MBX-APIKEY': api_key
    }

    # Send the request to fetch account information
    return requests.get(account_url, headers=headers)

def checkBalance():
    response = request()
    # Process the account information response
    if response.status_code == 200:
        account_info = response.json()
        balances = account_info['balances']
        
        # Construct a list to store asset balances and their USD equivalents
        assets = []
        
        # Fetch the USDT equivalent for each asset
        for balance in balances:
            asset = balance['asset']
            free_balance = float(balance['free'])
            locked_balance = float(balance['locked'])
            total_balance = free_balance + locked_balance
            threshold = 10

            if total_balance > threshold and 'USDT' not in asset:
                # Construct the request URL for fetching USDT price
                price_url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT'
                
                # Send the request to fetch the price
                price_response = requests.get(price_url)
                
                # Process the price response
                if price_response.status_code == 200:
                    price_info = price_response.json()
                    usdt_price = float(price_info['price'])
                    
                    # Calculate the USD equivalent
                    usd_equivalent = total_balance * usdt_price
                    
                    # Append asset and USD equivalent to the list
                    assets.append((asset, usd_equivalent, free_balance))
            elif 'USDT' in asset:
                assets.append((asset, free_balance, free_balance))


        # Print the asset balances and their USD equivalents
        return assets

    else:
        print(f"Error: {response.status_code}, {response.text}")


def addTailCoinBeforeBuy(buy_tail_symbol):
    assets = checkBalance()
    if len(assets) == 0:
        exit()

    limit_per_trade = 11
    for asset, usd_equivalent, quantity in assets:
        if asset == buy_tail_symbol and usd_equivalent >= limit_per_trade:
            print(f"{asset}: USD Equivalent: {usd_equivalent}")
            break
        else:
            print("buying " + buy_tail_symbol + " $"+str(limit_per_trade))
            symbol = buy_tail_symbol + "USDT"
            tradeApi.trade(symbol, "BUY", 'MARKET', limit_per_trade)        
            break 

def quantityConverter(buy_head_symbol, buy_tail_symbol):
    assets = checkBalance()
    symbol =  buy_head_symbol + buy_tail_symbol
    for asset, usd_equivalent, quantity in assets:
        if asset == buy_tail_symbol:
            # Fetch the order book
            orderbook_url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit=2'
            response = requests.get(orderbook_url)
            orderbook = response.json()

            # Extract the current best ask price (lowest price someone is willing to sell JST for BTC)
            ask_price = float(orderbook['asks'][0][0])

            quantity = round(quantity, 1) 
            # Calculate the amount of JST you can buy
            amount = quantity / ask_price
            amount  = math.floor(round(amount, 1))
            # Print the result
            print(f"With {quantity} {buy_tail_symbol}, you can buy approximately {amount} {buy_head_symbol}")
            return amount

'''
buy_symbol_head = "ONE"
buy_symbol_tail = "USDT"
buy_head_tail_symbol = "ONEBTC"
addTailCoinBeforeBuy(buy_symbol_tail)
amount = quantityConverter(buy_symbol_head, buy_symbol_tail)

is_success = tradeApi.trade(buy_head_tail_symbol, "BUY", 'MARKET', amount)
if 'success' == is_success:
    tradeApi.trade(buy_head_tail_symbol, "SELL", 'LIMIT', amount)
'''