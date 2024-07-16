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

