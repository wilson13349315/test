"""Useful functions for gathering existing data from the db and comparing it to avoid adding already existing data to the database."""

import json
import logging
import os
from datetime import datetime

import pandas as pd

from Modules import send_email
from Modules.connect_to_sql import MySqlConnection


class SqlCompareTools:
    """Useful functions for gathering existing data from the db and comparing it to avoid adding already existing data to the database.

    Created by Murilo Romera


    Parameters
    ----------
    sql_params : dict
        SQL parameters for the connection.
    data_params : dict
        Data params used for filling the tables.
    logger: Logger
        `logging` instance for logging.

    """

    def __init__(self, sql_params: dict, data_params: dict, logger: logging.Logger) -> None:
        self.sql_params = sql_params
        self.data_params = data_params
        self.logger = logger

        self.sql_obj = MySqlConnection(
            sql_params["server_name"],
            sql_params["database_name"],
        )
        pass

    def get_last_date(self, table_name=""):
        """Gets the most recent date from the Date column.

        Parameters
        ----------
        table_name : str (optional)
            Table to get last date from. If not populated, it will use the sql_params table name.

        Returns
        -------
        datetime
            Last date recorded in the database.

        """

        table = table_name if table_name != "" else self.sql_params["table_name"]

        query = f"""
        SELECT	TOP (1)
            [Date]
        FROM	[{self.sql_params["database_name"]}].[{self.sql_params["schema_name"]}].[{table}]
        ORDER BY
            DATE DESC
        """

        last_date = self.sql_obj.sql_to_df(query)
        if len(last_date) > 0:
            timestamp = last_date.iloc[0, 0]
            return timestamp.to_pydatetime()
        return 0

    def get_old_data(
        self,
        partition_by_columns: "list[str]",
        value_column_name="Value",
        date: datetime = None,
    ):
        """Gets the already existing data from the database to do the comparison with the new data.

        Parameters
        ----------
        partition_by_columns : list[str]
            Columns that will be used in the PARTITION BY clause. Columns need to be in the same string, separated by commas.
        value_column_name : str = "Value"
            Column used to store the values.
        date : datetime = None
            (optional) If added, will filter the query by dates after this.

        Returns
        -------
        DataFrame
            Table with old values.

        """

        query = f"""
        SELECT
            {", ".join([f'[{col}]' for col in partition_by_columns])}, [{value_column_name}] AS 'old_{value_column_name}'
        FROM	(
            SELECT
                *
                ,ROW_NUMBER() OVER (PARTITION BY
                                        {", ".join([f'[{col}]' for col in partition_by_columns])}
                                    ORDER BY
                                        [CrawlDate]
                            ) rn
            FROM	[{self.sql_params["database_name"]}].[{self.sql_params["schema_name"]}].[{self.sql_params["table_name"]}]
        ) X
        WHERE
            rn = 1
        """

        if date:
            query = query + " AND [DATE] > '" + date.strftime("%Y%m%d") + "'"

        df_old = self.sql_obj.sql_to_df(query)
        return df_old

    def compare_and_upload(  # noqa: PLR0913
        self,
        df_new: pd.DataFrame,
        df_old: pd.DataFrame,
        old_column_name="old_Value",
        new_column_name="Value",
        keep_first_col=False,
        cols_to_compare: "list[str]" = None,
        should_send_email=True,
    ):
        """Compares both old and new data to avoid adding already existing data to the database. If there's new data to be added, uploads it to SQL.

        Parameters
        ----------
        df_new : DataFrame
            DataFrame with the data gathered by the crawler.
        df_old : DataFrame
            DataFrame with the existing data from the server.
        old_column_name : str = "old_Value"
            Name used for the column with the old data.
        new_column_name : str = "Value"
            Name used for the column with the new data.
        keep_first_col : bool = False
            If true, will keep the first column when comparing both tables.
        cols_to_compare : list[str] = None
            List of columns to use in comparison during upsert. If populated, `df_sql_upsert()` will be used to upload the data.

        """

        # Define columns to merge on , not sure w??
        cols2join = [
            c for c in df_old.columns if new_column_name not in c
        ]  # take every column to join apart from the column with the unit

        # Get source table information
        df_source = self.sql_obj.sql_to_df(
            f"select top 1 * from {self.sql_params['schema_name']}.{self.sql_params['table_name']}",
        )  # it selects 1 raw of values, not sure why I need it?

        # Define columns to keep
        if keep_first_col:
            cols2keep = df_source.columns
            datatypes = df_source.dtypes
        else:
            cols2keep = df_source.columns[1:]
            datatypes = df_source.dtypes[1:]

        # Define source table data types
        df_tmp = df_new[cols2keep].astype(datatypes)

        # Merge and compare new and old
        df_final = pd.merge(
            df_tmp,
            df_old,
            on=cols2join,
            how="left",
        )  # so the column that is gonna show up on the right will be the old_org_value column
        df_final = df_final.loc[
            df_final[new_column_name].astype(float).round(3) != df_final[old_column_name].astype(float).round(3)
        ].reset_index(drop=True)

        # Upload to sql if new data present
        if len(df_final) > 0:
            # Only attach top 50 changes to an email
            df2send = df_final[cols2join + [old_column_name, new_column_name]].head(50)

            # Upload new benchmarks to database
            df_final = df_final[cols2keep]

            if cols_to_compare is None or len(cols_to_compare) == 0:
                self.sql_obj.df_to_sql(
                    df_final,
                    self.sql_params["table_name"],
                    self.sql_params["schema_name"],
                )
            else:
                self.sql_obj.df_sql_upsert(
                    df_final,
                    self.sql_params["table_name"],
                    self.sql_params["schema_name"],
                    cols_to_compare,
                )

            # logging and email
            self.logger.info(f"{len(df_final.index)} data points written to sql")
            if os.getenv("SEND_EMAIL") == "True" and should_send_email:
                send_email.new_benchmark(
                    df2send,
                    fundamental=self.data_params["fundamental"],
                    country=self.data_params["country"],
                    to_emails=json.loads(os.getenv("EMAILS")),
                )
        else:
            self.logger.info("No new data")

    def upsert(self, table: pd.DataFrame, match_columns: "list[str]") -> None:
        """Directly upserts data in a selected table, without doing the numbers comparison. Useful for data not based on numbers (ex. locations).

        Parameters
        ----------
        table : DataFrame
            DataFrame with the data gathered by the crawler.
        match_columns : list[str] = None
            List of columns to use in comparison during upsert.

        """

        table_len_df = self.sql_obj.sql_to_df(
            f'SELECT COUNT(*) FROM {self.sql_params["schema_name"]}.{self.sql_params["table_name"]}',
        )
        table_len_before = table_len_df.iloc[0, 0]

        self.sql_obj.df_sql_upsert(
            table,
            self.sql_params["table_name"],
            self.sql_params["schema_name"],
            match_columns,
        )

        table_len_df = self.sql_obj.sql_to_df(
            f'SELECT COUNT(*) FROM {self.sql_params["schema_name"]}.{self.sql_params["table_name"]}',
        )
        table_len_after = table_len_df.iloc[0, 0]

        # Only attach last 50 changes to an email
        df2send = table.tail(50)

        self.logger.info(f"{len(table)} data points upserted to sql")
        if os.getenv("SEND_EMAIL") == "True" and table_len_before != table_len_after:
            send_email.new_benchmark(
                df2send,
                fundamental=self.sql_params["table_name"],
                country=self.data_params["country"],
                to_emails=json.loads(os.getenv("EMAILS")),
            )

    def truncate_and_upload(self, table: pd.DataFrame, should_send_email=True):
        """Truncates all data present in the table and completely replaces it by new values.

        Parameters
        ----------
        table : DataFrame
            DataFrame with the data to be uploaded.
        should_send_email : bool = True
            If true, will send an email with part of the data uploaded.

        """

        self.logger.info("Truncating database...")
        self.sql_obj.truncate_table(self.sql_params["table_name"], self.sql_params["schema_name"])
        self.logger.info("Uploading data...")
        self.sql_obj.df_to_sql(table, self.sql_params["table_name"], self.sql_params["schema_name"])

        # Only attach top 50 changes to an email
        df2send = table.head(50)
        self.logger.info(f"{len(table.index)} data points uploaded to sql")
        if os.getenv("SEND_EMAIL") == "True" and should_send_email:
            send_email.new_benchmark(
                df2send,
                fundamental=self.data_params["fundamental"],
                country=self.data_params["country"],
                to_emails=json.loads(os.getenv("EMAILS")),
            )

    def upload(self, table: pd.DataFrame, should_send_email=True):
        """Uploads the given DataFrame to the database table, with no comparisons and no truncation.

        Parameters
        ----------
        table : DataFrame
            DataFrame with the data to be uploaded.
        should_send_email : bool = True
            If true, will send an email with part of the data uploaded.

        """

        self.logger.info("Uploading data...")
        self.sql_obj.df_to_sql(table, self.sql_params["table_name"], self.sql_params["schema_name"])

        # Only attach top 50 changes to an email
        df2send = table.head(50)
        self.logger.info(f"{len(table.index)} data points uploaded to sql")
        if os.getenv("SEND_EMAIL") == "True" and should_send_email:
            send_email.new_benchmark(
                df2send,
                fundamental=self.data_params["fundamental"],
                country=self.data_params["country"],
                to_emails=json.loads(os.getenv("EMAILS")),
            )
