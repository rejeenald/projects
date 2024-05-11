import datetime as dt
import logging
import json
import pandas as pd
import time

from date_setter.date_setter import DateSetter
from db.db_client import DBClient
from spapi.custom_sp_api import CustomSPAPI
from settings import US_CREDENTIALS, CA_CREDENTIALS, TIMEOUT, RETRY_COUNT

class VCReports:
    def __init__(self, country:str="US") -> None:
        logging.info("\"===========================VCReports===========================\"")
        logging.info(f"Getting report from {country}")
        credentials = US_CREDENTIALS if country == "US" else CA_CREDENTIALS
        logging.debug(f"Credentials: {credentials}")
        self.sp_obj = CustomSPAPI(credentials=credentials)
        self.retry_count = RETRY_COUNT 
        self.date_setter = DateSetter()

    def request_report(self, marketplace_id:str, report_type:str, forecasting:bool=False) -> int:
        end_date = self.date_setter.end_date
        logging.info(f"Creating a new {report_type} report for {marketplace_id} from {self.date_setter.start_date} to {end_date}.")
        request_response = self.sp_obj.request_report(report_type=report_type, start_date=str(self.date_setter.start_date), end_date=str(end_date), marketplace_ids=[marketplace_id], forecasting=forecasting)
        report_data = self.__request_report_with_the_id(request_response)
        if not report_data:
            logging.info(f"The report data for the requested date range is not yet available. Moving end_date {end_date} to a day before.")
            self.date_setter.end_date=end_date
            logging.info(f"New end date: {self.date_setter.end_date}")
            return self.request_report(marketplace_id=marketplace_id, report_type=report_type, forecasting=forecasting)
        return report_data

    def __request_report_with_the_id(self, request_response):
        report_id = request_response['payload']['reportId']
        logging.info(f"Report ID: {report_id}")
        report_document_id = self._request_report_document_id(report_id=report_id)
        report_data = self._request_to_download_report(report_document_id=report_document_id)
        if "errorDetails" in report_data.keys():
            return
        return report_data

    def _request_report_document_id(self, report_id:int) -> str:
        logging.info(f"Getting the report document for report id {report_id}")
        while self.retry_count:
            report_status_response = self.sp_obj.get_report_status(report_id)
            logging.info(f"report_status_response: {report_status_response['payload']}")
            if report_status_response['payload'].get('reportDocumentId'):
                report_document_id = report_status_response['payload'].get('reportDocumentId')
                logging.info(f"Report document ID: {report_document_id}")
                return report_document_id

            self.retry_count -= 1
            logging.info(f"Waiting for {TIMEOUT} seconds...")
            time.sleep(TIMEOUT)

        logging.warning(f"ReachED RETRY_COUNT LIMIT {self.retry_count}! No report document id returned by Amazon for {report_id}.")
        return
        

    def _request_to_download_report(self, report_document_id:str) -> pd.DataFrame:
        return self.sp_obj.download_report(report_document_id)
    
    def save_report_to_db(self, report:pd.DataFrame, table_name:str) -> None:
        logging.info(f"Saving report to database table: {table_name}")
        db = DBClient()
        db.save_to_table(table_name=table_name, report=report, start_date=self.date_setter.start_date, end_date=self.date_setter.end_date)
        # report.to_csv(table_name, index=False)
        logging.info(f"Report saved to database: table name: {table_name}")
