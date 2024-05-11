import datetime as dt
import logging
from .date_settings import START_DATE, END_DATE

class DateSetter:
    def __init__(self) -> None:
        self._end_date = END_DATE
        self._start_date = START_DATE

    @property
    def start_date(self):
        return self._start_date
    
    @property
    def end_date(self):
        return self._end_date
    
    @end_date.setter
    def end_date(self, end_date):
        logging.debug(f"Enddate to move a day before: {end_date}")
        self._end_date = end_date - dt.timedelta(days=1)
        logging.debug(f"Enddate to move a day before: {self.end_date}")

    
    
    
