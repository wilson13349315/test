# -*- coding: utf-8 -*-
"""Created on Wed Jun 17 13:03:21 2020.

@author: Simene
"""
import uuid

import pandas as pd
import pyodbc
import sqlalchemy


class MySqlConnection:
    """A convenient method to connect to SQL."""

    def __init__(self, server_name, database_name):
        """Create sql connection, cursor and engine.

        Parameters
        ----------
        server_name : str
            Server name.
        database_name : str
            Database name.

        """
        self.server_name = server_name
        self.database_name = database_name
        self.params = "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=%s; DATABASE=%s; Trusted_Connection=Yes" % (
            self.server_name,
            self.database_name,
        )
        self.connection = pyodbc.connect(self.params)
        self.connection_cursor = self.connection.cursor()
        self.connection_engine = sqlalchemy.create_engine(
            "mssql+pyodbc://%s/%s?driver=ODBC+Driver+17+for+SQL+Server" % (self.server_name, self.database_name),
            fast_executemany=True,
        )

    def get_connection_information(self):
        print(f"Server: {self.server_name}")
        print(f"Database: {self.database_name}")

    def sql_to_df(self, query):
        """Reads query to pandas dataframe.

        Parameters
        ----------
        query : str
            SQL query.

        Returns
        -------
        Pandas DataFrame.

        """
        return pd.read_sql_query(query, self.connection_engine)

    def df_to_sql(self, df, table_name, schema):
        """Uploads pandas dataframe to sql.

        ### Parameters
        ----------
        df : DataFrame
            Data to upload.
        table_name : str
            Table name in SQL database.
        schema : str
            Schema name in SQL database.


        """
        df.to_sql(
            name=table_name,
            con=self.connection_engine,
            if_exists="append",
            index=False,
            schema=schema,
            chunksize=20000,
        )

        print(f"{len(df.index)} rows added to SQL")

    def df_sql_upsert(  # noqa: PLR0913
        self,
        data_frame: pd.DataFrame,
        table_name: str,
        schema: str,
        match_columns: "list[str]" = None,
        chunksize: int = None,
        dtype: dict = None,
        skip_inserts: bool = False,
        skip_updates: bool = False,
    ):
        """Perform an "upsert" on a SQL Server table from a DataFrame. Constructs a T-SQL MERGE statement, uploads the DataFrame to a temporary table, and then executes the MERGE.

        Parameters
        ----------
        data_frame : pandas.DataFrame
            The DataFrame to be upserted.
        table_name : str
            The name of the target table.
        schema : str
            The name of the schema containing the target table.
        match_columns : list of str, optional
            A list of the column name(s) on which to match. If omitted, the
            primary key columns of the target table will be used.
        chunksize: int, optional
            Specify chunk size for .to_sql(). See the pandas docs for details.
        dtype : dict, optional
            Specify column types for .to_sql(). See the pandas docs for details.
        skip_inserts : bool, optional
            Skip inserting unmatched rows. (Default: False)
        skip_updates : bool, optional
            Skip updating matched rows. (Default: False)

        """

        if skip_inserts and skip_updates:
            raise ValueError("skip_inserts and skip_updates cannot both be True")

        temp_table_name = "##" + str(uuid.uuid4()).replace("-", "_")

        table_spec = ""
        if schema:
            table_spec += "[" + schema.replace("]", "]]") + "]."
        table_spec += "[" + table_name.replace("]", "]]") + "]"

        df_columns = list(data_frame.columns)
        if not match_columns:
            insp = sqlalchemy.inspect(self.connection_engine)
            match_columns = insp.get_pk_constraint(table_name, schema=schema)["constrained_columns"]

        columns_to_update = [col for col in df_columns if col not in match_columns]

        stmt = f"MERGE {table_spec} WITH (HOLDLOCK) AS main\n"
        stmt += f"USING (SELECT {', '.join([f'[{col}]' for col in df_columns])} FROM {temp_table_name}) AS temp\n"

        join_condition = " AND ".join([f"main.[{col}] = temp.[{col}]" for col in match_columns])
        stmt += f"ON ({join_condition})"

        if not skip_updates:
            stmt += "\nWHEN MATCHED THEN\n"
            update_list = ", ".join([f"[{col}] = temp.[{col}]" for col in columns_to_update])
            stmt += f"  UPDATE SET {update_list}"

        if not skip_inserts:
            stmt += "\nWHEN NOT MATCHED THEN\n"
            insert_cols_str = ", ".join([f"[{col}]" for col in df_columns])
            insert_vals_str = ", ".join([f"temp.[{col}]" for col in df_columns])
            stmt += f"  INSERT ({insert_cols_str}) VALUES ({insert_vals_str})"

        stmt += ";"

        with self.connection_engine.begin() as conn:
            data_frame.to_sql(temp_table_name, conn, index=False, chunksize=chunksize, dtype=dtype)
            conn.exec_driver_sql(stmt)
            conn.exec_driver_sql(f"DROP TABLE IF EXISTS {temp_table_name}")

    def truncate_table(self, table_name, schema, reseed=False):
        """Truncates selected table in the database.

        Parameters
        ----------
        table_name : str
            Table name in SQL database.
        schema: str
            SQL schema

        """
        query = f"""TRUNCATE TABLE {schema}.{table_name}"""
        self.connection_cursor.execute(query)
        self.connection.commit()

        if reseed:
            query = f"""DBCC CHECKIDENT ('{schema}.{table_name}', RESEED, 1);"""
            self.connection_cursor.execute(query)
            self.connection.commit()

    def delete_with_conditions(self, table_name, schema, conditions):
        """Replicating a SQL query for deleting rows with conditions.

        Parameters
        ----------
        table_name : string, name of table,
        schema :  string, name of schema
        conditions : string, SQL format of the where clause. Example: Country = 'Norway' AND Year between 2010 and 2021 and Sector in ('Road, 'Aviation')

        """
        assert isinstance(table_name, str)
        assert isinstance(schema, str)
        assert isinstance(conditions, str)

        query_delete = f"""DELETE FROM {schema}.{table_name} WHERE {conditions}"""
        with self.connection_engine.begin() as conn:
            conn.execute(sqlalchemy.text(query_delete))

    def run_query(self, query, fetch_rows=None):
        """Run custom query with context manager. In principle, enables rollback if exception.

        Parameters
        ----------
        query : str

        """
        assert isinstance(query, str)
        with self.connection_engine.begin() as conn:
            if fetch_rows is None:
                conn.execute(sqlalchemy.text(query))
                results = None
            elif fetch_rows == "one":
                results = conn.execute(sqlalchemy.text(query)).fetchone()
                cols = ["ReturnCode", "ReturnMessage"]
                results = pd.DataFrame([tuple(results)])
                results.columns = cols
            elif fetch_rows == "all":
                print("not implemented yet")
            else:
                print("not implemented yet")

            return results

    def close_connection(self):
        """Closes the SQL connection."""
        self.connection.close()

    def df_to_new_table(self, df, table_name, schema, **kwargs):
        """Uploads pandas dataframe to sql.

        Parameters
        ----------
        table_name : str
            Table name in SQL database.
        schema: str
            schema name
        df: str
            dataframe to upload


        """
        # Default values:
        len_varchar = 255

        for key, value in kwargs.items():
            if key == "varchar":
                len_varchar = value

        print(
            f"Creating new table {self.server_name}.{self.database_name}.{schema}.{table_name} and uploading {len(df)} rows",
        )

        dtypedict = {}
        for i, j in zip(df.columns, df.dtypes):
            if "object" in str(j):
                dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=len_varchar)})

            if "datetime" in str(j):
                dtypedict.update({i: sqlalchemy.types.DateTime()})

            if "float" in str(j):
                dtypedict.update(
                    {i: sqlalchemy.types.Float(precision=3, asdecimal=True)},
                )

            if "int" in str(j):
                dtypedict.update({i: sqlalchemy.types.INT()})

        df.to_sql(
            name=table_name,
            con=self.connection_engine,
            if_exists="replace",
            index=False,
            schema=schema,
            chunksize=100000,
            dtype=dtypedict,
        )

        print("All done! :D")

    def commit_custom_query(self, query):
        self.connection_cursor.execute(query)
        self.connection.commit()


def connect_to_sql(server_name, database_name):
    """Connects to sql."""

    params = "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=%s; DATABASE=%s; Trusted_Connection=Yes" % (
        server_name,
        database_name,
    )
    connection = pyodbc.connect(params)
    connection_cursor = connection.cursor()
    connection_engine = sqlalchemy.create_engine(
        "mssql+pyodbc://%s/%s?driver=SQL+Server" % (server_name, database_name),
    )
    return connection, connection_cursor, connection_engine


if __name__ == "__main__":  # TODO change this to our gas data
    server_name = "ekofisk"
    db_name = "RealTimeData"
    schema = ""  # needed for querying data
    table_name = ""  # needed to upload to SQL
    ekofisk = MySqlConnection(server_name, db_name)  # Defines the sql object
    query = """select top(10) * from FactRealTimeData"""
    df = ekofisk.sql_to_df(query)
    print(df)
    ekofisk.close_connection()  # how to close the connection

    # ekofisk.connection # how to acces the sql connection
    # ekofisk.connection_cursor # how to access the cursor
    # ekofisk.connection_engine # how to access the engine
