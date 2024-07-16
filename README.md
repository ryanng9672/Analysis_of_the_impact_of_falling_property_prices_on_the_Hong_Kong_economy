# Analysis_of_the_impact_of_falling_property_prices_on_the_Hong_Kong_economy

# Table of Content
* [Project_Introduction](#Project_Introduction)
* [Analysis_Purpose](#Analysis_Purpose)
* [Python](#Python)
* [WebsiteRelated](#WebsiteRelated)


# Project_Introduction
 **Overview**

**This project consists of two main components:**

**Analysis of Hong Kong Property Price Trends**
![螢幕擷取畫面 2024-07-16 174328](https://github.com/user-attachments/assets/cc3e8819-1c0d-4536-8560-5a29b9a3160d)


File: fn_pj_house.ipynb

Title: Analysis of the Impact of Falling Property Prices on the Hong Kong Economy

**Automated Real Estate Data Collection and Price Prediction(Data Pipeline)**
![螢幕擷取畫面 2024-07-16 174038](https://github.com/user-attachments/assets/72b3127d-efca-46d6-ad3e-86c82937a3e5)

File: house730.ipynb
This component involves:
Automated data collection from the house_730 real estate transaction website using Airflow
Extraction of current rental listings and successful rental transactions
Storage of collected data in PostgreSQL
Prediction of actual transaction prices for current rental listings based on historical successful rental data
The Airflow-related content is stored in a separate Airflow folder.

# Analysis_Purpose

**Impact of Hong Kong Property Price Decline**

**The analysis results and detailed information are stored in PowerPoint and Word documents.**

[PPT Link](https://github.com/ryanng9672/Analysis_of_the_impact_of_falling_property_prices_on_the_Hong_Kong_economy/blob/master/up_to_git_pj/Final%20Project_ppt.pptx)

[Word Link](https://github.com/ryanng9672/Analysis_of_the_impact_of_falling_property_prices_on_the_Hong_Kong_economy/blob/master/up_to_git_pj/Final%20Project_word.docx)

[data set link](https://github.com/ryanng9672/Analysis_of_the_impact_of_falling_property_prices_on_the_Hong_Kong_economy/blob/master/up_to_git_pj/Final_Project_data.zip)

Main objective: To understand the impact of falling property prices on Hong Kong's economy.

**House730 Rental Market Analysis**

![螢幕擷取畫面 2024-07-16 173642](https://github.com/user-attachments/assets/6747696c-cdbf-4d72-bc40-44fede5b5a28)


Main objective: To determine the actual rental transaction prices in the market.

# Python
-爬蟲(web scraping) << in houesing730
```shell
while True:
    print(f"正在get第 {payload['pageIndex']} 頁的租盤data...")
    #time.sleep(1) 
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if data['code'] != 0 or 'data' not in data['result'] or len(data['result']['data']) == 0:
        print(f"第 {payload['pageIndex']} 頁nodata,end in the post") #https://www.house730.com/rent/t1g180/ 只可以去到180頁
        break
```
![螢幕擷取畫面 2024-07-16 181029](https://github.com/user-attachments/assets/138e1940-bdc5-46d4-a53d-f11a3b5641a1)



-視覺化(data-visualization)<<< in Analysis of the Impact of Falling Property Prices on the Hong Kong Economy

![螢幕擷取畫面 2024-07-14 233400](https://github.com/user-attachments/assets/b9273886-77a0-4cef-85d5-f7b596d58157)

```shell
import plotly.graph_objects as go
from datetime import datetime

fig_old = px.line(centaline_data_housing_old, x='Date', y='CCL_housing')

events = [
    {'year': 1997, 'event': '1997年亞洲金融危機'},
    {'year': 2003, 'event': '2003年SARS疫情'},
    {'year': 2008, 'event': '2008年全球金融危機'},
    {'year': 2009, 'event': '2009-2013年量化寬鬆和低利率環境', 'end_year': 2013},
    {'year': 2014, 'event': '2014-2015年"佔中運動"', 'end_year': 2015},
    {'year': 2016, 'event': '2016-2018年房地產市場調控政策(「房住不炒」)', 'end_year': 2018},
    {'year': 2019, 'event': '2019年社會事件(民運事件)'},
    {'year': 2020, 'event': '2020年至新冠疫情+國安法'}
]

centaline_data_housing_old['Date'] = pd.to_datetime(centaline_data_housing_old['Date'])

for event in events:
    event_date = datetime(event['year'], 1, 1)
    fig_old.add_shape(type="line",
                  x0=event_date, y0=0, x1=event_date, y1=1,
                  xref="x", yref="paper",
                  line=dict(color="gray", width=1, dash="dash"))
    
    if 'end_year' in event:
        end_event_date = datetime(event['end_year'], 12, 31)
        fig_old.add_shape(type="line",
                      x0=end_event_date, y0=0, x1=end_event_date, y1=1,
                      xref="x", yref="paper",
                      line=dict(color="gray", width=1, dash="dash"))
    
    available_dates = centaline_data_housing_old[centaline_data_housing_old['Date'] >= event_date]['Date']
    if len(available_dates) > 0:
        nearest_date = min(available_dates)
        event_ccl = centaline_data_housing_old[centaline_data_housing_old['Date'] == nearest_date]['CCL_housing'].values[0]
        fig_old.add_trace(go.Scatter(x=[event_date], y=[event_ccl], mode='markers', 
                                     marker=dict(size=15, color='red'),
                                     hovertext=event['event'], showlegend=False))

fig_old.update_xaxes(range=['1997-01-01', centaline_data_housing_old['Date'].max()])
fig_old.update_xaxes(
    dtick="M12",  
    tickformat="%Y-%m"  
)

fig_old.update_layout(showlegend=False)

fig_old.show()
```

-PGSQL(keep_data)

![螢幕擷取畫面 2024-07-16 181534](https://github.com/user-attachments/assets/be15d941-a43b-4a73-b28b-0c727b137923)


# WebsiteRelated
https://www.house730.com/rent/g100/

https://data.gov.hk/tc-data/dataset/hk-pland-pland1-land-utilization-in-hong-kong-statistics/resource/ef09b603-bcc5-4a23-8ae4-201cf5cb988e

https://www.censtatd.gov.hk/tc/


https://www.landsd.gov.hk/tc/index.html




