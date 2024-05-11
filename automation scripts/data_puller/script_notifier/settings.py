import datetime as dt
import os
import pandas as pd

SYNCPLICITY_ROOT = os.getenv('SYNCPLICITY_HOME')

HOST = "---------------------------"
PORT = 587
SENDER_EMAIL = "---------------------------"
SENDER_PASSWORD = "---------------------------"
RECIPIENTS_CSV = SYNCPLICITY_ROOT +  r"---------------------------.csv"
RECIPIENTS = [email[0] for email in pd.read_csv(RECIPIENTS_CSV).values.tolist()]


PRODUCTION = True

DATE_NOW = dt.datetime.utcnow()
DATE_NOW_STR = DATE_NOW.strftime("%Y-%m-%d-%H-%M-%S")
FILENAME = "".join(["---------------------------", str(DATE_NOW_STR), ".csv"])

if PRODUCTION:
    RAW_DATA_CSV_FILEPATH = SYNCPLICITY_ROOT + r'---------------------------'
    STATUS_LOG = os.path.join(RAW_DATA_CSV_FILEPATH, FILENAME)
else:
    STATUS_LOG = FILENAME

print(RAW_DATA_CSV_FILEPATH)

SUBJECT_FOR_SUCCESS = "Success! Data Puller Monitor"
SUBJECT_FOR_FAILURE = "Script Failed! Data Puller Monitor"