import datetime as dt
import logging
import pandas as pd

class ShipByOrders:
    def __init__(self, orders:list) -> None:
        self.shipby_date = dt.datetime.now().date()
        self.orders = pd.DataFrame(orders)
        self.get_shipby_today()
        self.remove_not_shipby_today()
        self.orders.drop(columns=["shipby_today"], axis=1, inplace=True)
        
    @property
    def shipby_today_orders(self) -> pd.DataFrame:
        return self.orders

    def get_shipby_today(self) -> None:
        logging.info(f"Marking orders to be shipped on this date: {self.shipby_date}")
        self.orders["shipby_today"] = self.orders.apply(lambda x: self._mark_shipby_today(shipby_date=x["shipByDate"]), axis=1)

    def _mark_shipby_today(self, shipby_date:str) -> None:
        if shipby_date:
            shipby_date = shipby_date.split("T")[0]
            shipby_date = dt.datetime.strptime(shipby_date, "%Y-%m-%d").date()
            if shipby_date <= self.shipby_date:
                logging.debug(f"Added to orders today: {shipby_date}")
                return True
        return False
        
    def remove_not_shipby_today(self) -> None:
        logging.info(f"Removing orders no to be shipped today...")
        self.orders = self.orders[self.orders["shipby_today"] != False]