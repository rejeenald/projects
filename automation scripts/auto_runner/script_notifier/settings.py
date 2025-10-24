import datetime as dt
import os
import pandas as pd

SYNCPLICITY_ROOT = os.getenv('SYNCPLICITY_HOME')

HOST = "smtp.office365.com"
PORT = 587
SENDER_EMAIL = "rejeenald@smartish.com"
SENDER_PASSWORD = "Sm@rtSnek"
RECIPIENTS_CSV = SYNCPLICITY_ROOT +  r"\Order Fulfillment\Custom Orders\Script Stuff\email_recipients.csv"
RECIPIENTS = [email[0] for email in pd.read_csv(RECIPIENTS_CSV).values.tolist()]

PRODUCTION = True

DATE_NOW = dt.datetime.utcnow()
DATE_NOW_STR = DATE_NOW.strftime("%Y-%m-%d-%H-%M-%S")
FILENAME = "".join(["cu_auto_runner_daily_monitor_", str(DATE_NOW_STR), ".csv"])

if PRODUCTION:
    RAW_DATA_CSV_FILEPATH = SYNCPLICITY_ROOT + r'\\Order Fulfillment\\Custom Orders\\Script Stuff\\daily_script_monitor'
    STATUS_LOG = os.path.join(RAW_DATA_CSV_FILEPATH, FILENAME)
else:
    STATUS_LOG = FILENAME

SUBJECT_FOR_SUCCESS = "Success! Auto Runner Monitor"
SUBJECT_FOR_FAILURE = "Script Failed! Auto Runner Monitor"

