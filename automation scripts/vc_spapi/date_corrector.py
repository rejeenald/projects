import datetime as dt
import os
import pandas as pd


SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
SALES_CA = SYNCPLICITY_ROOT + "\\SCM\\raw_data_csv_spapi_testing\\sales_vendor_central_CA.csv"
SALES_US = SYNCPLICITY_ROOT + "\\SCM\\raw_data_csv_spapi_testing\\sales_vendor_central_CA.csv"
INV_US = SYNCPLICITY_ROOT + "\\SCM\\raw_data_csv_spapi_testing\\inv_vendor_central_US.csv"



def correct_date(date):
    print(f"date: {date}")
    print(f"type date: {type(date)}")
    return dt.datetime.strptime(date,"%m-%d-%Y").date() 

sales_ca = pd.read_csv(INV_US)
sales_ca["DATE"] = sales_ca["Date"].apply(lambda date: correct_date(str(date).strip()))
sales_ca.to_csv("inv_vendor_central_US_corrected.csv", index=False)



def get_year(date):
    if len(date[-1]) > 2:
        return date[-1]
    elif len(date[-1]) > 2:
        return date[0]
    else:
        return "2023"

    