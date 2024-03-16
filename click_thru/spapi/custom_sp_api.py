import logging
import json
import boto3
import pandas as pd
import requests
import gzip


from datetime import datetime, timezone
from io import BytesIO

from .aws_sig_v4 import AWSSigV4
from .spapi_settings import REGION

class CustomSPAPI:
    def __init__(self, credentials):
        logging.info("\"===========================CustomSPAPI===========================\"")
        self.access_token = None
        self.region = REGION
        self.headers = None
        if credentials:
            self.credentials = credentials
            self.refresh_token = credentials['refresh_token']
            self.client_id = credentials['lwa_app_id']
            self.client_secret = credentials['lwa_client_secret']
            self.aws_access_key = credentials['aws_access_key']
            self.aws_secret_key = credentials['aws_secret_key']
            self.role_arn = credentials['role_arn']
            self.boto3_client = boto3.client('sts',
                                             aws_access_key_id=credentials['aws_access_key'],
                                             aws_secret_access_key=credentials['aws_secret_key'])
            self.get_access_token()
            self.set_headers()

    def get_access_token(self):
        logging.info("Getting access token...")
        res = requests.post('https://api.amazon.com/auth/o2/token',
                            data={'grant_type': 'refresh_token',
                                  'refresh_token': self.refresh_token,
                                  'client_id': self.client_id,
                                  'client_secret': self.client_secret})

        self.access_token = res.json()['access_token']
        logging.debug(f"Access token: {self.access_token}")

    def set_headers(self):
        logging.info("Setting initial headers...")
        now = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
        self.headers = {'host': 'sellingpartnerapi-na.amazon.com',
                        'user-agent': 'custom_sp_api',
                        'x-amz-access-token': self.access_token,
                        'x-amz-date': now.strftime("%Y%m%dT%H%M%SZ"),
                        'content-type': 'application/json'}

    def set_role(self):
        logging.info("Setting the role...")
        role = self.boto3_client.assume_role(RoleArn=self.role_arn, RoleSessionName='prod')
        logging.debug(f"Role: {role}")
        return role

    def _sign_request(self):
        role = self.set_role()
        return AWSSigV4('execute-api',
                        aws_access_key_id=role.get('Credentials').get('AccessKeyId'),
                        aws_secret_access_key=role.get('Credentials').get('SecretAccessKey'),
                        region=self.region,
                        aws_session_token=role.get('Credentials').get('SessionToken'))

    def request_report(self, report_type:str, start_date:str, end_date:str, marketplace_ids:str) -> json:
        logging.info(f"Request marketplace ids: {marketplace_ids}")
        request_data = self.__set_request_data(report_type, start_date, end_date, marketplace_ids)
        logging.debug(f"request data: {request_data}")
        res = requests.post('https://sellingpartnerapi-na.amazon.com/reports/2020-09-04/reports',
                            data=json.dumps(request_data),
                            headers=self.headers,
                            auth=self._sign_request())   
        logging.debug(f"response: {res}")
        return res.json()

    @staticmethod
    def __set_request_data(report_type:str, start_date:str, end_date:str, marketplace_ids:str) -> dict:
        report_options = {"sellingProgram": "RETAIL"}
        request_data = {"reportType": report_type, "marketplaceIds": marketplace_ids}
        report_options["dateGranularity"] = "DAY"
        report_options["asinGranularity"] = "CHILD"
        request_data["dataStartTime"] = start_date
        request_data["dataEndTime"] = end_date
        request_data["reportOptions"] = report_options
        return request_data

    def get_report_status(self, report_id):
        logging.info("Checking report status")
        res = requests.get('https://sellingpartnerapi-na.amazon.com/reports/2020-09-04/reports/' + report_id,
                           headers=self.headers,
                           auth=self._sign_request())

        return res.json()

    def download_report(self, report_document_id):
        # report_document_id = "amzn1.spdoc.1.4.na.46fd6341-5138-4c2a-9a04-175b0147da01.T3KM5NC4YRKXHN.43400"
        logging.info(f"Downloading report document: {report_document_id}")
        res = requests.get('https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/documents/' + report_document_id,
                           headers=self.headers,
                           auth=self._sign_request())
        res = res.json()
        logging.debug(f"Download report: {res}")
        report_data = requests.get(res['url'])
        return self.__decode_report_data(report_data)
       
    def __decode_report_data(self, report_data):
        logging.info("Decoding the report data...")
        logging.debug(f"Report_date: {type(report_data)}")
        # logging.debug(f"report response: \n\n {report_data.content}")
        try:
            return self.__extract_into_dataframe__(report_data)
        except Exception as e:
            logging.warning(f"BadGzipFile: {e}")
            # logging.debug(f"Assuming it is a json already: {report_data}")
            return

    @staticmethod
    def __extract_into_dataframe__(report_data):
        logging.info("Trying to decode...")
        buf = BytesIO(report_data.content) 
        gzip_f = gzip.GzipFile(fileobj=buf)
        report_data = gzip_f.read()
        report_data = json.loads(report_data)
        date_collected = report_data["reportSpecification"]["dataStartTime"]
        report_data = report_data["salesAndTrafficByAsin"]
        report_data = pd.DataFrame(report_data)
        report_data['Date'] = date_collected
        logging.debug(f"Dataframe: \n{report_data}")
        
        logging.debug(f"report column: {report_data.columns}")
        return report_data

        
