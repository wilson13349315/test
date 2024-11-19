import math
from email.mime.text import MIMEText

import numpy as np
import pandas
import pandas as pd
import sqlalchemy as sal

"""
Created 05.07.2021

:Author: Andreas Rystad
"""


class Method:
    max_varchar = 255

    def __init__(self, varchar_size):
        """:param max_varchar_size size of maximum length of varchar"""
        self.set_max_varchar(varchar_size)

    def get_table_columns(self, table_name, schema_name, sql_conn):
        """Method for returning table columns
        :parameter table_name name of table
        :parameter schema_name name of schema
        :parameter sql_conn instance of SQLConnection class

        :returns Dataframe with columns in SQL table
        """
        columns = sql_conn.read_to_df(
            "SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
            + f"WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA ='{schema_name}'",
        )
        return columns

    def get_table_info(self, table_name, schema_name, sql_conn):
        """Prints table information for a given table name with columns, datatypes and nr of rows
        :parameter table_name name of table
        :parameter schema_name name of schema
        :parameter sql_conn instance of SQLConnection class

        :returns Dataframe with columns and types in SQL table
        """
        columns = self.get_table_columns(table_name, schema_name, sql_conn)
        print(self.format_string(table_name + "\n" + str(columns)))
        number_of_rows = sql_conn.read_to_df(
            f"Select Count(*) FROM {schema_name}.{table_name}",
        ).values[
            0
        ][0]
        print(f"number of rows in {table_name}: {number_of_rows}")
        return columns

    def get_all_tables_info(self, sql_conn):
        """A method returning and printing all tables in database
        :parameter sql_conn instance of SQLConnection class
        :returns DF with all tables in database
        """
        val = sql_conn.read_to_df(
            "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES",
        )
        print(self.format_string(str(val)))
        return val

    def preview_table(self, table_name, schema_name, nr_of_lines, sql_conn):
        """Preview method that prints first few rows of a table for users
        :parameter table_name name of table
        :parameter schema_name name of schema
        :parameter nr_of_lines number of lines to show
        :parameter sql_conn instance of SQLConnection class
        """
        df = sql_conn.read_to_df("SELECT * FROM " + schema_name + "." + table_name)
        print(self.format_string(table_name + "\n" + str(df.head(nr_of_lines))))
        return df.head(nr_of_lines)

    def push_data(
        self,
        table_name,
        schema_name,
        input_data,
        column_name_list,
        value_columns,
        crawldate_column,
        replace,
        ignore_duplicates_check,
        sql_conn,
        recipients,
    ):
        """Method for pushing data to the desired table in database
        :param crawldate_column:
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param input_data: Data to be pushed
        :param column_name_list: Used for giving correct name to data. Only required when input_data is a list
        :param value_columns: Columns that contains values. Used to check for identical lines and replaced based on replace
        :param replace: Boolean deciding if old values should be replaced if there is a identical row (except for value_columns)
                If True new value will be kept, if False, old value will be kept
        :param sql_conn: Instance of SQLConnection class
        :param ignore_duplicates_check True if you want no duplicate check to run
        :param recipients string with emails that should receive email in case of errors
        :raises Exception if input_data on unrecognizable structure.
        """
        engine, conn = sql_conn.get_connection()
        if input_data is None:
            self.send_email(sql_conn, recipients, "Input data cannot be None / empty")
            raise Exception("Input_data can not be None")
        col_list = self.get_table_columns(
            table_name,
            schema_name,
            sql_conn,
        ).values.tolist()  # using this in case they are not using column_name_list
        if max(len(col_list), len(column_name_list)) <= len(value_columns):
            self.send_email(
                sql_conn,
                recipients,
                "Every column cannot be a value column",
            )
            raise Exception("every column cant be a value column!")

        schema_created = False
        try:
            engine.execute(sal.schema.CreateSchema(schema_name), checkfirst=True)
            print("Created new schema in DB: " + schema_name)
            schema_created = True  # solve differently??
        except:
            print("Schema " + schema_name + " exists in DB")
        if any(isinstance(i, list) for i in input_data):  # list in list
            df = pd.DataFrame(input_data, columns=column_name_list)
            self.df_to_db(
                table_name,
                schema_name,
                df,
                value_columns,
                replace,
                schema_created,
                sql_conn,
                ignore_duplicates_check,
                crawldate_column,
                recipients,
            )

        elif isinstance(input_data, list):  # list
            if len(column_name_list) == len(input_data):
                df = pd.DataFrame([input_data], columns=column_name_list)  # list = row
            else:
                df = pd.DataFrame(input_data, columns=column_name_list)  # list = column
            self.df_to_db(
                table_name,
                schema_name,
                df,
                value_columns,
                replace,
                schema_created,
                sql_conn,
                ignore_duplicates_check,
                crawldate_column,
                recipients,
            )

        elif isinstance(input_data, pd.DataFrame):  # pandas.Dataframe
            self.df_to_db(
                table_name,
                schema_name,
                input_data,
                value_columns,
                replace,
                schema_created,
                sql_conn,
                ignore_duplicates_check,
                crawldate_column,
                recipients,
            )
        elif isinstance(input_data, np.ndarray):  # np.ndarray
            df = pd.DataFrame(input_data)
            self.df_to_db(
                table_name,
                schema_name,
                df,
                value_columns,
                replace,
                schema_created,
                sql_conn,
                ignore_duplicates_check,
                crawldate_column,
                recipients,
            )
        elif isinstance(input_data, dict):  # dict
            df = pd.DataFrame(input_data.items(), columns=column_name_list)
            self.df_to_db(
                table_name,
                schema_name,
                df,
                value_columns,
                replace,
                schema_created,
                sql_conn,
                ignore_duplicates_check,
                crawldate_column,
                recipients,
            )
        else:
            body = (
                f"Did not recognize data structure for insert into {schema_name}.{table_name} crawler. "
                f"Please change data structure"
            )
            if schema_created:
                self.drop_schema(schema_name, sql_conn)
            self.send_email(sql_conn, recipients, body)
            raise Exception("DID NOT RECOGNISE INPUT: " + str(input_data))

    def df_to_db(
        self,
        table_name,
        schema_name,
        df,
        value_columns,
        replace,
        schema_created,
        sql_conn,
        ignore_duplicates_check,
        crawldate_column,
        recipients,
    ):
        """Push Data to the selected table and provide errors if they occur,
        this should also append today's date to the data as a 'Crawled Date' column
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param df: Dataframe to be pushed to database
        :param value_columns: columns with values
        :param replace: Boolean deciding if old or new values should be kept in case of duplicates (excluding value columns)
        :param schema_created: Schema_created flag for deleting schema if upload to DB fails. Used to avoid empty schemas in DB
        :param sql_conn: Intance of SQLConnection class
        :param ignore_duplicates_check True if you want no duplicate check to run
        :param crawldate_column: String describing name of crawl_date column. Default is 'CrawlDate'
        :param recipients string with emails that should receive email in case of errors
        """

        # TODO Should the default column name be changed from CrawlDate to UploadDate?
        col_list = []  # used for feedback to user
        if crawldate_column:
            if crawldate_column not in df:
                df[crawldate_column] = pandas.Timestamp.now()
        elif "CrawlDate" not in df:
            df["CrawlDate"] = pandas.Timestamp.now()
        engine, conn = sql_conn.get_connection()
        varchar_cols = {}
        for i in range(len(df.columns)):
            if "object" in str(df.dtypes[i]):  # to avoid varchar(max)
                varchar_cols[df.columns[i]] = sal.types.NVARCHAR(self.max_varchar)
        before = self.get_row_count(table_name, schema_name, sql_conn)
        try:
            # this will fail if there is a new column
            df.to_sql(
                table_name,
                schema=schema_name,
                con=engine,
                if_exists="append",
                index=False,
                dtype=varchar_cols,
                chunksize=int(math.floor(2100 / len(df.columns))) - 1,
                method="multi",
            )
        except:
            try:
                cols = self.get_table_columns(table_name, schema_name, sql_conn)["COLUMN_NAME"].tolist()
                for i in range(len(df.columns.values)):
                    if df.columns.values[i] not in cols:
                        col_list.append(df.columns.values[i])
                        type = self.get_dtype(df.dtypes[i])
                        query = f"ALTER TABLE {schema_name}.{table_name} ADD [{df.columns.values[i]}] {type}"
                        sql_conn.execute(query)
                df.to_sql(
                    table_name,
                    schema=schema_name,
                    con=engine,
                    if_exists="append",
                    index=False,
                    chunksize=int(math.floor(2100 / len(df.columns))) - 1,
                    method="multi",
                )
            except Exception as e:
                if schema_created:
                    self.drop_schema(schema_name, sql_conn)
                self.monitor_crawler(table_name, schema_name, 0, False, engine)
                self.send_email(
                    sql_conn,
                    recipients,
                    f"Adding to {schema_name}.{table_name} failed. The following error occured: " + str(e),
                )
                raise Exception(
                    f"Adding to {schema_name}.{table_name} failed. The following error occured: " + str(e),
                )
        if not ignore_duplicates_check:
            self.remove_duplicates(
                table_name,
                schema_name,
                replace,
                value_columns,
                sql_conn,
                crawldate_column,
            )
        after = self.get_row_count(table_name, schema_name, sql_conn)
        self.monitor_crawler(table_name, schema_name, after - before, True, engine)
        if len(col_list) != 0:
            text = (
                f"{after - before} rows added to: {table_name}. Before: {before} rows, after: {after} rows. Also added following new columns: "
                + " ,".join(col_list)
            )
            print(text)
        else:
            text = f"{after - before} rows added to: {table_name}. Before: {before} rows, after: {after} rows."
            print(text)
        if before != after:
            body = text + "\n\n" + f"""{df.head(50).to_html(index=False)}"""
            self.send_email(
                sql_conn,
                recipients,
                MIMEText(body.replace("\n", "<br>"), "html"),
                "New data added to " + table_name,
            )

    def remove_duplicates(
        self,
        table_name,
        schema_name,
        replace,
        value_columns,
        sql_conn,
        crawldate_column="CrawlDate",
    ):
        """Method for removing duplicates from DB
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param replace: Boolean describing if old or new values are to be kept in case of duplicates.
        :param value_columns: List with name of columns where values are
        :param sql_conn: Instance of SQLConnection class
        :param crawldate_column: String describing name of crawl_date column. Default is 'CrawlDate'
        """
        if replace:
            sql_val = "Desc"
        else:
            sql_val = "Asc"
        col_list = self.get_table_columns(
            table_name,
            schema_name,
            sql_conn,
        ).values.tolist()
        if len(col_list) <= len(value_columns):
            raise Exception("every column cant be a value column!")
        col_string = ""
        server_name, db_name = sql_conn.get_names()
        for i in col_list:
            if i[0] in value_columns or i[0] == "CrawlDate":
                continue
            else:
                col_string += f"[{i[0]}], "
        params = (
            f"BEGIN WITH CTE AS (SELECT *, ROW_NUMBER() OVER"
            f" (PARTITION BY {col_string[:-2]} order by [{crawldate_column}] {sql_val})"
            f" AS RN FROM [{db_name}].[{schema_name}].[{table_name}]) DELETE FROM CTE WHERE RN<>1 END COMMIT"
        )
        sql_conn.execute(params)

    def get_dtype(self, pandas_type):
        """Method used for finding correct type
        :param pandas_type: Type in pandas
        :return: Type in SQL
        """
        if "object" in str(pandas_type):
            return sal.types.NVARCHAR(self.max_varchar)
        elif "datetime" in str(pandas_type):
            return sal.types.DateTime()
        elif "float" in str(pandas_type):
            return sal.types.Float(asdecimal=True)
        elif "int" in str(pandas_type):
            return sal.types.INT()
        else:  # rarely happen?
            return sal.types.NVARCHAR(self.max_varchar)

    def format_string(self, string):
        """For formatting strings
        :param string: string to be formatted

        :return: formatted string
        """
        s = "-------------------------------------------------------"
        return s + "\n" + string + "\n" + s + "\n"

    def drop_schema(self, schema_name, sql_conn):
        """Method for dropping schema and all subtables
        :param schema_name: Name of schema
        :param sql_conn: Instance of SQLConnection class
        """
        df = sql_conn.read_to_df(
            f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES Where TABLE_SCHEMA = '{schema_name}'",
        )
        for i in range(len(df)):
            sql_conn.execute(f"DROP TABLE [{schema_name}].[{df.values[i][0]}]")
        sql_conn.execute(f"DROP SCHEMA [{schema_name}]")
        print(f"{schema_name} and subtables has been dropped")

    def monitor_crawler(self, table_name, schema_name, nr_of_lines, successful, engine):
        """Method for running the monitoring table
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param nr_of_lines number of lines added
        :param successful if upload was successful or not
        :param engine engine used to connect to database
        """
        try:
            engine.execute(sal.schema.CreateSchema("Info"), checkfirst=True)
            print("Info-Schema created")
        except:
            print("updating monitoring table...")
        col_dtypes = {
            "Table": sal.types.NVARCHAR(255),
            "Schema": sal.types.NVARCHAR(255),
            "Nr_of_rows": sal.types.INT(),
            "Timestamp": sal.types.DateTime(),
        }
        df = pd.DataFrame(
            [
                [
                    schema_name,
                    table_name,
                    nr_of_lines,
                    successful,
                    pd.pandas.Timestamp.now(),
                ],
            ],
            columns=["Schema", "Table", "Nr_of_rows", "Upload successful", "Timestamp"],
        )
        df.to_sql(
            "MonitoringTable",
            schema="Info",
            con=engine,
            if_exists="append",
            index=False,
            dtype=col_dtypes,
        )

    def get_row_count(self, table_name, schema_name, sql_conn):
        """Method for getting row count
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param sql_conn: Instance of SQLConnection class
        :return number of lines in table
        """
        # this might later be replaced by count=df.to_sql(). Not a current feature, but talks of implementing it.
        try:
            df = sql_conn.read_to_df(
                f"SELECT COUNT(*) FROM [{schema_name}].[{table_name}]",
            )
            return int(df.values[0][0])
        except:
            return 0

    def send_email(self, sql_conn, recipients, body, subject="Crawler Error"):
        """:param sql_conn: Instance of SQLConnection class
        :param recipients recipients of email, string or list
        :param body message to be written in email. The subject is always "Crawler failed"
        """
        if recipients is not None:
            engine, conn = sql_conn.get_connection()
            if isinstance(recipients, list):
                recipients = ";".join(recipients)
            query = (
                "Begin EXEC msdb.dbo.sp_send_dbmail "
                "@profile_name = 'TechnologySupport', "
                f"@recipients = '{recipients}', "
                f"@body = '{body}', "
                "@body_format = 'HTML', "
                f"@subject = '{subject}'; End Commit"
            )
            engine.execute(query)
            print(f"mail sent to {recipients}")

    def set_max_varchar(self, varchar_size):
        """:param max_varchar_size size of maximum length of varchar"""
        if varchar_size > 1023:
            raise Exception("Varchar too big, maximum is 1023")
        elif varchar_size == 0:
            raise Exception("Varchar size cannot be 0")
        else:
            self.max_varchar = varchar_size

    def get_newest_date(self, table_name, schema_name, col_name, sql_conn):
        """Method for getting the newest date present
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param sql_conn: Instance of SQLConnection class
        :return number of lines in table
        """
        try:

            res_df = sql_conn.read_to_df(
                f"Select Top 1 {col_name} From {schema_name}.{table_name} Order By {col_name} Desc",
            )
            date = pd.to_datetime(res_df.iloc[0][0])
            return date
        except:
            return 0
