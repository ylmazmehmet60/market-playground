import json
import csv
import requests

def getPairList():
    url = "https://api2.bybit.com/contract/v5/product/dynamic-symbol-list?filter=all"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        result = data['result']
        for item in result["LinearPerpetual"]:
            symbolName = item["symbolName"]

            print(symbolName)
           
        return 
    else:
        print("Error: Failed to retrieve data. Status code:", response.status_code)

getPairList()