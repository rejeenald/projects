import fitz  # PyMuPD
import logging
import os
import subprocess
import shutil

from .packing_slip_data import PackingSlipData
from .slip_template import SlipTemplate
from .slipper_settings import SLIP_DIR

class SlipPDFEditor:
    def __init__(self, order:dict=None, label_path:str=None, slip_filename:str=None):
        logging.info("==========================SlipPDFEditor==========================")
        self._select_packing_slip_template(order=order)
        self.label_pdf_path = label_path
        self.doc = fitz.open(self.template_path)
        self.packing_slip_path_editable = f"{SLIP_DIR}\{slip_filename}_editable.pdf"
        self.packing_slip_path = f"{SLIP_DIR}\{slip_filename}.pdf"
        self.data_to_add_to_slip = PackingSlipData(order=order)

    def _select_packing_slip_template(self, order:dict) -> None:
        slip_template = SlipTemplate()
        self.template_path = slip_template.select_template(order=order)

    def _fill_form_fields(self, data_dict):
        logging.info("Filling out pdf editable fields of the packing slip template...")
        for page in self.doc:
            widgets = page.widgets()
            if not widgets:
                logging.warning(f"There are no widgets!")
                continue
            for widget in widgets:
                field_name = widget.field_name
                if field_name in data_dict:
                    widget.field_value = str(data_dict[field_name])
                    widget.update()
            try:
                page.wrap_contents()
            except Exception as e:
                logging.error(f"Failed to wrap!: {e}")

    def _insert_label_image(self):
        logging.info("Inserting label to the packing slip...")
        if not self.label_pdf_path:
            return

        label_doc = fitz.open(self.label_pdf_path)
        label_page = label_doc[0]

        for page in self.doc:
            widgets = page.widgets()
            if not widgets:
                continue

            for widget in widgets:
                if widget.field_name == "label":
                    widget_rect = widget.rect
                    page.delete_widget(widget)

                    rotate_matrix = fitz.Matrix(5, 5).prerotate(-90)
                    rotated_pix = label_page.get_pixmap(matrix=rotate_matrix)

                    scale_w = widget_rect.width / rotated_pix.width
                    scale_h = widget_rect.height / rotated_pix.height
                    scale = min(scale_w, scale_h)

                    new_width = rotated_pix.width * scale
                    new_height = rotated_pix.height * scale

                    x0 = widget_rect.x0 + (widget_rect.width - new_width) / 2
                    y0 = widget_rect.y0 + (widget_rect.height - new_height) / 2
                    img_rect = fitz.Rect(x0, y0, x0 + new_width, y0 + new_height)

                    page.insert_image(img_rect, pixmap=rotated_pix, overlay=True)
                    
    def _save(self):
        self.doc.save(self.packing_slip_path_editable)
        logging.info(f"✅ Editable PDF saved to: {self.packing_slip_path_editable}")
        self.doc.close()
        
    def flatten_pdf_with_ghostscript(self, delete_original=True):
        # Try using common Ghostscript executable names (Windows/Linux)
        gs_commands = ["gswin64c", "gswin32c", "gs"]  # fallback list
        gs_executable = None

        for cmd in gs_commands:
            if shutil.which(cmd):
                gs_executable = cmd
                break

        if not gs_executable:
            raise EnvironmentError("Ghostscript not found. Please install it and add to PATH.")

        command = [
            gs_executable,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/prepress",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dPrinted=true",  # This helps flatten forms
            f"-sOutputFile={self.packing_slip_path}",
            self.packing_slip_path_editable,
        ]

        try:
            subprocess.run(command, check=True)
            print(f"✅ Flattened PDF saved to: {self.packing_slip_path}")
            if delete_original:
                os.remove(self.packing_slip_path_editable)
                print(f"🗑️ Deleted original input file: {self.packing_slip_path_editable}")
        except subprocess.CalledProcessError as e:
            print("❌ Ghostscript failed:", e)
            

        


    def create_slip(self):
        logging.info("Creating the label...")
        self._fill_form_fields(data_dict=self.data_to_add_to_slip.slip_data)
        self._insert_label_image()
        self._save()
        self.flatten_pdf_with_ghostscript()


# if __name__ == "__main__":
#     input_pdf = r"C:\Users\NOVA\Documents\smartish\auto_runner\op_sheets\label_maker\slipper\sample_templates\10.pdf"
#     output_pdf = r"C:\Users\NOVA\Documents\smartish\auto_runner\op_sheets\label_maker\slipper\sample_templates\10.pdf"


#     editor = SlipPDFEditor(input_pdf, output_pdf)
#     editor.create_slip()