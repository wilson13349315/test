from . import methods, sql_connection

"""
Created 05.07.2021

:Author: Andreas Rystad
"""


class resqlconnection:
    """Class used for connecting and communicating with SQL"""

    sql_conn = None
    method = None

    def __init__(self, server_name, db_name, local=True, remote_args={}):
        """Method for initialising class. Makes a connection with database
        :param server_name: String with name of server
        :param db_name: String with name of database
        """
        try:
            self.sql_conn = sql_connection.SQLConnection(
                server_name,
                db_name,
                local,
                remote_args,
            )
            self.method = methods
            print("Connection created")
            self.method = methods.Method(255)
        except Exception as e:
            print(str(e))
            raise Exception(
                f"something went wrong with creating a connection with {server_name} and {db_name}",
            )

    def get_table_info(self, table_name, schema_name):
        """Method for returning information about a certain table. Includes columns, data types and number of rows
        :param table_name: Name of table
        :param schema_name: Name of schema
        :return: Dataframe with columns and data types
        """
        return self.method.get_table_info(table_name, schema_name, self.sql_conn)

    def get_all_tables(self):
        """Method for returning all tables in selected database
        :return: tables in DB
        """
        return self.method.get_all_tables_info(self.sql_conn)

    def preview_table(self, table_name, schema_name, nr_of_lines=5):
        """Method that prints first rows of a table
        :param table_name: Name of table
        :param schema_name: Name of schema
        :param nr_of_lines: Number of lines to be printed. Default value is 5
        :return: preview of table
        """
        return self.method.preview_table(
            table_name,
            schema_name,
            nr_of_lines,
            self.sql_conn,
        )

    def push_data(
        self,
        table_name,
        schema_name,
        input_data,
        column_name_list,
        value_columns,
        crawldate_column="CrawlDate",
        replace=False,
        ignore_duplicates_check=False,
        recipients=None,
    ):
        """Pushes data to SQL server. Also appends a CrawlDate column if it does not exist
        :param table_name: String with name of table
        :param schema_name: String with name of schema
        :param input_data: Data to be pushed to database
        :param column_name_list: List with name of columns. Only important if input is on list format
        :param value_columns: List with name of columns where values are. These will be ignored when looking for duplicates
        :param crawldate_column: String describing name of crawl_date column. Default is 'CrawlDate'
        :param replace: Boolean describing if replacing old values or discarding new ones when a duplicate happens.
        :param ignore_duplicates_check True if you want no duplicate check to run
        :param recipients list or string with emails that will receive message if method fails
        """
        return self.method.push_data(
            table_name,
            schema_name,
            input_data,
            column_name_list,
            value_columns,
            crawldate_column,
            replace,
            ignore_duplicates_check,
            self.sql_conn,
            recipients,
        )

    def remove_duplicates(self, table_name, schema_name, replace, value_columns):
        """Method for removing duplicate rows from SQL database
        :param table_name: String with name of table
        :param schema_name: String with name of schema
        :param replace: Boolean describing if replacing old values or discarding new ones when a duplicate happens
        :param value_columns: Columns that contains value. Will be ignored when looking for duplicates
        :param crawldate_column: String describing name of crawl_date column. Default is 'CrawlDate'
        :return:
        """
        return self.method.remove_duplicates(
            table_name,
            schema_name,
            replace,
            value_columns,
            self.sql_conn,
        )

    def send_email(self, recipients, message, subject="Crawler Failed"):
        """:param recipients email addresses, string or list
        :param message to be written in email. The subject is always "Crawler failed"
        """
        return self.method.send_email(self.sql_conn, recipients, message, subject)

    def set_max_varchar(self, max_varchar_size):
        """:param max_varchar_size size of maximum length of varchar"""
        self.method.set_max_varchar(max_varchar_size)

    def get_newest_date(self, table_name, schema_name, date_column_name):
        """Getting the newest date present
        :param date_column_name: name of column in database that holds date
        """
        return self.method.get_newest_date(
            table_name,
            schema_name,
            date_column_name,
            self.sql_conn,
        )

    def get_row_count(self, table_name, schema_name):
        """Getting the number of rows"""
        return self.method.get_row_count(table_name, schema_name, self.sql_conn)
