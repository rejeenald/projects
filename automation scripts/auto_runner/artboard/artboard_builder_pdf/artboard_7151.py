import os
import csv
import traceback
from pathlib import Path
from pikepdf import Pdf, Rectangle, StreamDecodeLevel, ObjectStreamMode


PAGE_WIDTH = 1729.13
PAGE_HEIGHT = 1190.55

CENTER_POINTS = [
    (1415, 130.05), (875, 130.05), (335, 130.05),
    (1415, 436.05),  (875, 436.05),  (335, 436.05),
    (1415, 742.05),  (875, 742.05),  (335, 742.05),
    (1415, 1048.05),  (875, 1048.05),  (335, 1048.05)
]



class ArtboardBuilder7151:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.image_paths = self._load_image_paths()
        self.output_pdf = self._generate_output_pdf_name()

    def _load_image_paths(self):
        print("Read image paths from CSV starting from the second row.")
        image_paths = []
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0].strip():
                    image_paths.append(row[0].strip())
        return image_paths[:12]

    def _generate_output_pdf_name(self):
        filename = os.path.splitext(os.path.basename(self.csv_path))[0]
        return f"{filename}.pdf"

    def build_pdf(self):
        print("📄 Building output artboard from image list.")
        out_pdf = Pdf.new()
        dest_page = out_pdf.add_blank_page(page_size=(PAGE_WIDTH, PAGE_HEIGHT))

        for idx, (artfile_path, center) in enumerate(zip(self.image_paths, CENTER_POINTS)):
            ext = artfile_path.split(".")[-1]
            if ext == "pdf":
                self._process_artfile(artfile_path, center, dest_page)
            else:
                print(f"Artfile is not a pdf. Skipping: {artfile_path}")

        self._save_pdf(out_pdf)
        print(f"✅ PDF saved as '{self.output_pdf}'")

    def _process_artfile(self, artfile_path, center, dest_page):
        cx, cy = center
        print(f"center points: {center}")
        try:
            print(f"➡️  Importing: {artfile_path}")
            with Pdf.open(artfile_path) as src:
                src_page = src.pages[0]
                src_page.rotate(270, relative=True)

                w, h = self._get_rotated_dimensions(src_page)
                rect = self._calculate_position(cx, cy, w, h)

                dest_page.add_overlay(src_page, rect)
        except Exception as e:
            print(f"❌ Error processing '{artfile_path}': {e}")
            traceback.print_exc()

    def _get_rotated_dimensions(self, page):
        llx, lly, urx, ury = map(float, page.MediaBox)
        width = urx - llx
        height = ury - lly
        return height, width  # swapped due to rotation

    def _calculate_position(self, center_x, center_y, width, height):
        x0 = center_x - width / 2
        y0 = center_y - height / 2
        return Rectangle(x0, y0, x0 + width, y0 + height)

    def _save_pdf(self, pdf_obj):
        pdf_obj.save(
            self.output_pdf,
            force_version="1.6",
            linearize=True,
            stream_decode_level=StreamDecodeLevel.generalized,
            compress_streams=False,
            object_stream_mode=ObjectStreamMode.generate
        )



# Example usage
if __name__ == "__main__":
    # csv_file = r"/Users/joe/SyncDrive/Order Fulfillment/Custom Orders/Script Stuff/artboard_templates/joe_version_bg.csv"
    csv_file = r"C:\Users\automation\Syncplicity\Order Fulfillment\Custom Orders\Script Stuff\artboard_templates\2025-07-16-07-07-54--7151--1200x1200-130-2-0754_AUTO_.csv"
    builder = ArtboardBuilder(csv_file)
    builder.build_pdf()
