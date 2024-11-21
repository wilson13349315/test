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


# static definition
conversion_GWh2McM = 0.09999
split_country_list = ['Belgium','Germany','France','Hungary','Italy','Luxembourg','Poland','Portugal','United Kingdom','Netherlands']

def get_European_balance():
    sql_params = {
        "server_name": "ekofisk",
        "database_name": "LNGTrade",
        "table_name": "tblEuropeanMonthlyBalance",
        "schema_name": "LNGG",
    }

    sql_obj = MySqlConnection(sql_params["server_name"], sql_params["database_name"])

    query_europe_production = '''
    SELECT  [Date]
      ,[Storage]
      ,[Storage_FC_normal]
      ,[Net_injection_normal]
      ,[EU27+UK]
      ,[Demand]
      ,[Algeria]
      ,[Azerbaijan]
      ,[Libya]
      ,[Russia]
      ,[Turkey]
      ,[NOR Pipe]
      ,[LNG]
      ,[Balance]
      ,[Timestamp]
  FROM [LNGTrade].[LNGG].[tblEuropeanMonthlyBalance]
  where timestamp = (select max(timestamp)   FROM [LNGTrade].[LNGG].[tblEuropeanMonthlyBalance]) 

    '''

    df = sql_obj.sql_to_df(query_europe_production)
    df['Date'] = pd.to_datetime(df['Date'])

    return df

def get_European_demand_by_sector():
    sql_params = {
        "server_name": "ekofisk",
        "database_name": "LNGTrade",
        "table_name": "tblEuropeanMonthlyBalance",
        "schema_name": "LNGG",
    }

    sql_obj = MySqlConnection(sql_params["server_name"], sql_params["database_name"])

    query = '''
    SELECT [Date]
      ,[Country]
      ,[Demand Sector Category]
      ,[Value]
      ,[Model_type]
      ,[Source]
    FROM [LNGTrade].[dbo].[ZL_EuropeDemandMonthly]
    where [RebalancedOrder] =1 
    and timestamp = (select max(timestamp) FROM [LNGTrade].[dbo].[ZL_EuropeDemandMonthly]) 
    order by timestamp desc
      '''

    df = sql_obj.sql_to_df(query)
    df['Date'] = pd.to_datetime(df['Date'])

    return df


df_balance = get_European_balance()
df_balance = df_balance.drop(['Timestamp'], axis=1)
df_balance.to_csv('df_balance.csv', index=False)


