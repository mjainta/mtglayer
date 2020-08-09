from dotenv import load_dotenv
from pathlib import Path
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

import csv
import os
import psycopg2
import pandas

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

df = pandas.read_json('mbbl-www.bazaarofmagic.eu.json')
print(df)

foundProducts = []
possibleBuys = []
notFoundPrices = []

mkm = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

f = open('result.csv', 'w')

with f:
    # try:
    connection = psycopg2.connect(user = os.getenv("MKM_TRADER_DB_USER"),
                                password = os.getenv("MKM_TRADER_DB_PASS"),
                                host = os.getenv("MKM_TRADER_DB_HOST"),
                                port = os.getenv("MKM_TRADER_DB_PORT"),
                                database = os.getenv("MKM_TRADER_DB_NAME"))

    cursor = connection.cursor()

    for card in df.iterrows():
        setAbbr = card[1]['set-name'].upper()
        cardName = card[1]['card-name'].replace("'", "''")
        extendedArt = card[1]['extended-art']
        euroAmount = card[1]['euro-amount'].replace(',', '.')
        foil = card[1]['foil']
        result = cursor.execute(f"select expansion_id, name_en from mkm_expansions where abbreviation = '{setAbbr}';")
        setRow = cursor.fetchone()
        print(setRow)

        if euroAmount == 'Bulk' or foil:
            continue
        else:
            euroAmount = float(euroAmount)

        if setRow:
            setId = setRow[0]

            cursor.execute(f"""
            select name,
                product_id,
                metacard_id
            from mkm_products
            where expansion_id = '{setId}'
                and name = '{cardName}'""")
            productRow = cursor.fetchone()

            if productRow:
                productName = productRow[0]
                productId = productRow[1]
                cursor.execute(f"""
                select last(german_pro_low, created_at),
                    last(low_price_min_ex, created_at),
                    last(foil_sell, created_at)
                from timeseries_priceguides
                where id_product = '{productId}';""")
                priceRow = cursor.fetchone()

                if priceRow:
                    foundProducts.append(productRow + priceRow)
                    priceToCompare = priceRow[0]

                    if foil and priceRow[2] is not None:
                        priceToCompare = priceRow[2]

                    if priceToCompare is not None and float(priceToCompare) < (euroAmount * 0.7):
                        possibleBuys.append(productRow + priceRow)

                        params = {
                            'idProduct': productId,
                            'maxResults': 10,
                            'minUserScore': 3,
                            'idLanguage': 1,
                            'minCondition': 'NM',
                            'minAvailable': 2,
                            'isFoil': foil,
                        }
                        response = mkm.market_place.articles(product=productId, params=params)

                        for article in response.json()['article']:
                            priceEur = article['priceEUR']
                            count = article['count']
                            row = [
                                productId,
                                productName,
                                euroAmount,
                                priceToCompare,
                                priceEur,
                                count,
                                article['seller']['username'],
                                article['seller']['address']['country'],
                                article['seller']['shipsFast'],
                            ]

                            writer = csv.writer(f)
                            writer.writerow(row)
                else:
                    notFoundPrices.append(productRow)


    # except (Exception, psycopg2.Error) as error :
    #     print ("Error while connecting to PostgreSQL", error)
    # finally:
    #     #closing database connection.
    #         if(connection):
    #             cursor.close()
    #             connection.close()
    #             print("PostgreSQL connection is closed")

print(foundProducts)
print(f'found %d products' % len(foundProducts))

print(possibleBuys)
print(f'found %d possibilities' % len(possibleBuys))

print(notFoundPrices)
print(f'not found %d prices' % len(notFoundPrices))