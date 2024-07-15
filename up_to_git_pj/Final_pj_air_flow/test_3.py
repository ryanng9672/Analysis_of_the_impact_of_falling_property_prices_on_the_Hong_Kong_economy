import pandas as pd
import time
import random
import httpx
import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, Float, MetaData, select

def centaline_scraping_transaction_data():
    url = "https://hk.centanet.com/findproperty/api/Transaction/Search"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
        'Lang': 'hk',
        'Content-Type': 'application/json; charset=utf-8'
    }

    payload = {
        "postType": "Rent",
        "day": "Day180",
        "sort": "InsOrRegDate",
        "order": "Descending",
        "size": 24,
        "offset": 0,
        "pageSource": "search"
    }

    all_result = []
    start_offset = 0
    end_offset = 9984

    p = start_offset
    max_retries = 5

    while p <= end_offset:
        time.sleep(random.random() + 0.5)
        payload['offset'] = p
        print(f"Fetching offset: {p}")

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()

                data = response.json().get('data', [])
                if len(data) == 0:
                    print("No data received.")
                    break

                for item in data:
                    ins_date_str = item.get("insDate")
                    ins_date = datetime.datetime.fromisoformat(ins_date_str.replace('Z', '+00:00')) if ins_date_str else None
                    building = {
                        "insDate": ins_date,
                        "address": item.get("address"),
                        "buildingName": item.get("buildingName"),
                        "whole_address": item.get("displayText", {}).get("addr", {}).get("line1"),
                        "price": item.get("transactionPrice"),
                        'districtName': item.get('districtName'),
                        'bigEstateName': item.get('bigEstateName'),
                        'estateName': item.get('estateName'),
                        'estateType': item.get('estateType'),
                        'terr': item.get('scope', {}).get('terr'),
                        'gArea': item.get('gArea'),
                        'gUnitPrice': item.get('gUnitPrice'),
                        'nArea': item.get('nArea'),
                        'nUnitPrice': item.get('nUnitPrice'),
                        'floor': item.get('xAxis'),
                        'flat': item.get('yAxis'),
                        'direction': item.get('direction'),
                        'bedroomCount': item.get('bedroomCount')
                    }
                    all_result.append(building)

                p += 24
        except httpx.RequestError as e:
            max_retries -= 1
            if max_retries > 0:
                print(f"Request error: {e}. Retrying... ({max_retries} retries left)")
                time.sleep(2)
            else:
                print(f"Request error: {e}. No more retries left.")
                break
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500:
                max_retries -= 1
                if max_retries > 0:
                    print(f"Server error: {e}. Retrying... ({max_retries} retries left)")
                    time.sleep(2)
                else:
                    print(f"Server error: {e}. No more retries left.")
                    break
            else:
                print(f"HTTP error: {e}.")
                break

    df = pd.DataFrame(all_result)
    df = df.drop_duplicates(subset=['address', 'buildingName', 'flat'])
    df['get_data_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df['insDate'] = df['insDate'].fillna(pd.NaT)
    df['insDate'] = df['insDate'].astype(object).where(df['insDate'].notnull(), None)

    # PGSQL path
    engine = create_engine('postgresql://postgres:1234@localhost:5432/centaline_pj')

    # make are sql table
    meta = MetaData()
    transaction_data_table = Table(
        'transaction_data', meta,
        Column('insDate', DateTime),
        Column('address', String),
        Column('buildingName', String),
        Column('whole_address', String),
        Column('price', Float),
        Column('districtName', String),
        Column('bigEstateName', String),
        Column('estateName', String),
        Column('estateType', String),
        Column('terr', String),
        Column('gArea', Float),
        Column('gUnitPrice', Float),
        Column('nArea', Float),
        Column('nUnitPrice', Float),
        Column('floor', String),
        Column('flat', String),
        Column('direction', String),
        Column('bedroomCount', Float),
        Column('get_data_time', DateTime)
    )
    meta.create_all(engine)
    
    df['bedroomCount'] = df['bedroomCount'].astype('Int64')

    # 由sql check back 有冇相同data
    existing_data = []
    with engine.connect() as conn:
        for _, row in df.iterrows():
            query = select([transaction_data_table]).where(
                (transaction_data_table.c.address == row['address']) &
                (transaction_data_table.c.buildingName == row['buildingName']) &
                (transaction_data_table.c.flat == row['flat'])
            )
            result = conn.execute(query).fetchone()
            if result:
                existing_data.append(row)

    # 如果從sql check有相同數據就drop再入db,防止重覆data
    df = df.drop(existing_data)

    # new data 放入 db
    with engine.connect() as conn:
        conn.execute(transaction_data_table.insert(), df.to_dict('records'))
        print("Data has been written to PostgreSQL.")

centaline_scraping_transaction_data()