import datetime as dt
import logging
import json
import pandas as pd
import time


from db.db_client import DBClient
from spapi.custom_sp_api import CustomSPAPI
from settings import US_CREDENTIALS, TIMEOUT, RETRY_COUNT

class SCReports:
    def __init__(self, country:str="US") -> None:
        logging.info("\"===========================SCReports===========================\"")
        logging.info(f"Getting report from {country}")
        credentials = US_CREDENTIALS
        logging.debug(f"Credentials: {credentials}")
        self.sp_obj = CustomSPAPI(credentials=credentials)
        self.retry_count = RETRY_COUNT 

    def request_report(self, marketplace_id:str, report_type:str, date_to_collect:dt.datetime) -> int:
        logging.info(f"Creating a new {report_type} report for {marketplace_id} from {date_to_collect} to {date_to_collect}.")
        request_response = self.sp_obj.request_report(report_type=report_type, start_date=str(date_to_collect), end_date=str(date_to_collect), marketplace_ids=[marketplace_id])
        report_data = self.__request_report_with_the_id(request_response)
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
    
    def save_report_to_db(self, report:pd.DataFrame, table_name:str, date_to_remove:dt.datetime) -> None:
        logging.info(f"Saving report to database table: {table_name}")
        db = DBClient()
        logging.debug(f"Start date: {date_to_remove}")
        logging.debug(f"End date: {date_to_remove}")
        db.save_to_table(table_name=table_name, report=report, start_date=date_to_remove)
        logging.info(f"Report saved to database: table name: {table_name}")