import datetime as dt
import logging
import pandas as pd

class PaidOrders:
    def __init__(self, orders:list) -> None:
        self.orders = pd.DataFrame(orders)
        self._get_paid_orders()
        self._remove_unpaid()
        self.orders.drop(columns=["paid"], axis=1, inplace=True)
        
    @property
    def paid_orders(self) -> dict:
        return self.orders.to_dict("records")

    def _get_paid_orders(self) -> None:
        logging.info(f"Getting paid orders only...")
        self.orders["paid"] = self.orders.apply(lambda x: self.__mark_paid(amount_paid=x["amountPaid"]), axis=1)

    def __mark_paid(self, amount_paid:str) -> None:
        if amount_paid:
            return True
        return False
        
    def _remove_unpaid(self) -> None:
        logging.info(f"Removing orders no to be shipped today...")
        self.orders = self.orders[self.orders["paid"] != False]