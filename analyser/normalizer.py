from dotenv import load_dotenv
from pathlib import Path

import csv
import json
import os
import psycopg2
import pandas as pd

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

# df = pandas.read_json('ckbl-www.cardkingdom.com.json')
# print(df)

foundProducts = []
possibleBuys = []
notFoundPrices = []

connection = psycopg2.connect(user = os.getenv("MKM_TRADER_DB_USER"),
                            password = os.getenv("MKM_TRADER_DB_PASS"),
                            host = os.getenv("MKM_TRADER_DB_HOST"),
                            port = os.getenv("MKM_TRADER_DB_PORT"),
                            database = os.getenv("MKM_TRADER_DB_NAME"))

cursor = connection.cursor()

def normalizeBuylistCardkingdom(filePath, buylistName):
    data = json.load(open(filePath))
    df = pd.DataFrame(data['data'])
    print(df)

    data = []
    interimData = []
    batchSize = 1000
    count = 0

    for card in df.iterrows():
        setName = card[1]['edition']
        cardName = card[1]['name']
        priceCash = float(card[1]['price_buy'])
        priceCredit = priceCash * 1.3
        foil = card[1]['is_foil']
        maxQuantity= int(card[1]['qty_buying'])
        productId= int(card[1]['id'])
        specialArt= card[1]['variation']

        if maxQuantity == 0:
            continue

        productData = {
            'buylistName': 'Cardkingdom',
            'cardName': cardName,
            'setName': setName,
            'special_art': specialArt,
            'buylistCardId': productId,
            'buylistCredit': priceCredit,
            'buylistCash': priceCash,
            'maxQuantity': maxQuantity,
        }
        interimData.append(productData)
        count = count + 1

        if count >= batchSize:
            print('Processing %d' % productId)
            ids = ",".join([str(d['buylistCardId']) for d in interimData])
            sql = "select name, set_id, mcm_id, cardkingdom_id from mtgjson_cards where cardkingdom_id IN({ids});"
            result = cursor.execute(sql.format(ids = ids))
            rows = cursor.fetchall()

            for row in rows:
                mcmId = None

                if row and row[2] != None:
                    mcmId = int(row[2])

                productData = list(filter(lambda x: x['buylistCardId'] == row[3], interimData))
                if productData:
                    productData = productData[0]

                data.append({
                    'buylistName': 'Cardkingdom',
                    'cardName': productData['cardName'],
                    'setName': productData['setName'],
                    'special_art': productData['special_art'],
                    'buylistCardId': productData['buylistCardId'],
                    'mcmCardId': mcmId,
                    'buylistCredit': productData['buylistCredit'],
                    'buylistCash': productData['buylistCash'],
                    'maxQuantity': productData['maxQuantity'],
                })

            count = 0
            interimData = []

    return data


def getDataFrame(data):
    df = pd.DataFrame (data, columns = [
        'buylistName',
        'cardName',
        'setName',
        'special_art',
        'buylistCardId',
        'mcmCardId',
        'buylistCredit',
        'buylistCash',
        'maxQuantity',
        ]
    )
    print (df)
    return df


