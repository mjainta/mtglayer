from dotenv import load_dotenv
from pathlib import Path
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

import csv
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
    df = pd.read_json(filePath)
    print(df)

    data = []

    for card in df.iterrows():
        setName = card[1]['set_name'].upper()
        cardName = card[1]['card_name'].replace("'", "''")
        priceCash = card[1]['dollar_amount_cash'] + (card[1]['cent_amount_cash'] / 100)
        priceCredit = card[1]['dollar_amount_credit'] + (card[1]['cent_amount_credit'] / 100)
        foil = card[1]['foil']
        maxQuantity= int(card[1]['max_quantity'])
        productId= int(card[1]['product_id'])
        specialArt= int(card[1]['special_art'])

        result = cursor.execute(f"select name, set_id, mcm_id from mtgjson_cards where cardkingdom_id = '{productId}';")
        row = cursor.fetchone()
        mcmId = None

        if row and row[2] != None:
            mcmId = int(row[2])

        data.append({
            'buylistName': 'Cardkingdom',
            'cardName': cardName,
            'special_art': specialArt,
            'buylistCardId': productId,
            'mcmCardId': mcmId,
            'buylistCredit': priceCredit,
            'buylistCash': priceCash,
        })

    return data


def getDataFrame(data):
    df = pd.DataFrame (data, columns = ['buylistName', 'cardName', 'special_art', 'buylistCardId', 'mcmCardId', 'buylistCredit', 'buylistCash'])
    print (df)
    return df


