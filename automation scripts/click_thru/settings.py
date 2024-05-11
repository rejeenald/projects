import datetime as dt
import os
import pandas as pd

PRODUCTION = True
ACTIVE_EMAIL_NOTIFICATION = False
RETRY_COUNT = 20
REGION = "us-east-1"
TIMEOUT = 60
AWS_ACCESS_KEY = "------"
AWS_SECRET_KEY = "-------"
ROLE_ARN = "--------"

US_CREDENTIALS = dict(
    refresh_token='------',
    lwa_app_id='-------',
    lwa_client_secret='------5', 
    aws_access_key=AWS_ACCESS_KEY,
    aws_secret_key=AWS_SECRET_KEY,
    role_arn=ROLE_ARN
)

if PRODUCTION:
    SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
    ASIN_SKU = SYNCPLICITY_ROOT + "-----------------"
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
else:
    SYNCPLICITY_ROOT = ""
    SCRIPT_LOG_PATH = "__logs_and_csvs"
    ASIN_SKU = "--------------.csv"

MARKETPLACE_IDS ={
    "US": "-------------",
} 

START_DATE_THRESHOLD = 3
END_DATE_THRESHOLD = 1
DATE_NOW = dt.datetime.utcnow().date()
END_DATE = DATE_NOW - dt.timedelta(days=END_DATE_THRESHOLD)
START_DATE = DATE_NOW - dt.timedelta(days=START_DATE_THRESHOLD)