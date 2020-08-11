from dotenv import load_dotenv
from pathlib import Path
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

import csv
import os
import psycopg2
import pandas as pd
import math

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

df = pd.read_json('normalized_buylists.json', orient='index')
print(df)

foundProducts = []
possibleBuys = []
notFoundPrices = []
validMcmIdCount = 0

mkm = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

f = open('result.csv', 'w')

data = []

with f:
    # try:
    connection = psycopg2.connect(user = os.getenv("MKM_TRADER_DB_USER"),
                                password = os.getenv("MKM_TRADER_DB_PASS"),
                                host = os.getenv("MKM_TRADER_DB_HOST"),
                                port = os.getenv("MKM_TRADER_DB_PORT"),
                                database = os.getenv("MKM_TRADER_DB_NAME"))

    cursor = connection.cursor()

    for buylistEntry in df.iterrows():
        print(buylistEntry)
        mcmId = buylistEntry[1]['mcmCardId']
        buylistCash = float(buylistEntry[1]['buylistCash'])
        euroAmount = buylistCash * 0.85

        if math.isnan(mcmId):
            continue
        else:
            mcmId = int(mcmId)
            validMcmIdCount = validMcmIdCount + 1

            cursor.execute(f"""
            select last(german_pro_low, created_at),
                last(low_price_min_ex, created_at)
            from timeseries_priceguides
            where id_product = '{mcmId}';""")
            priceRow = cursor.fetchone()

            if priceRow:
                germanProLow = priceRow[0]

                foundProducts.append({
                    'buylistName': buylistEntry[1]['buylistName'],
                    'cardName': buylistEntry[1]['cardName'],
                    'mcmCardId': buylistEntry[1]['mcmCardId'],
                    'euroAmount': euroAmount,
                    'germanProLow': germanProLow,
                    'lowMinEx': priceRow[1],
                })

                if germanProLow is not None and float(germanProLow) < (euroAmount * 0.7):
                    possibleBuys.append({
                        'buylistName': buylistEntry[1]['buylistName'],
                        'cardName': buylistEntry[1]['cardName'],
                        'mcmCardId': buylistEntry[1]['mcmCardId'],
                        'euroAmount': euroAmount,
                        'germanProLow': germanProLow,
                        'lowMinEx': priceRow[1],
                    })

                    params = {
                        'idProduct': mcmId,
                        'start': 0,
                        'maxResults': 5,
                        'minUserScore': 3,
                        'idLanguage': 1,
                        'minCondition': 'NM',
                        'minAvailable': 2,
                        'isFoil': False,
                    }
                    response = mkm.market_place.articles(product=mcmId, params=params)

                    for article in response.json()['article']:
                        priceEur = article['priceEUR']
                        count = article['count']

                        data.append({
                            'buylistName': buylistEntry[1]['buylistName'],
                            'cardName': buylistEntry[1]['cardName'],
                            'mcmCardId': buylistEntry[1]['mcmCardId'],
                            'euroAmount': euroAmount,
                            'germanProLow': germanProLow,
                            'lowMinEx': priceRow[1],
                            'seller': article['seller']['username'],
                            'country': article['seller']['address']['country'],
                            'shippingDays': article['seller']['shipsFast'],
                            'count': count,
                            'priceEurOffer': priceEur
                        })
            else:
                notFoundPrices.append({
                    'buylistName': buylistEntry[1]['buylistName'],
                    'cardName': buylistEntry[1]['cardName'],
                    'mcmCardId': buylistEntry[1]['mcmCardId'],
                    'euroAmount': euroAmount,
                })


if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")

df = pd.DataFrame (data, columns = [
    'buylistName',
    'cardName',
    'mcmCardId',
    'euroAmount',
    'germanProLow',
    'lowMinEx',
    'seller',
    'country',
    'shippingDays',
    'count',
    'priceEurOffer',
    ]
)
print (df)
df.to_json('buylists_results.json', orient='index')

print(foundProducts)
print(f'found %d products' % len(foundProducts))

print(possibleBuys)
print(f'found %d possibilities' % len(possibleBuys))

print(notFoundPrices)
print(f'not found %d prices' % len(notFoundPrices))
