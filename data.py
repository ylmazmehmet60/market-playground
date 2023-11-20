import json
import csv
import requests

def getPairList():
    url = "https://api.binance.com/api/v1/exchangeInfo"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        parity_names = []
        stopped_symbols = []
        for item in data["symbols"]:
            b = item["baseAsset"]
            q = item["quoteAsset"]
            status = item['status']
            symbol = item['symbol']
            order_types = item['orderTypes']
            if 'TRADING' in status and (('LIMIT' and 'MARKET') in order_types):
                parity_names.append(b)
                parity_names.append(q)
            else:
                stopped_symbols.append(symbol)    
        return sorted(list(set(stopped_symbols)), reverse=True), sorted(list(set(parity_names)), reverse=True)
    else:
        print("Error: Failed to retrieve data. Status code:", response.status_code)

stopped_symbols, pair_list = getPairList()

if len(pair_list) == 0:
    print("Pair List is empty. Exit.")
    exit()

def splitPair(pair):
    for elem in pair_list:
        if pair.startswith(elem):
            tail = pair.replace(elem, "")
            head = pair[:-len(tail)]
            return head, tail
        
csv_file = 'data.csv'
header = ['Parity', 'Head', 'Tail', 'Close']
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)

def getSymbols():
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        merge = []
        for item in data:
            symbol = item["symbol"]
            if symbol not in stopped_symbols:
                price = item["price"]
                head, tail = splitPair(symbol)
                new_element = {'parity': symbol, 'head': head, 'tail': tail, 'close': price}
                merge.append(new_element)

        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            for item in merge:
                writer.writerow([item['parity'], item['head'], item['tail'], item['close']])     
    else:
        print("Error: Failed to retrieve data. Status code:", response.status_code)

#getSymbols()
