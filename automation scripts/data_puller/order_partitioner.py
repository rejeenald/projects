import datetime as dt
import json
import logging
import pandas as pd

from settings import HEADERS, RAW_DATA_HEADERS, PRODUCTION_DATA
from valid_orders_parser import ValidOrdersParsers

class OrderPartitioner:
    def __init__(self) -> None:
        self.canceled_orders = None
        self.shipped_orders = None
        self.test_orders = None
        self.clean_orders = None
        self.persy_orders = None

    def partition_orders(self, orders:list) -> list:
        logging.info(f"Partitioning {len(orders)} orders from ShipStation...")
        orders = self.__get_valid_orders(orders)
        self._extract_clean_orders(orders)
        self._extract_shipped_orders(orders)
        self._extract_canceled_orders(orders)
        self._extract_test_orders(orders)
        self._extract_persy_orders(orders)
    
    def __get_valid_orders(self, orders) -> pd.DataFrame:
        orders = pd.DataFrame(orders)
        order_validator = ValidOrdersParsers(orders)
        co = order_validator.custom_orders
        zo = order_validator.zprint_orders
        fo = order_validator.featured_orders
        oo = order_validator.outlier_orders
        nmspink = order_validator.nmspink
        persy_orders = order_validator.persy_orders
        logging.info("Merging customs, featured, zprints, nmspink, and outlier orders!")
        return pd.concat([co, zo, fo, oo, nmspink, persy_orders])

    def _extract_clean_orders(self, orders:list) -> None: 
        logging.info(f"Size of orders: {len(orders)}")
        co = orders.query('orderStatus != "shipped"')
        co = co.query('orderStatus != "cancelled"')
        if PRODUCTION_DATA:
            co = co.query('store != 405182')
        else:
            co = co.query('store == 405182')
        co.drop_duplicates(subset=RAW_DATA_HEADERS, keep='last')
        logging.debug(f"Dropped duplicates. New size: {len(co)}")
        self.clean_orders = co[HEADERS].copy()
        logging.debug(f"Retained the on_hold and awaiting_shipment orders only excluding the testing orders: {len(co)}")

    def _extract_shipped_orders(self, orders:list) -> None: 
        logging.info(f"Size of  orders: {len(orders)}")
        so = orders.query('orderStatus == "shipped"')
        so.drop_duplicates(subset=RAW_DATA_HEADERS, keep='last')
        logging.debug(f"Dropped duplicates. New size: {len(so)}")
        self.shipped_orders = so[HEADERS].copy()
        logging.debug(f"Only shipped orders: {len(self.shipped_orders)}")

    def _extract_canceled_orders(self, orders:list) -> None: 
        logging.info(f"Size of  orders: {len(orders)}")
        cno = orders.query('orderStatus == "cancelled"')
        cno.drop_duplicates(subset=RAW_DATA_HEADERS, keep='last')
        logging.debug(f"Dropped duplicates. New size: {len(cno)}")
        self.canceled_orders = cno[HEADERS].copy()
        logging.debug(f"Only cancelled orders: {len(self.canceled_orders)}")

    def _extract_test_orders(self, orders:list) -> None: 
        logging.info(f"Size of  orders: {len(orders)}")
        to = orders.query('store == 405182')
        to.drop_duplicates(subset=RAW_DATA_HEADERS, keep='last')
        logging.debug(f"Dropped duplicates. New size: {len(to)}")
        self.test_orders = to[HEADERS].copy()
        logging.debug(f"Only test orders: {len(self.test_orders)}")

    def _extract_persy_orders(self, orders:list) -> None:
        logging.info(f"Size of orders: {len(orders)}")
        po = orders.query('orderStatus != "shipped"')
        po = po.query('orderStatus != "cancelled"')
        po = po.query('store == 388704')
        po.drop_duplicates(subset=RAW_DATA_HEADERS, keep='last')
        logging.debug(f"Dropped duplicates. New size: {len(po)}")
        self.persy_orders = po[HEADERS].copy()
        logging.debug(f"Persy orders: {len(po)}")

    @property
    def cleaned_ss_orders(self) -> pd.DataFrame:
        logging.info(f"Clean orders: {self.clean_orders.head()}")
        return self.clean_orders

    @property
    def canceled_ss_orders(self) -> pd.DataFrame:
        logging.info(f"Cancelled orders: {self.canceled_orders.head()}")
        return self.canceled_orders

    @property
    def shipped_ss_orders(self) -> pd.DataFrame:
        logging.info(f"Shipped orders: {self.shipped_orders.head()}")
        return self.shipped_orders
        
    @property
    def test_ss_orders(self) -> pd.DataFrame:
        logging.info(f"Test orders: {self.test_orders.head()}")
        return self.test_orders
    
    @property
    def persy_ss_orders(self) -> pd.DataFrame:
        logging.info(f"Persy_orders: {self.persy_orders}")
        return self.persy_orders
