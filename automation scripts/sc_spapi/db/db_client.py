import datetime as dt
import logging
import pandas as pd
import sqlite3 as db
from .db_settings import DB_PATH, DB_PRODUCTION, MOCK_DF, TEST_TABLE, TEST_TABLE_COLS

class DBClient:
    def __init__(self) -> None:
        logging.info("\"===========================DBClient===========================\"")
        self.con = db.connect(DB_PATH)
        logging.info(f"Database opened successfully: {DB_PATH}")
   
    def save_to_table(self, report:pd.DataFrame, table_name:str, start_date:str, end_date:str) -> None:
        logging.info(f"Saving report to {table_name} Date >= {start_date}")
        if table_name != "vc_forecast":
            self._delete_existing(table_name=table_name, start_date=start_date, end_date=end_date)
            report.to_sql(table_name, self.con, if_exists="append", index=False)
        else:
            report.to_sql(table_name, self.con, if_exists="replace", index=False)
        self.con.close()

    def _delete_existing(self, table_name:str, start_date:str, end_date:str) -> None:
        
        while start_date <= end_date:
            query = f'''DELETE FROM {table_name} WHERE Date = '{start_date}';'''
            logging.info(f"Executing query: {query}")
            start_date = dt.datetime.strptime(start_date, "%m-%d-%Y")
            start_date += dt.timedelta(days=1)
            start_date = start_date.strftime("%m-%d-%Y")
            logging.debug(f"start_date: {start_date}")
            self.con.execute(query)
            self.con.commit()
    
    @staticmethod
    def drop_duplicates(table_name, report):
        if not TEST_TABLE_COLS:
            if "sales" in table_name:
                report.drop_duplicates(keep=False)
            else:
                report.drop_duplicates(keep=False)
        else:
            report.drop_duplicates(TEST_TABLE, keep=False)