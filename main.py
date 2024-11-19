import streamlit as st
from pmdarima.arima import auto_arima
import warnings
from Modules.connect_to_sql import MySqlConnection
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

warnings.simplefilter(action='ignore', category=FutureWarning)

import Modules.send_email as send_email

# Title and Description
st.title("Clothing Price Forecast Tool")
st.write("Adjust parameters to dynamically forecast clothing prices based on business metrics.")

x = st.text_input("Enter the number of days to forecast:", "365")
st.write("You entered: ", x)

# static definition
conversion_GWh2McM = 0.09999
split_country_list = ['Belgium','Germany','France','Hungary','Italy','Luxembourg','Poland','Portugal','United Kingdom','Netherlands']


def get_GMC_factors():
    # initiate sql connection
    sql_params = {
        "server_name": "ekofisk",
        "database_name": "GasMarketsCubeRelease",
        "table_name": "PipelineStringDump",
        "schema_name": "dbo",
    }
    cn = MySqlConnection(sql_params["server_name"], sql_params["database_name"])
    query_GMC = '''
    SELECT [Country]
      ,[Year]
      ,[Demand Sector Category]
      ,[Demand (Bcm)]
    FROM [GasMarketsCube].[dbo].[tblDemandConsumption]
    '''
    df_GMC_demand = cn.sql_to_df(query_GMC)
    df_GMC_demand.loc[df_GMC_demand['Demand Sector Category'] == 'Fuel gas', 'Demand Sector Category'] = 'Fuel Gas'
    df1 = df_GMC_demand.groupby(['Country', 'Year', 'Demand Sector Category'], as_index=False)['Demand (Bcm)'].sum()
    df2 = df_GMC_demand.groupby(['Country', 'Year'], as_index=False)['Demand (Bcm)'].sum()
    df_sector_share = df1.merge(df2, how='inner', on=['Country', 'Year'])
    df_sector_share['share'] = df_sector_share['Demand (Bcm)_x'] / df_sector_share['Demand (Bcm)_y']

    df3 = df_GMC_demand[~df_GMC_demand['Demand Sector Category'].isin(['Power'])].groupby(
        ['Country', 'Year', 'Demand Sector Category'], as_index=False)['Demand (Bcm)'].sum()
    df4 = df3.groupby(['Country', 'Year'], as_index=False)['Demand (Bcm)'].sum()
    df_sector_share_exclude_power = df3.merge(df4, how='inner', on=['Country', 'Year'])
    df_sector_share_exclude_power['share'] = df_sector_share_exclude_power['Demand (Bcm)_x'] / \
                                             df_sector_share_exclude_power['Demand (Bcm)_y']

    # share of "Others" in ST Dim
    df5 = df_GMC_demand[
        df_GMC_demand['Demand Sector Category'].isin(['Transportation', 'Losses', 'Fuel Gas', 'Others'])].groupby(
        ['Country', 'Year'], as_index=False)['Demand (Bcm)'].sum()
    df_sector_share_others = df5.merge(df2, how='inner', on=['Country', 'Year'])
    df_sector_share_others['share'] = df_sector_share_others['Demand (Bcm)_x'] / df_sector_share_others[
        'Demand (Bcm)_y']
    df_sector_share_others['share'] = 1 - df_sector_share_others['share'].copy()

    # Use the annual GMC power data to apply efficiency calculation
    df_GMC_power = df_GMC_demand[df_GMC_demand['Demand Sector Category'] == 'Power'].sort_values(by=['Country', 'Year'])

    return df_GMC_power,df_sector_share_exclude_power,df_sector_share,df_sector_share_others

df_GMC_power, df_sector_share_exclude_power, df_sector_share, df_sector_share_others = get_GMC_factors()

st.title(df_sector_share_others['Country'].unique())