import datetime as dt

START_DATE_THRESHOLD = 30
END_DATE_THRESHOLD = 2
DATE_NOW = dt.datetime.utcnow().date()
END_DATE = DATE_NOW #- dt.timedelta(days=END_DATE_THRESHOLD)
START_DATE = DATE_NOW - dt.timedelta(days=START_DATE_THRESHOLD)
# START_DATE = dt.datetime.strptime("2022-09-25","%Y-%m-%d").date() 
# END_DATE = dt.datetime.strptime("2022-09-25","%Y-%m-%d").date() 