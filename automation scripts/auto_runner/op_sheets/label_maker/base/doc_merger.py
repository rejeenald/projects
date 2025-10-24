import logging
import os
from PyPDF4 import PdfFileMerger, PdfFileReader

from .base_settings import SLIP_DIR, OPERATOR_SHEET_DIR

class DocumentMerger:
    def __init__(self, pdf_name:str='') -> None:
        logging.info("===============DocumentMerger===============")
        self.filename = pdf_name.split("\\")[-1]
        self.pdfs = self.__retrieve_pdfs_in_slip()
        self.merger = PdfFileMerger(strict=False)
        self.pick_sheet = OPERATOR_SHEET_DIR+ f"{self.filename}.pdf"
        logging.info(f"op sheet: {self.pick_sheet}")
        logging.info(f"pdfs: {self.pdfs}")
        
    def __retrieve_pdfs_in_slip(self) -> list:
        return [f"{SLIP_DIR}\\{pdf}" for pdf in os.listdir(SLIP_DIR) if pdf.endswith('.pdf')]

    def merge_documents(self) -> None:
        logging.info("merging documents method now...")
        self._merge_warning_document()
        logging.info("merged warning document")
        self._merge_non_preprint()
        logging.info("merged non prelogging.infos")
        self._merge_valid_pdfs()
        logging.info("merged valid pdfs")
        self._write_merged_pdf_to_operator_sheet()
        logging.info("done  writing of merged pdf to op sheet ")
        self.merger.close()

    def _merge_warning_document(self) -> None:
        if len(self.pdfs) >= 1 and self.pdfs[0] == f"{SLIP_DIR}\\0.pdf":
            logging.info(f"Warning document found. Merging and then deleting it after merging...")
            self.merger.append(PdfFileReader(self.pdfs[0], strict=False), 'rb')
            del self.pdfs[0]
        else:
            logging.info("No Warning document. yay!")

    def _merge_non_preprint(self) -> None:
        if "Preprint" not in self.filename:
            logging.info(f"File is not a Preprint.")
            self.merger.append(PdfFileReader(self.pick_sheet, strict=False), 'rb')
        else:
            logging.info("A prelogging.info. Ignoring it!")

    def _merge_valid_pdfs(self) -> None:
        logging.info(f"Merging all valid pdfs: {self.pdfs}")
        for pdf in self.pdfs:
            logging.info(f"pdf: {pdf}")
            self.merger.append(PdfFileReader(pdf, strict=False), 'rb')

    def _write_merged_pdf_to_operator_sheet(self) -> None:
        logging.info("Writing merged pdf to a file")
        with open(self.pick_sheet, 'wb') as f:
            logging.info(f"operator sheet: {f}")
            self.merger.write(f)
    



    

    

