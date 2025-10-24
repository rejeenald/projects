import logging
import sys

from .directory_cleaner import DirectoryCleaner
from .doc_merger import DocumentMerger
from .warning_document_creator import CreateWarningDocument

from ..json_builder.json_builder import JSONBuilder
from ..slipper.slip_generator import SlipGenerator


class LabelMakerExecuter:
    def __init__(self, sys_argv:list, run_in_console:bool=True) -> None:
        logging.info("===============LabelMakerExecuter===============")
        logging.info(f"paths: {sys.path}")
        self.sys_argv = sys_argv
        logging.info("Checking if work dirs are empty...")
        self.__cleanup_storage_directories()
        self.run_in_console = run_in_console

    @staticmethod
    def __cleanup_storage_directories(conf_files:bool=False) -> None:
        logging.info(f"Cleaning up the directories first...")
        cleaner = DirectoryCleaner()
        cleaner.clean_confirmation_files_dir(conf_files=conf_files)
        cleaner.clean_label_dir()
        cleaner.clean_slip_dir()
        
    def execute_label_maker(self) -> None:
        logging.info(f"Executing Label Maker!")
        try:
            return self._execute_the_label_maker_process()
        except Exception as e:
            logging.critical("Error making labels: {}.".format(str(e)))
            return False        

    def _execute_the_label_maker_process(self) -> None:
        logging.info(f"Executing label maker script...")
        pdf_name, orders = self.__parse_orders_from_sys_arguments(self.sys_argv)
        logging.info(f"Processing for {pdf_name} containing orders {orders}")
        order_dict, unverified = self.__build_json(orders=orders, pdf_name=pdf_name)
        logging.info("Collect orders after generated slips...")
        no_slip_orders, slip_already_created = self.__collect_orders_after_generated_slips(order_dict=order_dict)
        logging.info("Execute: creating warning document...")
        self.__create_warning_documents(unverified=unverified, no_slip_orders=no_slip_orders, slip_already_created=slip_already_created)
        logging.info("Execute: merging labels...")
        self.__merge_labels(pdf_name)
        logging.info("Cleaning storage directories...")
        return True

    def __create_warning_documents(self, unverified:list=[], no_slip_orders:list=[], slip_already_created:list=[]) -> None:
        logging.info(f"Creating a warning document if there's any orders to add!")
        print("Creating a warning document if there's any orders to add!")
        cwd = CreateWarningDocument(unverified=unverified, no_slip_orders=no_slip_orders, slip_already_created=slip_already_created)
        cwd.create_warning_document()

    def __parse_orders_from_sys_arguments(self, argv:list) -> (str, list):
        logging.info(f"Parsing orders from passed system arguments: {argv}")
        orders, pdf_name = self.___extract_argvs(argv)
        if len(orders) == 0:
            logging.critical("No order numbers provided for labels!")
            sys.exit(1)
        return pdf_name, orders

    def ___extract_argvs(self, argv):
        if self.run_in_console:
            orders = [int(x) for x in argv[2:]]
            pdf_name = argv[1]
        else:
            orders = [int(x) for x in argv[1:]]
            pdf_name = argv[0]
            
        return orders,pdf_name

    def __build_json(self, orders:list, pdf_name:str) -> (dict, dict):
        logging.info("Utilizing JSONBuilder...")
        logging.info(f"Building JSON data for these orders: {orders}")
        jb = JSONBuilder(pdf_name=pdf_name)
        jb.build_json(orders_id=orders)
        order_dict = jb.order_dict_with_unships
        unverified_orders = jb.unverified_orders
        return order_dict, unverified_orders
    
    def __collect_orders_after_generated_slips(self, order_dict:dict) -> list:
        logging.info(f"Creating labels and then returning orders with no slips or slips already created...")
        sg = SlipGenerator(order_dict=order_dict)
        sg.generate_slips_to_slip_dir()
        return sg.no_slip_orders, sg.slip_already_created

    def __merge_labels(self, pdf_name:str='') -> None:
        dm = DocumentMerger(pdf_name=pdf_name)
        try:
            logging.info("Tyring to merge documents...")
            dm.merge_documents()
        except PermissionError:
            logging.critical("Did not have permission to write to the file. Please close all pdfs and pull these labels manually.")
        except Exception as e:
            logging.critical(f"Failed to merge labels, retrying: {e}")
            dm.merge_documents()