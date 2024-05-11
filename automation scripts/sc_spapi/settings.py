import datetime as dt
import os
import pandas as pd

PRODUCTION = True
ACTIVE_EMAIL_NOTIFICATION = False
RETRY_COUNT = 20
REGION = "us-east-1"
TIMEOUT = 60
AWS_ACCESS_KEY = "-------------------"
AWS_SECRET_KEY = "-------------------"
ROLE_ARN = "-------------------"

US_CREDENTIALS = dict(
    refresh_token='-------------------',
    lwa_client_secret='-------------------', 
    aws_access_key=AWS_ACCESS_KEY,
    aws_secret_key=AWS_SECRET_KEY,
    role_arn=ROLE_ARN
)

if PRODUCTION:
    SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
    ASIN_SKU = SYNCPLICITY_ROOT + "-------------------.csv"
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
else:
    SYNCPLICITY_ROOT = ""
    SCRIPT_LOG_PATH = "__logs_and_csvs"
    ASIN_SKU = "-------------------.csv"

MARKETPLACE_IDS ={
    "US": "-------------------",
} 