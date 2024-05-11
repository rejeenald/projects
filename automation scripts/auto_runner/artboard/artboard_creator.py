import logging

from abc import abstractmethod
from time import sleep


class AIArtboardCreator:
    def __init__(self) -> None:
        pass
        
    def process_images(self, images, jigposition_x, jigposition_Y) -> None:
        counter = 0
        img_list = []
        for img in images:
            try:
                logging.debug(f"img: {img}")
                img_name = img
                img_name = self.__set_img_name(img_name=img_name)
                logging.debug(f"Setting to artboard...{img_name}")
                img = self.illz.import_image(img)
                logging.debug(f"Already set: {img}")
                img_list.append(img)
                logging.debug(f"Updated img_list: {img_list}")
                textLayer = self.__add_art_filename(img_name=img_name)
                logging.debug(f"Added text layer...")
                self._position_elements_to_jig_position(jigposition_x, jigposition_Y, counter, img, textLayer)
                logging.debug("Positioned the artowrk in the jig!")
            except:
                logging.warning(f"Artwork not existing! Check print path: {img_name}")

            counter += 1
            sleep(.1)

        return img_list

    def __set_img_name(self, img_name:str) -> str:
        print(f"img_name: {img_name}")
        return img_name.split("/")[-1]
   
    def __add_art_filename(self, img_name:str):
        textLayer = self.illz.docRef.TextFrames.Add()
        textLayer.Contents = img_name
        return textLayer

    def _position_elements_to_jig_position(self, jigposition_x, jigposition_y, counter, img, textLayer):
        imgLeft, imgTop, textLeft, textTop, imgxCenter, imgyCenter = self.__set_item_boundaries(img, textLayer)
        relativeXtext, relativeYtext = self.__caculate_delta_to_move_centerpoint_to_jig_position_relative_to_text(counter, jigposition_x, jigposition_y, textLeft, textTop)
        relativeX, relativeY = self.__caculate_delta_to_move_centerpoint_to_jig_position_relative_to_img(counter, jigposition_x, jigposition_y, imgLeft, imgTop, imgxCenter, imgyCenter)
        self.__move_artwork_to_jig_position(img, textLayer, relativeXtext, relativeYtext, relativeX, relativeY)

    @staticmethod
    def __set_item_boundaries(img, textLayer):
        # returns the distance from top and left of the artwork bounding box to the top of the artboard
        imgLeft = img.Left
        imgTop = img.Top
        textLeft = textLayer.Left
        textTop = textLayer.Top
        imgxCenter = img.Width / 2
        imgyCenter = img.Height / 2
        return imgLeft, imgTop, textLeft, textTop, imgxCenter, imgyCenter

    @staticmethod
    def __caculate_delta_to_move_centerpoint_to_jig_position_relative_to_text(counter, jigposition_x, jigposition_y, textLeft, textTop):
        relativeXtext = jigposition_x[counter] - textLeft
        relativeYtext = -jigposition_y[counter] - textTop
        return relativeXtext, relativeYtext

    @staticmethod
    def __caculate_delta_to_move_centerpoint_to_jig_position_relative_to_img(counter, jigposition_x, jigposition_y, imgLeft, imgTop, imgxCenter, imgyCenter):
        relativeX = (jigposition_x[counter] - imgLeft - imgxCenter)
        relativeY = (-jigposition_y[counter] - imgTop + imgyCenter)
        return relativeX, relativeY

    @staticmethod
    def __move_artwork_to_jig_position(img, textLayer, relativeXtext, relativeYtext, relativeX, relativeY):
        img.Translate(relativeX, relativeY)
        textLayer.Translate(relativeXtext, relativeYtext)
        img.Rotate(90)
    
    def hide_center_points(self) -> None:
        # hide centerpoints
        centerMarksLayer = self.illz.docRef.Layers('new center marks')
        centerMarksLayer.Locked = True
        centerMarksLayer.Visible = False

    def add_layer_containing_file_names(self) -> None:
        # Add a layer that contains all the file names
        textLayerSet = self.illz.docRef.Layers.Add()
        textLayerSet.Name = "File Names"
        return textLayerSet

    def move_text_items_to_new_text_layer(self, textLayerSet) -> None:
        artworkLayer = self.illz.docRef.Layers('artwork')
        numTextItems = len(artworkLayer.TextFrames)
        for i in range(numTextItems):
            artworkLayer.TextFrames.Item(1).Move(textLayerSet, 2)
    
    def hide_text_layer(self, textLayerSet) -> None:
        textLayerSet.Visible = False

    def embed_image(self, img_list) -> None:
        for img in img_list:
            test = img.Embed()

    def set_eps_filename(self, artboard_csv:str, destination_folder:str) -> str:
        logging.info("Setting eps filename...")
        fname = artboard_csv.split('\\')[-1].split('/')[-1]
        fname = fname.replace('.csv', '.eps')
        save_name = destination_folder + '\\' + fname
        logging.info(f"Save filename: {save_name}")
        return save_name

    def set_eps_options(self):
        logging.info("Setting eps options...")
        eps_options = self.illz.eps_options()
        logging.debug("CMYKPostScript")
        eps_options.CMYKPostScript = True
        logging.debug("EmbedAllFonts")
        eps_options.EmbedAllFonts = True
        logging.debug("EmbedLinkedFiles")
        eps_options.EmbedLinkedFiles = True
        logging.debug("IncludeDocumentThumbnails")
        eps_options.IncludeDocumentThumbnails = False
        logging.debug("SaveMultipleArtboards")
        eps_options.SaveMultipleArtboards = True
        logging.debug("ArtboardRange")
        eps_options.ArtboardRange = "1"
        logging.debug("Preview")
        eps_options.Preview = 1
        logging.info(f"eps options all set!")
        return eps_options