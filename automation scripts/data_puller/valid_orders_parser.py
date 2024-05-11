import logging
import pandas as pd
import re
from settings import OUTLIER

class ValidOrdersParsers:
    def __init__(self, orders: pd.DataFrame) -> None:
        self.__orders = orders

    def _parse_valid_orders(self, search_term:str="") -> pd.DataFrame:
        logging.info(f"Search Term: {search_term}")
        print(f"Search Term: {search_term}")
        valid_orders = self.__orders.query("sku != None ")
        valid_orders = valid_orders.query("'CD-FEATURED' not in sku")

        if search_term == "persy":
            logging.info(f"Getting persy orders...")
            valid_orders = valid_orders.query('store == 388704')
        else:
            if search_term != "":
                q = f"sku.str.contains('{search_term}', na=False)"
                valid_orders = valid_orders.query(q)

        return valid_orders

    @property
    def custom_orders(self) -> pd.DataFrame:
        co =  self._parse_valid_orders("CUSTOM")
        logging.info(f"Custom orders: {len(co)}")
        return co

    @property
    def zprint_orders(self) -> pd.DataFrame:
        zo = self._parse_valid_orders("[zZ]\\d{4}")
        logging.info(f"zPrint orders: {len(zo)}")
        return zo

    @property
    def featured_orders(self) -> pd.DataFrame:
        fo = self._parse_valid_orders("FEATURE")
        logging.info(f"Featured orders: {len(fo)}")
        return fo

    @property
    def outlier_orders(self) -> pd.DataFrame:
        initial_oo = self._parse_valid_orders()
        oo = []
        for outlier_sku in OUTLIER:
            logging.debug(f"Outlier SKU: {outlier_sku}")
            q = f"sku.str.contains('{outlier_sku}', na=False)"
            q_oo = initial_oo.query(q)
            if q_oo.any:
                oo.append(q_oo)
        logging.info(f"Outlier orders: {len(oo)}")
        return pd.concat(oo)
    
    @property
    def nmspink(self) -> pd.DataFrame:
        nmspink = self._parse_valid_orders("NMSPINK-ALL")
        logging.info(f"NMSPINK-ALL orders: {len(nmspink)}")
        nmspink["color"] = nmspink["color"].apply(lambda color: "Pinking Clearly")
        nmspink["design"] = nmspink["color"].apply(lambda color: "All Pink Everything")
        return nmspink

    @property
    def persy_orders(self) -> pd.DataFrame:
        persys = self._parse_valid_orders("persy")
        logging.info(f"Persy orders: {len(persys)}")
        return persys