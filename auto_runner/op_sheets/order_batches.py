import datetime as dt
import logging
import pandas as pd
pd.options.mode.chained_assignment = None  
from time import sleep

try:
    from op_sheet_settings import SKU_GROUPINGS, OP_SHEET_SUFFIX, LIMIT_7151, LIMIT_6042, BATCHES
except:
    from .op_sheet_settings import SKU_GROUPINGS, OP_SHEET_SUFFIX, LIMIT_7151, LIMIT_6042, BATCHES

class OrderBatches:
    def __init__(self, artboard:pd.DataFrame, regular:bool) -> None:
        logging.info("===============OrderBatches===============")
        self.sku_batches = SKU_GROUPINGS.groupby(["group_number", "printer"])["family_sku"].apply(set).to_dict()
        logging.debug(f"sku batches: {self.sku_batches}")
        self.artboard = artboard
        self.regular = regular
        
    def _batch_orders(self) -> None:
        logging.info("Grouping orders by batch...")
        batches = {}
        batch_counter = 1
        for batch in self.sku_batches:
            printer = self.__set_printer(batch)
            orders_in_batch = self.artboard.loc[self.artboard["family_sku"].isin(self.sku_batches[batch])]
            if orders_in_batch.empty:
                continue

            logging.debug(f"Length of orders in the batch: {len(orders_in_batch.index)}")
            logging.debug(f"Orders in batch: {orders_in_batch}")
            
            row_count_limit = self._get_order_count_limit(printer=printer)
            split_grouped_orders = self._split_grouped_orders(orders_in_batch, row_count_limit)
            logging.info(f"Split grouped orders: {len(split_grouped_orders)}")
            if len(split_grouped_orders) > 1:
                logging.info(f"Found excess orders")

            logging.info(split_grouped_orders)
            for grouped_orders in split_grouped_orders:
                batch_number = f"batch_{str(batch_counter)}"
                logging.info(f"Populating for batch {batch_number}")
                batches, filename = self._populate_batch(batches=batches, batch_number=batch_number, grouped_orders=grouped_orders, printer=printer)
                grouped_orders.to_csv(f"{BATCHES}{filename}.csv")
                batch_counter += 1
                
                sleep(5)
        return batches

    def _split_grouped_orders(self, orders_in_batch:pd.DataFrame, row_count_limit:int):
        split_dfs = []
        orders_count = len(orders_in_batch)
        if orders_count == row_count_limit:
            split_dfs.append(orders_in_batch)
        else:
            extra = (orders_count % row_count_limit)
            if extra > 0:
                num_splits = (orders_count // row_count_limit) + 1
            else:
                num_splits = (orders_count // row_count_limit)
            logging.info(f"Need to split: row count limit is greater than the orders count: {orders_count}")
            logging.info(f"Number of splits: {num_splits}")

            start = 0
            for split in range(num_splits):
                end = start + row_count_limit
                logging.info(f"start: {start}")
                logging.info(f"end: {end}")
                if end < len(orders_in_batch):
                    sub_group = orders_in_batch[start:end]
                else:
                    logging.info(f"Exceeded index from length of dataframe.")
                    sub_group = orders_in_batch[start:]
                split_dfs.append(sub_group)
                start = end

                # sub_group.to_csv(f"split_{split}.csv")
            
        return split_dfs

    def __set_printer(self, batch):
        if self.regular:
            printer = batch[-1]
        else:
            printer = "7151"
        return str(printer)

    def _get_order_count_limit(self, printer:str) -> int:
        if printer == "7151":
            limit = LIMIT_7151
        else:
            limit = LIMIT_6042
        logging.info(f"Slot limit for printer {printer}: {limit}")
        return limit

    def _populate_batch(self, batches:dict, batch_number:str, grouped_orders:pd.DataFrame, printer:str) -> None:
        logging.debug(f"Populating batch with info of {batch_number}")
        batches[batch_number] = grouped_orders
        settings = self.__extract_settings_from_orders(batch=batches[batch_number], printer=printer)
        logging.debug(f"Settings: {settings}")
        batches[batch_number]["printer"] = str(printer)
        filename = self.__generate_filename(settings=settings)
        batches[batch_number]["filename"] = filename
        batches[batch_number]["op_sheet_top_left_detail"] = batches[batch_number]["filename"].apply(lambda fn: self.__construct_op_sheet_top_left_detail(filename=fn))
        batches[batch_number] = batches[batch_number].sort_values(by="Sort Sku")
        batches[batch_number]["Order - ItemID"] = batches[batch_number].apply(lambda order: str(int(order["Order - ItemID"])), axis=1)
        batches[batch_number]["Order - ID"] = batches[batch_number].apply(lambda order: str(int(order["Order - ID"])), axis=1)
        
        logging.debug(f"Filename: {batches[batch_number]['filename']}")
        return batches, filename

    def __construct_op_sheet_top_left_detail(self, filename:str) -> dict:
        after_printer_text = filename.split("--")[-1]
        top_left_detail = after_printer_text.replace("_AUTO_", "")
        return top_left_detail

    def __extract_settings_from_orders(self, batch, printer):
        logging.info("Extracting settings from orders...")
        # logging.debug(f"batch: {batch}")
        settings = {}
        settings["printer"] = f"-{printer}-"
        settings["print_settings"] = list(batch["Print Settings"].unique())
        settings["table_height"] = list(batch["Table Height"].unique())
        settings["trim"] = list(batch["Trim"].unique())
        return settings

    def __generate_filename(self, settings:dict) -> None:
        """
        Filename format: <YY-MM-DD-HH-MM-SS--PRINTER--PRINTER SETTING-TABLE HEIGHT-TRIM-MMSS_AUTO_>
        """
        logging.info(f"Generating the batch filename with these setting details: {settings}")
        date_time_now = dt.datetime.utcnow()
        date_time_str = date_time_now.strftime("%Y-%m-%d-%H-%M-%S")
        minute_and_seconds = self.__extract_minute_and_second_from_timestamp(date_time_now)
        settings = self.__combine_print_settings_for_filename__(settings)
        filename = "-".join([date_time_str, settings, minute_and_seconds]) + OP_SHEET_SUFFIX
        return filename

    def __combine_print_settings_for_filename__(self, settings) -> str:
        if len(settings.get("print_settings")) == 1 and len(settings.get("table_height")) == 1 and len(settings.get("trim")) == 1:
            if settings.get("trim")[0] == "Gloss" or settings.get("trim")[0] == "Dusk":
                return "-".join([settings.get("printer"), settings.get("print_settings")[0], str(int(settings.get("table_height")[0])), settings.get("trim")[0]])
            return "-".join([settings.get("printer"), settings.get("print_settings")[0], str(int(settings.get("table_height")[0])), str(int(settings.get("trim")[0]))])
        else:
            logging.warning("ERROR on print setting values!")
            return "ERROR on print setting values!"

    def __extract_minute_and_second_from_timestamp(self, date_time_now):
        seconds_str = str(date_time_now.second)
        if len(seconds_str) == 1:
            seconds_str = f"0{seconds_str}"
        
        minute_str = str(date_time_now.minute) 
        if len(minute_str) == 1:
            minute_str = f"0{minute_str}"

        minute_and_seconds = "".join([minute_str, seconds_str])
        return minute_and_seconds
    
    @property
    def batches(self) -> dict:
        try:
            return self._batch_orders()
        except Exception as e:
            logging.error(f"Failed to batch orders: {e}")
            return {}


    
# if __name__ == "__main__":
#     from settings import TO_PRINT_ARTBOARD
#     csv_gentr = OrderBatches(TO_PRINT_ARTBOARD)
#     csv_gentr.batches