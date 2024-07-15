import pandas as pd
import time
import random
import httpx
import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, Float, MetaData

url = "https://hk.centanet.com/findproperty/api/Post/Search"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Lang': 'hk',
    'Content-Type': 'application/json; charset=utf-8'
}

payload = {
    "postType": "Rent",
    "sort": "Ranking",
    "order": "Ascending",
    "size": 24,
    "displayTextStyle": "WebResultList",
    "mtrDuration":"600",
    "offset": 0,
    "pageSource": "search"
}

all_result = []

start_offset = 0  # start offset值
end_offset = 4536    # end offset值

p = start_offset
max_retries = 5  # 最大重試次數,因為有SSL,所以TRY 5次入去個WEB GET

while p <= end_offset:
    time.sleep(random.random() + 0.5)
    payload['offset'] = p
    print(f"Fetching offset: {p}")

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()  # check HTTP 有冇錯

            if len(response.json().get('data', [])) == 0:
                print("No data received.")
                break

            for item in response.json().get("data", []):
                nearby_facilities = item.get("labelGroup", {}).get("nearbyFacilities", {})
                mtr_labels = nearby_facilities.get("mtrLabels", [])
                mtr_walk_minutes = mtr_labels[0].get("walkMinutes") if mtr_labels else None

                gMap = item.get("gMap", {})
                lat = gMap.get("lat")
                lng = gMap.get("lng")

                scope = item.get("scope", {})
                db = scope.get("db")
                webScope = scope.get("webScope")

                publish_date_str = item.get("publishDate")
                publish_date = datetime.datetime.fromisoformat(publish_date_str) if publish_date_str else None

                building = {
                    "publishDate": publish_date,
                    "address": item.get("address"),
                    'bigEstateName':item.get('bigEstateName'),
                    "estateName": item.get("estateName"),
                    "buildingName": item.get("buildingName"),
                    'mtr_walkMinutes': mtr_walk_minutes,
                    'buildingAge': item.get('buildingAge'),
                    'lat': lat,
                    'lng': lng,
                    'district': db,
                    'sub_district': webScope,
                }
                all_result.append(building)

            p += 24
    except httpx.RequestError as e:
        max_retries -= 1
        if max_retries > 0:
            print(f"Request error: {e}. Retrying... ({max_retries} retries left)")
            time.sleep(2)  # time.sleep 2秒先行到,不要DEL
        else:
            print(f"Request error: {e}. No more retries left.")
            break

df = pd.DataFrame(all_result)
df = df.drop_duplicates(subset=['address','buildingName','estateName','bigEstateName'])
df['get_data_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


df['publishDate'] = df['publishDate'].fillna(pd.NaT)  
df['publishDate'] = df['publishDate'].astype(object).where(df['publishDate'].notnull(), None) 

# PostgreSQL數據庫連接
engine = create_engine('postgresql://postgres:1234@localhost:5432/centaline_pj')

# make are sql table
meta = MetaData()
rent_data_table = Table(
    'rent_data', meta,
    Column('publishDate', DateTime),
    Column('address', String),
    Column('bigEstateName',String),
    Column('estateName', String),
    Column('buildingName', String),
    Column('mtr_walkMinutes', String),
    Column('buildingAge', Float),
    Column('lat', Float),
    Column('lng', Float),
    Column('district', String),
    Column('sub_district', String),
    Column('get_data_time', DateTime)
)
meta.create_all(engine)

# 將data插入table
with engine.connect() as conn:
    conn.execute(rent_data_table.insert(), df.to_dict('records'))
    print("Data has been written to PostgreSQL.")