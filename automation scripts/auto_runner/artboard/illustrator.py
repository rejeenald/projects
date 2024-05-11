import logging, os, time
import pandas as pd
import psutil
import subprocess
from win32com.client import constants
from win32com.client import CoClassBaseClass
import shutil
import win32com.client.CLSIDToClass, pythoncom, pywintypes
import win32com

SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")

class Illustrator():
    def __init__(self):
        logging.info("===============Illustrator===============")
        try:
            logging.debug("Opening Adobe Illustrator..")
            self.ai = win32com.client.gencache.EnsureDispatch('Illustrator.Application')
        except AttributeError as e:
            logging.debug(f"AttributeError: {e}")
            f_loc = r'C:\Users\automation\AppData\Local\Temp\gen_py'
            shutil.rmtree(f_loc)
            # Path.rmdir(f_loc)
            self.ai = win32com.client.gencache.EnsureDispatch('Illustrator.Application')
        self.default = pythoncom.Empty
        self.dimension_file = SYNCPLICITY_ROOT + r'\Syncplicity\Production\_Personalized Prints\print\template dimensions.csv'

    def open(self, filename):
        self.docRef = self.ai.Open(filename)

    def find_layers_like(self, layer_sub_str, case_sensative = False):
        layers = []
        # if not self.docRef:
        #     raise ...
        for layer in self.docRef.Layers:
            if not case_sensative:
                if layer_sub_str.upper() in layer.Name.upper():
                    layers.append(layer.Name)
            else:
                if layer_sub_str in layer.Name:
                    layers.append(layer.Name)
        return layers

    def get_layer_by_name(self, name):
        for l in self.docRef.Layers:
            for g in l.GroupItems:
                print(g)
            # print(l.Name)
            # if l.Name == name:
            #     return l

    def import_image(self, image_file):
        img = self.docRef.PlacedItems.Add()
        try:
            img.File = image_file
        except Exception as e:
            print(image_file)
            print(e)
            raise e
        return img

    def get_template_info(self, sku):
        df_dim = pd.read_csv(self.dimension_file)
        mask_info = df_dim.loc[df_dim['sku'] == sku]
        print(mask_info)
        return {
            'template': mask_info['template'].values[0],
            'top': mask_info['top'].values[0],
            'left': mask_info['left'].values[0],
            'bottom': mask_info['bottom'].values[0],
            'right': mask_info['right'].values[0],
            # 'ink_top': mask_info['ink_top'].values[0],
            # 'ink_left': mask_info['ink_left'].values[0],
            # 'ink_height': mask_info['ink_height'].values[0],
            # 'ink_width': mask_info['ink_width'].values[0],
        }

    def eps_options(self):
        logging.debug("Illustrator eps options!!!")
        return win32com.client.gencache.EnsureDispatch('Illustrator.EPSSaveOptions')


    def close(self):
        self.docRef.Close(constants.aiDoNotSaveChanges)
        time.sleep(5)
        logging.info(f"Terminating the Adobe Illustrator process...")
        try:
            self._terminate_illustrator()
        except Exception as e:
            logging.warning("Failed to terminate the Adobe Illustrator!")

        time.sleep(5)

    @staticmethod
    def _terminate_illustrator() -> None:
        
        logging.info("Killing Illustrator.exe process...")
        for process in psutil.process_iter():
            try:
                if "Illustrator.exe" in process.name():
                    process.kill()
            except Exception as e:
                logging.warning("Failed to kill the Adobe Illustrator!")
                pass
