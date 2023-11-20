import requests


def get_symbol_orders(head, tail, limit=1):
    base_url = "https://api.binance.com"
    endpoint = "/api/v3/depth"
    params = {
        "symbol": head + tail,
        "limit": limit
    }

    try:
        response = requests.get(base_url + endpoint, params=params)
        response.raise_for_status()  # Raise an exception for unsuccessful responses
        data = response.json()
        sell_orders = data["asks"]  # Sell orders
        buy_orders = data["bids"]  # Buy orders
        return sell_orders, buy_orders
    except (requests.exceptions.HTTPError) as e:
        print("An error occurred:", e)
        return [], []

def order(head, tail):
    limit = 1
    sell_orders, buy_orders = get_symbol_orders(head, tail, limit)
    if tail != "USDT":

        try:
            operator = True
            usdt_price = get_symbol_orders(tail, "USDT", limit)[0][0][0]
        except:
            operator = False
            usdt_price = get_symbol_orders("USDT", tail, limit)[0][0][0]

        buy_orders = float(buy_orders[0][0])
        sell_orders = float(sell_orders[0][0])

        if operator == True:
            sell = float(usdt_price) * sell_orders
            sell = "{:.15f}".format(sell)

            buy = float(usdt_price) * buy_orders
            buy = "{:.15f}".format(buy)
        else:
            sell = sell_orders / float(usdt_price)
            sell = "{:.15f}".format(sell)

            buy = buy_orders / float(usdt_price)
            buy = "{:.15f}".format(buy)

        '''
        print(head, tail)
        print("usdt_price: " + usdt_price)
        print("buy: " + buy)
        print("sell: " + sell)
        '''

        return buy, sell
    else:
        return buy_orders[0][0], sell_orders[0][0]

'''
sell, buy = order("AMBBTC")
print(sell)
print(buy)
'''


