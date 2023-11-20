import pandas as pd
import numpy as np
import orderBook
import data
import api
import tradeApi

pd.set_option('display.float_format', '{:.8f}'.format)
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)

def getKeys(grouped_df):
    tail = grouped_df['Tail'].values
    head = grouped_df['Head'].values
    arr = np.append(tail, head)
    return list(set(arr))

def compare(grouped_df, source_parity):
    max_price = grouped_df['USD Price'].max()
    min_price = grouped_df['USD Price'].min()
    percentage = 100 - (100 * min_price / max_price )
    if not grouped_df.empty and percentage != 0 and percentage < 5 and max_price!=min_price and percentage > 0.2:  
        if "e" not in str(percentage) and "e" not in str(max_price) and "e" not in str(min_price):
            sorted_data = grouped_df.sort_values('USD Price', ascending=False)
            highest_value = sorted_data.iloc[0]['USD Price']
            lowest_value = sorted_data.iloc[-1]['USD Price']
            sell = sorted_data[sorted_data['USD Price'] == highest_value]
            sell_symbol_head = (sell['Head'].values)[0]
            sell_symbol_tail = (sell['Tail'].values)[0]
            sell_close = (sell['Close'].values)[0]
            sell_close = f'{sell_close:.10f}'

            buy = sorted_data[sorted_data['USD Price'] == lowest_value]
            buy_symbol_head = (buy['Head'].values)[0]
            buy_symbol_tail = (buy['Tail'].values)[0]
            buy_close = (buy['Close'].values)[0]
            buy_close = f'{buy_close:.10f}'

            return buy_symbol_head, buy_symbol_tail, sell_symbol_head, sell_symbol_tail, buy_close, sell_close, percentage

def sortList(arr):
    sorted_data = sorted(arr, key=lambda x: x[-1], reverse=True)
    for item in sorted_data:
       
        try:
            buy_symbol_head = item[0]
            buy_symbol_tail = item[1]
            sell_symbol_head = item[2]
            sell_symbol_tail = item[3]
            buy_close = item[4]
            sell_close = item[5]
            percentage = item[6]
            buy_symbol_full = buy_symbol_head + buy_symbol_tail
            sell_symbol_full = sell_symbol_head + sell_symbol_tail


            print(item)
            print("SUCCESS")
                
            
            if percentage > 0.1:
                print()
                '''
                buy_price = orderBook.order(buy_symbol_head, buy_symbol_tail)[0]
                sell_price = orderBook.order(sell_symbol_head, sell_symbol_tail)[0]
                
                if sell_price > buy_price:
                    print(item)
                    print(buy_price)
                    print(sell_price)
                    print("SUCCESS")
                ''' 
                #minv = min(buy_price, sell_price)
                #maxv = max(buy_price, sell_price)
                #percentage = 100 - (100 * float(maxv) / float(minv))

                '''
                api.addTailCoinBeforeBuy(buy_symbol_tail)
                amount = api.quantityConverter(buy_symbol_head, buy_symbol_tail)

                is_success = tradeApi.trade(buy_symbol_full, "BUY", 'MARKET', amount)
                if 'success' == is_success:
                    sell_price = float(sell_price)
                    #check sell price
                    #tradeApi.tradeLimit(sell_symbol_full, "SELL", 'LIMIT', amount, sell_price)
                
                break
                    '''
               
        except:
            print("exception occurred111")   
            break 
    


def process():
    csv_file = 'data.csv'

    df = pd.read_csv(csv_file)
    dropped_df = df.drop_duplicates(subset = ['Parity'], keep='last')

    # ANY PARITY TO USDT
    usd_price = dropped_df.where((dropped_df['Tail'] == "USDT")).dropna()
    filtered_df = dropped_df.loc[dropped_df['Head'].isin(['USDT'])].dropna()
    filtered_df[['Head', 'Tail']] = filtered_df[['Tail', 'Head']].values
    union_df = pd.concat([filtered_df, usd_price]).drop(['Parity', 'Tail'], axis=1).rename(columns={'Close': 'USD'})

    ## USDT BUST TUSD
    usd = dropped_df.loc[dropped_df['Tail'].isin(['USDT', 'BUSD', 'TUSD', 'USDC'])]
    usd.loc[:, 'USD'] = usd.loc[:, 'Close']
    usd.loc[:, 'USD Price'] = usd.loc[:, 'Close']

    cross_usd_parity = dropped_df.loc[~dropped_df['Tail'].isin(['USDT', 'BUSD', 'TUSD', 'USDC'])]
    left_merged = pd.merge(cross_usd_parity, union_df, left_on='Tail', right_on='Head', how='left').rename(columns={'Head_x': 'Head'}).drop(['Head_y'], axis=1).dropna(subset=['USD'])
    left_merged['USD Price'] = left_merged['Close'] * left_merged['USD']

    sub_df = pd.concat([usd, left_merged]).drop(['Parity'], axis=1)

    local_currency = pd.merge(filtered_df, sub_df, left_on='Head', right_on='Tail', how='left').drop(['Head_x', 'Tail_x', 'Close_x', 'Parity'], axis=1).rename(columns={'Head_y': 'Head', 'Tail_y': 'Tail', 'Close_y': 'Close'})
    local_currency['USD Price'] = local_currency['Close'] / local_currency['USD']

    not_include = sub_df.loc[~sub_df['Tail'].isin(filtered_df['Head'].values)]
    final_df = pd.concat([local_currency, not_include])

    keys = getKeys(final_df)
    arr = []
    for source_parity in keys:
        grouped_df_head = final_df.where((final_df['Head'] == source_parity)).dropna()
        grouped_df_tail = final_df.where((final_df['Tail'] == source_parity)).dropna()
        info_head = compare(grouped_df_head, source_parity)
        info_tail = compare(grouped_df_tail, source_parity)
        if info_head != None:
            arr.append(info_head)
        if info_tail != None:
            arr.append(info_tail)
    return arr

a = 0
while (100):
    if a % 10 == 0:
        print(a) 
    else:
        data.getSymbols()
        arr = process()
        sortList(arr)
        break
    a = a + 1