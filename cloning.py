import numpy as np
import cv2 as cv
from PIL import Image


class Cloning:

    def seamlessClone(self, source_image, target_image, pts, center):

        src_mask = np.zeros_like(source_image)
        cv.fillPoly(src_mask,  [pts], (255, 255, 255))
        result = cv.seamlessClone( source_image, target_image, src_mask, center, cv.NORMAL_CLONE)
        
        # cv.fillPoly(src_mask,  [pts], (1, 1, 1))
        # src_mask =  Image.fromarray ( src_mask * source_image)
        # src_mask.show()
        return result