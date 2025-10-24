import logging
from PIL import Image, ImageDraw, ImageFont
from .base_settings import SLIP_DIR, TOOLS_DIR

class CreateWarningDocument:
    def __init__(self, unverified:list=[], no_slip_orders:list=[], slip_already_created:list=[]) -> None:
        logging.info("===============CreateWarningDocument===============")
        self.unverified = unverified
        self.no_slip_orders = no_slip_orders
        self.slip_already_created = slip_already_created
        self.line_height = 26
        self.warning_font = ImageFont.truetype(TOOLS_DIR + f"\\RobotoCondensed-Bold.ttf", 64)
        self.body_font = ImageFont.truetype(TOOLS_DIR + f"\\RobotoCondensed-Regular.ttf", self.line_height - 2)
        self.main_img = Image.new('RGB', size=(1240, 1754), color='white')
        self.draw = ImageDraw.Draw(self.main_img)
        self.draw.rectangle([100, 100, 1040, 248], fill='red')
        self.draw.text((42, 105), "WARNING WARNING WARNING WARNING", font=self.warning_font)
        self.draw.text((77, 175), "WARNING WARNING WARNING WARNING", font=self.warning_font)
        self.start = 258

    def create_warning_document(self) -> None:
        logging.info(f"Creating warning document...")
        if self._has_warning_data_to_add():
            self._add_unverified_orders()
            self._add_no_slip_orders()
            self._add_slip_already_created()
            self._save_warning_document()
    
    def _has_warning_data_to_add(self) -> bool:
        logging.info("Checking if there is warning data to add!")
        vrfd = self.__has_unverified()
        nso = self.__has_no_slip_orders()
        slc = self.__has_slip_already_created()
        has_warning_data = (vrfd | nso | slc)
        logging.info(f"Has warning data to add: {has_warning_data}")
        return has_warning_data
        
    def _save_warning_document(self) -> None:
        filename = f"{SLIP_DIR}\\0.pdf"
        self.main_img.save(filename, dpi=(150, 150), quality=95)
        logging.info(f"['warning document creator']: Saved the warning document: {filename}")
    
    def _add_unverified_orders(self) -> None:
        if self.__has_unverified():
            logging.info(f"['warning document creator']: Adding unverified orders: {self.unverified}")
            intro = ["The following labels had addresses that could not be verified by Shipstation.", 
                    "Please correct the address and manually print the labels."]
            unverified = [[x['orderNumber'], x['name']] for x in self.unverified]
            self.__draw_contents(intro=intro, orders=unverified)

    def _add_no_slip_orders(self) -> None:
        if self.__has_no_slip_orders():
            logging.info(f"['warning document creator']: Adding no slip orders: {self.no_slip_orders}")
            intro = ["ShipStation did not generate and provide labels for these orders.", 
                    "You will need to pull their labels directly from shipstation.",
                    "Potential issue: ",
                    "1) ShipDate is set in past",
                    "2) No service code and package set in ShipStation ",
                    "3) Address not validated in ShipStation, but was marked validated in orders.csv",
                    "4) ShipStation Issue"]
            self.__draw_contents(intro=intro, orders=self.no_slip_orders)
            
    def _add_slip_already_created(self) -> None:
        if self.__has_slip_already_created():
            logging.info(f"['warning document creator']: Slip is already created: {self.slip_already_created}")
            intro = [f"These orders already have their slip created. Please check other op sheets for their slips!"]
            logging.info("Calling drawing contents method")
            self.__draw_contents(intro=intro, orders=self.slip_already_created)

    def __has_unverified(self) -> bool:
        logging.info("Checking for unverified addresses of orders...")
        return len(self.unverified) > 0

    def __has_no_slip_orders(self) -> bool:
        logging.info("Checking if no slip orders pulled from ShipStation...")
        return len(self.no_slip_orders) > 0

    def __has_slip_already_created(self) -> bool:
        logging.info("Checking whether slips for the order is already created...")
        return len(self.slip_already_created) > 0
    
    def __draw_contents(self, intro:str, orders:list) -> None:
        logging.info("drawing contents")
        logging.info("Drawing contents...")
        self.___draw_intro_text(intro=intro)
        self.___draw_order_details(orders=orders)

    def ___draw_intro_text(self, intro:str='') -> None:
        logging.info(f"Drawing intro: {len(intro)}")
        for i in range(len(intro)):
            logging.info(f"intro {i}: {intro[i]}")
            self.start += self.line_height 
            logging.info(f"start: {self.start}")
            self.draw.text((100, self.start), intro[i], font=self.body_font, fill="black")
            
        self.start += self.line_height * 2
        logging.info("Done drawing intro")

    def ___draw_order_details(self, orders:list=[]) -> None:
        logging.info(f"Drawing order details: {orders}")
        start = self.start
        for i in range(len(orders)):
            logging.debug(f"order: {orders[i]}")
            start += self.line_height
            logging.debug(f"start: {start}")
            cust_name = f"{orders[i][1]}"
            order_no = f"{orders[i][0]}"
            logging.debug(f"customer {cust_name}")
            self.draw.text((100, start), cust_name, font=self.body_font, fill="black")
            logging.debug(f"order number: {order_no}")
            self.draw.text((500, start), order_no, font=self.body_font, fill="black")
        
        logging.debug(f"Exited loop of orders...")
        self.start += self.line_height * 2
        logging.info("Done drawing order details")