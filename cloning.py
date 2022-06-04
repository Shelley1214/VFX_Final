import numpy as np
import cv2 as cv
from PIL import Image
import matplotlib.pyplot as plt

from scipy.spatial import Delaunay
import triangle as  tr
class Cloning:

    def __init__(self):
        self.source_image = []
        self.target_image = []
        self.pts = []

    # ref: https://github.com/Tony-Tseng/vfx_final_project
    def seamlessClone(self, center):

        source_image = np.array(self.source_image, dtype=np.float64)
        target_image = np.array(self.target_image, dtype=np.float64)
        src_mask = np.zeros_like(source_image, dtype=np.uint8)
        cv.fillPoly(src_mask,  [np.array(self.pts)], (255, 255, 255))
        src_mask = src_mask[:,:,0]
       
        # boundary and cloning area
        boundary = cv.findContours(src_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2][0].reshape(-1,2)
        boundary = np.append( boundary, [boundary[0,:]], axis=0)
        src_mask [ boundary[:,1] , boundary[:,0] ] = 0
        inner_pixel = np.argwhere(src_mask == 255)
        
        # MVC
        Lambda = np.zeros(( inner_pixel.shape[0], boundary.shape[0]-1))
        for i, (r, c) in enumerate(inner_pixel):

            vec =  boundary - [c, r] 
            a_vec = vec [0:-1, :]
            b_vec = vec [1:,:]
            cosine_angle = np.sum(a_vec*b_vec, axis=1) / (np.linalg.norm(a_vec,axis=1) * np.linalg.norm(b_vec,axis=1))
            cosine_angle = np.clip(-1,cosine_angle,1)
            tan_val = np.tan(np.arccos(cosine_angle)/2)

            a_tan = np.r_[tan_val[-1], tan_val[0:-1]]
            b_tan = tan_val
            w = (a_tan + b_tan) / np.linalg.norm(a_vec, axis=1)
            Lambda[i, :] = w
        Lambda /= Lambda.sum(axis=1, keepdims=True)

        # boundary difference
        offset =  center -  (np.mean(boundary, axis=0, dtype=np.int))
        target_boundary = boundary + offset
        diff = target_image[target_boundary[:-1,1], target_boundary[:-1,0],:] - source_image[boundary[:-1,1], boundary[:-1,0],:]

        # interpolant
        index = offset + inner_pixel[:, [1,0]]
        R = np.dot(Lambda, diff)
        target_image[ index[:,1], index[:,0], : ] = source_image[ inner_pixel[:,0], inner_pixel[:,1], : ] + R
        target_image = np.clip(0, target_image, 255)

        return target_image.astype(np.uint8)


    def OpenCV_Cloning(self, center):

        source_image = np.array(self.source_image, dtype=np.uint8)
        target_image = np.array(self.target_image, dtype=np.uint8)
        src_mask = np.zeros_like(source_image)
        cv.fillPoly(src_mask,  [np.array(self.pts)], (255, 255, 255))
        result = cv.seamlessClone( source_image, target_image, src_mask, center, cv.NORMAL_CLONE)       
        # cv.fillPoly(src_mask,  [pts], (1, 1, 1))
        # src_mask =  Image.fromarray ( src_mask * source_image)
        # src_mask.show()