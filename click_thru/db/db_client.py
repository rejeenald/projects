import datetime as dt
import logging
import pandas as pd
import sqlite3 as db
from .db_settings import DB_PATH

class DBClient:
    def __init__(self) -> None:
        logging.info("\"===========================DBClient===========================\"")
        self.con = db.connect(DB_PATH)
        logging.info(f"Database opened successfully: {DB_PATH}")
   
    def save_to_table(self, report:pd.DataFrame, table_name:str, start_date:str) -> None:
        logging.info(f"Saving report to {table_name} Date = {start_date}")
        self._delete_existing(table_name=table_name, start_date=start_date)
        report.to_sql(table_name, self.con, if_exists="append", index=False)
        self.con.close()

    def _delete_existing(self, table_name:str, start_date:str) -> None:
        formatted_date  = start_date.strftime("%Y-%m-%d")
        query = f'''DELETE FROM {table_name} WHERE Date = '{formatted_date}';'''
        logging.info(f"Executing query: {query}")
        logging.debug(f"start_date: {type(start_date)}")
        self.con.execute(query)
        self.con.commit()
        logging.debug(f"Deleted records for date: {formatted_date}")

    
    @staticmethod
    def drop_duplicates(table_name, report):
        report.drop_duplicates(keep=False)