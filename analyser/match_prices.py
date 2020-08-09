from dotenv import load_dotenv
from pathlib import Path
import os
import psycopg2
import pandas

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

df = pandas.read_json('mbbl-www.bazaarofmagic.eu.json')
print(df)

foundProducts = []
possibleBuys = []

try:
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
        euroAmount = float(card[1]['euro-amount'].replace(',', '.'))
        foil = card[1]['foil']
        result = cursor.execute(f"select expansion_id, name_en from mkm_expansions where abbreviation = '{setAbbr}';")
        setRow = cursor.fetchone()
        print(setRow)

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
                productId = productRow[1]
                cursor.execute(f"""
                select last(german_pro_low, created_at),
                    last(low_price_min_ex, created_at),
                    last(foil_sell, created_at)
                from timeseries_priceguides
                where id_product = '{productId}';""")
                priceRow = cursor.fetchone()

                foundProducts.append(productRow + priceRow)

                if float(priceRow[0]) < euroAmount:
                    possibleBuys.append(productRow + priceRow)

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

print(foundProducts)
print(f'found %d products' % len(foundProducts))

print(possibleBuys)
print(f'found %d possibilities' % len(possibleBuys))
