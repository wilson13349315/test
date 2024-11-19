import pandas as pd
import pyodbc
import sqlalchemy

"""
Created 05.07.2021
r
:Author: Andreas Rystad
"""


class SQLConnection:
    """
    Class for connecting to a database and server

    The following guide was used:
    https://medium.com/@anushkamehra16/connecting-to-sql-database-using-sqlalchemy-in-python-2be2cf883f85
    """

    connection = None
    cursor = None
    engine = None
    server_name = None
    db_name = None

    def __init__(self, server_name, db_name, local=True, remote_args={}):
        """
        Method initialising class with name of server and database
        :param server_name: String with server name
        :param db_name: String with DB name
        :param remote_args
        """
        self.server_name = server_name
        self.db_name = db_name

        if local:
            params = (
                "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=%s; DATABASE=%s; Trusted_Connection=Yes"
                % (server_name, db_name)
            )
            self.connection = pyodbc.connect(params)
            self.cursor = self.connection.cursor()
            self.engine = sqlalchemy.create_engine(
                "mssql+pyodbc://%s/%s?driver=ODBC+Driver+17+for+SQL+Server"
                % (server_name, db_name)
            )
        # If we can't use windows authentification then use this method
        else:
            #  params = "DRIVER=%s; SERVER=%s; DATABASE=%s; UID=%s; PWD=%s" % (remote_args['driver'],
            # server_name, db_name, remote_args['username'], remote_args['password'])
            # self.connection = pyodbc.connect(params)
            # self.cursor = self.connection.cursor()

            self.engine = sqlalchemy.create_engine(
                f"{remote_args['protocol']}://"
                f"{remote_args['username']}:"
                f"{remote_args['password']}@"
                f"{server_name}:"
                f"{remote_args['port']}/"
                f"{db_name}"
                f"?driver={remote_args['driver']}&port={remote_args['port']}&odbc_options='TDS_Version=8.0'",
                isolation_level="AUTOCOMMIT",
            )

    def execute(self, sql_statement):
        """
        Method for executing a SQL statement
        :param: sql_statement: SQL statement to be executed
        :return: result with sqlalchemy.engine.cursor.LegacyCursorResult object. (can call .rowcount)
        """
        result = self.engine.execute(sql_statement)
        return result

    def read_to_df(self, sql_statement):
        """
        Method for reading from database and turning result to dataframe
        :param sql_statement: SQL statement to be executed
        :return: pandas.Dataframe with information from sql statement
        """
        sql_result = pd.read_sql_query(sql_statement, self.engine)
        df = pd.DataFrame(sql_result)
        return df

    def get_connection(self):
        """
        Method for getting connection
        :return: engine and connection
        """
        return self.engine, self.connection

    def get_names(self):
        """
        Method for getting server and database name
        :return:
        """
        return self.server_name, self.db_name


def make_connection(server_name, db_name):
    """
    Method for creating a new connection. Can be used if one doesnt wish to have an instance
    :param server_name: name of server
    :param db_name: name of database
    :return: connection, cursor, engine
    """
    params = (
        "DRIVER={ODBC Driver 17 for SQL Server}; SERVER=%s; DATABASE=%s; Trusted_Connection=Yes"
        % (server_name, db_name)
    )
    connection = pyodbc.connect(params)
    cursor = connection.cursor()
    engine = sqlalchemy.create_engine(
        "mssql+pyodbc://%s/%s?driver=ODBC+Driver+17+for+SQL+Server"
        % (server_name, db_name)
    )
    return connection, cursor, engine
