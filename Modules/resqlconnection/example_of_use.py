import pandas as pd
from resqlconnection import resqlconnection
from datetime import datetime


# EXAMPLE 1
table_name="testtable"
schema_name="crawlertest"
server_name= "TOR"
db_name = "RECrawlers"

conn = resqlconnection(server_name, db_name)

input_list = [["This is a test",1,1.5,datetime.now(),5], ["also a test",3,1.5,datetime(2015,1,5),10]]

col = ["Str","num","float","Time","value"] # The names of the columns as they will be in the db, a crawl date column will automatically be added

dataframe = pd.DataFrame(input_list,columns=col)

conn.push_data(table_name, schema_name, dataframe, dataframe.columns, ["value"])

# The package also allows you to get information about tables from the database
conn.get_table_info(table_name, schema_name)

conn.preview_table(table_name, schema_name)





#pushing data
#input_list2 = ["String",2,2.9,None,2]
#conn.push_data(table_name,schema_name,input_list,col,["value"],False)                       #list in list
#conn.push_data(table_name,schema_name,input_list2,col,["value"],False)                      #list
            #dataframe

#conn.get_all_tables()

#example 2 of use:
"""
list = []
for i in range(1,3):
    list.append(["Norway",pd.Timestamp.date(pd.Timestamp(year=2021,month=1,day=i)),i])
for i in range(1,3):
    list.append(["Sweden",pd.Timestamp.date(pd.Timestamp(year=2021,month=1,day=i)),i+2])

conn.push_data("test","example",list,["Country","Date","Value"],["Value"],True)
 """


#example 3, only using sql_connection class
#connection, cursor, engine = resqlconnection.sql_connection.make_connection(server_name,db_name)
# use for whatever you need, e.g
#sql_query = f"SELECT * FROM {schema_name}.{table_name}"
#engine.execute(sql_query)


