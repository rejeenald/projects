import datetime as dt
import logging
from random import randint
import pandas as pd
from exceptions import IndexOutOfRangeException, UnknownError
from data_extractor import DataExtractor
from order_partitioner import OrderPartitioner
from paid_orders import PaidOrders
from settings import *
from shipby import ShipByOrders
from ssapi.api import ShipStation
from time import sleep

class SSDataPuller:
    def __init__(self) -> None:
        logging.info(f"Data Puller PRODUCTION DATA: {PRODUCTION_DATA}")
        logging.info(f"Data Puller PRODUCTION: {PRODUCTION}")
        logging.info(f"Initiating ShipStation...")
        self.ss_api = ShipStation(auth_key=SHIPSTATION_KEY, auth_secret=SHIPSTATION_SECRET)
        self.data_extractor = DataExtractor()
        self.order_paritioner = OrderPartitioner()
        
    def save_to_csv_ss_data(self) -> pd.DataFrame:
        orders = self._pull_orders_from_ss()
        if orders:
            orders = self._extract_data(orders)
            self.order_paritioner.partition_orders(orders)
            self._save_to_csv()
            self._concatenate_orders_to_historical_reports()
            # self.tag_items_in_ss() # uncomment this when OF team requires the PrintQueue tag (yellow orange tag)
        else:
            logging.warning(f"No orders collected: {orders}")

    def _pull_orders_from_ss(self) -> dict:
        pages = self._get_number_of_pages()
        orders = self._get_all_orders_from_all_pages(pages=pages)
        if SHIPBY_DATE:
            logging.info(f"Limiting to just shipbys: SHIPBYS: {SHIPBY_DATE}")
            orders = self._get_shipby_today_orders(orders=orders)
            orders = self._get_paid_orders_only(orders=orders)
        else:
            logging.info(f"All orders - not just shipbys today!: SHIPBYS: {SHIPBY_DATE}")
        return orders

    def _extract_data(self, orders):
        self.data_extractor.extract_data(orders=orders)
        orders = self.data_extractor.orders
        return orders

    def _get_number_of_pages(self) -> int:
        logging.info(f"Getting the number of pages of total orders...")
        try:
            pages = self.ss_api.get_order_list(create_date_start=START_TIME, page_size=MAX_PAGE_SIZE)["pages"]
            logging.debug(f"Pages: {pages}")
        except IndexOutOfRangeException as e:
            logging.warning(f"Request failed to pull list of orders in ShipStation. \n {e}")
            logging.info(f"Retrying failed requests...")
            pages = self._get_number_of_pages()
        except UnknownError as e:
            logging.error(f"Unknown error. Cannot retry requests.\n {e}")     
            pages = 0
        
        return int(pages)
    
    def _get_all_orders_from_all_pages(self, pages:int) -> list:
        logging.info(f"Getting all orders from all pages of orders...")
        orders = []
        for page in range(1, pages + 1):
            if PRODUCTION_DATA:
                ss_order = self.ss_api.get_order_list(order_date_start=START_TIME, page_size=MAX_PAGE_SIZE, page=page)
            else:
                ss_order = self.ss_api.get_order_list(order_date_start=START_TIME, page_size=MAX_PAGE_SIZE, page=page, store_id=405182)
            orders += ss_order["orders"]
            sleep_time = randint(1,5)
            logging.info(f"Sleeping for {sleep_time}")
            sleep(sleep_time)
        logging.debug(f"All orders (including canceled and shipped): {len(orders)}")
        return orders

    def _get_shipby_today_orders(self, orders:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Getting orders to be shipped today only...")
        shipby = ShipByOrders(orders=orders)
        return shipby.shipby_today_orders

    def _get_paid_orders_only(self, orders:pd.DataFrame) -> dict:
        logging.info(f"Getting paid orders only...")
        paid_orders = PaidOrders(orders=orders)
        return paid_orders.paid_orders

    def _save_to_csv(self) -> None:
        logging.info(f"Saving ShipStation data for {DATE_NOW}")
        self.order_paritioner.cleaned_ss_orders.to_csv(ORDERS, index=False, encoding="utf-8")
        self.order_paritioner.cleaned_ss_orders.to_csv(ORDERS_BACKUP, index=False, encoding="utf-8")
        self.order_paritioner.canceled_ss_orders.to_csv(CANCELLED_ORDERS, index=False, encoding="utf-8")
        self.order_paritioner.shipped_ss_orders.to_csv(SHIPPED_ORDERS, index=False, encoding="utf-8")
        self.order_paritioner.test_ss_orders.to_csv(TEST_ORDERS, index=False, encoding="utf-8")
        self.order_paritioner.persy_ss_orders.to_csv(PERSY_ORDERS, index=False, encoding="utf-8")

    def _concatenate_orders_to_historical_reports(self) -> None:
        try:
            logging.info(f"Adding to historical records the canceled orders... ")
            self.order_paritioner.canceled_ss_orders.to_csv(HISTORICAL_RECORDS_CANCELED_ORDERS, mode='a', index=False, header=False)
        except Exception as e:
            logging.error(f"An error occurred while concatenating canceled orders to historical reports: {e}")

        try:
            logging.info(f"Adding to historical records the shipped orders... ")
            self.order_paritioner.shipped_ss_orders.to_csv(HISTORICAL_RECORDS_SHIPPED_ORDERS, mode='a', index=False, header=False)
        except Exception as e:
            logging.error(f"An error occurred while concatenating shipped orders to historical reports: {e}")

    def tag_items_in_ss(self) -> None:
        logging.info("Tagging items in ShipStation...")
        orders = self.order_paritioner.clean_orders.to_dict('records')
        order_counter = 1
        for order in orders:
            logging.debug(f"['tag_items']: orderId: {order['orderId']}")
            response = self.ss_api.add_tag(order['orderId'], PRINT_QUEUE_TAG)
            logging.debug(f"['tag_items']: response: {response}")
            if order_counter >= DELAY_THRESHOLD:
                logging.info(f"20 orders tagged. Sleeping for 20 seconds.")
                sleep(20)
            else:
                sleep_time = randint(1,5)
                logging.debug(f"Sleeping for {sleep_time}")
                sleep(sleep_time)
            order_counter += 1