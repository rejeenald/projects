import logging
import os
import pandas as pd

from artboard.artboard_creator import AIArtboardCreator
from artboard.artboard_settings_6042 import JIGPOSITIONS_X_6042, JIGPOSITIONS_Y_6042, UP_JIG_6042, DESTINATION_FOLDER_6042, CSV_DIR, OLD_JOB_DIR
from artboard.illustrator import Illustrator

class AIArtboardCreator_6042(AIArtboardCreator):
    def __init__(self) -> None:
        super().__init__()
        logging.info("===============AIArtboardCreator_6042===============")

    def move_csv(self, csv_filename:str) -> None:
        logging.info(f"Moving eps to {csv_filename} to {OLD_JOB_DIR}")
        os.rename(CSV_DIR + csv_filename, OLD_JOB_DIR + csv_filename)

    def run_illustrator(self, artboard_csv:str) -> None:
        logging.info(f"Artboard: {artboard_csv}")
        df_images = pd.read_csv(artboard_csv)
        logging.info(f"df_images: {df_images}")
        images = df_images['URL'].tolist()
        logging.info(f"images: {images}")
        self.illz = Illustrator()
        logging.info(f"Initialized 'Illustrator'! Opening the jig now...")
        self.illz.open(UP_JIG_6042)
        logging.info(f"Jig opened: {UP_JIG_6042}")

        img_list = self.process_images(images, JIGPOSITIONS_X_6042, JIGPOSITIONS_Y_6042)
        logging.info(f"img_list: {img_list}")

        self.hide_center_points()
        logging.info("Hid center points!")

        logging.info("Setting text layers!")
        textLayerSet = self.add_layer_containing_file_names()
        self.move_text_items_to_new_text_layer(textLayerSet)
        self.hide_text_layer(textLayerSet)
        self.embed_image(img_list)

        logging.info("Setting eps filename and options!")
        eps_filename = self.set_eps_filename(artboard_csv, DESTINATION_FOLDER_6042)
        eps_options = self.set_eps_options()
        self.illz.docRef.SaveAs(SaveIn=eps_filename, Options=eps_options)
        self.illz.close()
        logging.info("Illustrator closed!")