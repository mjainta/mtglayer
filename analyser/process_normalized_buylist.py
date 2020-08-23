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


def isArbitrageOption(germanProLow, buylistEur):
    if germanProLow is not None:
        if buylistEur <= 0.75:
            return False

        shippingFee = 0.30
        profitRatio = 0.7
        germanProLow = float(germanProLow)
        flatProfitThreshold = 5

        # The ratio is better for low value singles
        if germanProLow < (buylistEur * profitRatio - shippingFee):
            return True

        # The flat profit threshold is better for high value singles, since the ratio would be unexpectedly high
        if germanProLow < (buylistEur - flatProfitThreshold - shippingFee):
            return True

    else:
        return False

dfBuylists = pd.read_json('normalized_buylists.json', orient='index')
print(dfBuylists)

foundProducts = []
possibleBuys = []
notFoundPrices = []
validMcmIdCount = 0

# mkm = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

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

    interimData = []
    batchSize = 100
    count = 0

    for buylistEntry in dfBuylists.iterrows():
        mcmId = buylistEntry[1]['mcmCardId']
        buylistCash = float(buylistEntry[1]['buylistCash'])
        euroAmount = buylistCash * 0.85
        maxQuantity = int(buylistEntry[1]['maxQuantity'])
        setName = buylistEntry[1]['setName']

        if math.isnan(mcmId) or buylistEntry[1]['special_art']:
            continue
        else:
            interimData.append({
                'buylistName': buylistEntry[1]['buylistName'],
                'cardName': buylistEntry[1]['cardName'],
                'setName': setName,
                'mcmCardId': str(int(mcmId)),
                'euroAmount': euroAmount,
                'maxQuantity': maxQuantity,
            })
            count = count + 1

            if count >= batchSize:
                print('Processing %d' % mcmId)
                ids = list(d['mcmCardId'] for d in interimData)
                sql = """
                select last(german_pro_low, created_at),
                    last(low_price_min_ex, created_at),
                    id_product
                from timeseries_priceguides
                where id_product = ANY(%s)
                GROUP BY id_product;"""
                result = cursor.execute(sql, (ids,))
                rows = cursor.fetchall()

                for priceRow in rows:
                    validMcmIdCount = validMcmIdCount + 1
                    germanProLow = priceRow[0]
                    lowMinEx = priceRow[1]

                    buylistEntry = list(filter(lambda x: x['mcmCardId'] == priceRow[2], interimData))
                    if buylistEntry:
                        buylistEntry = buylistEntry[0]

                    foundProducts.append({
                        'buylistName': buylistEntry['buylistName'],
                        'cardName': buylistEntry['cardName'],
                        'setName': buylistEntry['setName'],
                        'mcmCardId': buylistEntry['mcmCardId'],
                        'euroAmount': buylistEntry['euroAmount'],
                        'maxQuantity': buylistEntry['maxQuantity'],
                        'germanProLow': germanProLow,
                        'lowMinEx': lowMinEx,
                    })

                    if isArbitrageOption(germanProLow, buylistEntry['euroAmount']):
                        possibleBuys.append({
                            'buylistName': buylistEntry['buylistName'],
                            'cardName': buylistEntry['cardName'],
                            'setName': buylistEntry['setName'],
                            'mcmCardId': buylistEntry['mcmCardId'],
                            'euroAmount': buylistEntry['euroAmount'],
                            'maxQuantity': maxQuantity,
                            'germanProLow': germanProLow,
                            'lowMinEx': lowMinEx,
                        })

                    # params = {
                    #     'idProduct': mcmId,
                    #     'start': 0,
                    #     'maxResults': 1,
                    #     'minUserScore': 3,
                    #     'idLanguage': 1,
                    #     'minCondition': 'NM',
                    #     'minAvailable': 2,
                    #     'isFoil': False,
                    # }
                    # response = mkm.market_place.articles(product=mcmId, params=params)

                    # for article in response.json()['article']:
                    #     priceEur = article['priceEUR']
                    #     count = article['count']

                    #     data.append({
                    #         'buylistName': buylistEntry[1]['buylistName'],
                    #         'cardName': buylistEntry[1]['cardName'],
                    #         'setName': setName,
                    #         'mcmCardId': buylistEntry[1]['mcmCardId'],
                    #         'euroAmount': euroAmount,
                    #         'maxQuantity': maxQuantity,
                    #         'germanProLow': germanProLow,
                    #         'lowMinEx': priceRow[1],
                    #         'seller': article['seller']['username'],
                    #         'country': article['seller']['address']['country'],
                    #         'shippingDays': article['seller']['shipsFast'],
                    #         'count': count,
                    #         'priceEurOffer': priceEur
                    #     })
                interimData = []
                count = 0


if(connection):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")

df = pd.DataFrame (possibleBuys, columns = [
    'buylistName',
    'cardName',
    'setName',
    'mcmCardId',
    'euroAmount',
    'maxQuantity',
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

# print(foundProducts)
print(f'found %d products' % len(foundProducts))

# print(possibleBuys)
print(f'found %d possibilities' % len(possibleBuys))

# print(notFoundPrices)
notFoundPrices = len(dfBuylists) - len(foundProducts)
print(f'not found %d prices' % notFoundPrices)
