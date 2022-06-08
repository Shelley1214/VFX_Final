import numpy as np
import cv2 as cv
from PIL import Image
import scipy.ndimage
from wrap import MVC

class Cloning:

    def __init__(self):
        self.source_image = []
        self.target_image = []
        self.trimap_image = []
        self.pts = []
        self.alpha = []

    # ref: https://github.com/Tony-Tseng/vfx_final_project
    def mvc_cloning(self, center,  mask=[]):
        source_image = np.array(self.source_image, dtype=np.float64)
        target_image = np.array(self.target_image, dtype=np.float64)

        src_mask = mask.copy()
        if mask == []:
            src_mask = np.zeros_like(source_image, dtype=np.uint8)
            cv.fillPoly(src_mask,  [np.array(self.pts)], (255, 255, 255))
            src_mask = src_mask[:,:,0]
       
        # boundary and cloning area
        boundary = cv.findContours(src_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2][0].reshape(-1,2)
        boundary = np.append( boundary, [boundary[0,:]], axis=0)
        src_mask [ boundary[:,1] , boundary[:,0] ] = 0
        inner_pixel = np.argwhere(src_mask == 255)
        
        # boundary difference
        offset =  center -  (np.mean(boundary, axis=0, dtype=np.int))
        target_boundary = boundary + offset
        diff = target_image[target_boundary[:-1,1], target_boundary[:-1,0],:] - source_image[boundary[:-1,1], boundary[:-1,0],:]
        
        # MVC
        R= MVC(boundary, inner_pixel, diff, 3)
        R = R.reshape((inner_pixel.shape[0],3))

        # interpolant
        index = offset + inner_pixel[:, [1,0]]
        target_image[ index[:,1], index[:,0], : ] = source_image[ inner_pixel[:,0], inner_pixel[:,1], : ] + R
        target_image = np.clip(0, target_image, 255)

        return target_image.astype(np.uint8)

    def boundary(self,boundary):
        width = boundary[:,0]
        height = boundary[:,1]
        if  any(width > self.target.width()) or any(width < 0) or any(height> self.target.height() )or any(height < 0):
            return True
        return False

    # ref: https://github.com/MarcoForte/poisson-matting
    def matting(self,center):

        source_image = np.array(self.source_image, dtype=np.uint8)
        target_image = np.array(self.target_image, dtype=np.uint8)

        gray_img = cv.cvtColor(source_image, cv.COLOR_RGB2GRAY) 
        trimap_image = cv.cvtColor( np.array(self.trimap_image, dtype=np.uint8), cv.COLOR_RGB2GRAY)
        mask = np.zeros_like(gray_img, dtype=np.uint8) + 255
        mask [ trimap_image == 0 ] = 0
        boundary = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2][0].reshape(-1,2)
        trimap_image [ boundary[:,1] , boundary[:,0] ] = 0
        boundary = np.append( boundary, [boundary[0,:]], axis=0)
        offset =  center -  (np.mean(boundary, axis=0, dtype=np.int))
        
        if self.boundary( (boundary + offset)):
            print("position out of range")
            return self.result

        fg = trimap_image == 255
        bg = trimap_image == 0
        unknown = True ^ np.logical_or(fg,bg)
        alphaEstimate = fg.astype(np.float64) + 0.5 * unknown

        # diff (Smooth F - B image)
        fg_img = gray_img.astype(np.float64)*fg
        bg_img = gray_img.astype(np.float64)*bg
        approx_bg = cv.inpaint(bg_img.astype(np.uint8),(unknown+fg).astype(np.uint8)*255,3,cv.INPAINT_TELEA).astype(np.float64)
        approx_fg = cv.inpaint(fg_img.astype(np.uint8),(unknown+bg).astype(np.uint8)*255,3,cv.INPAINT_TELEA).astype(np.float64)
        
        approx_diff = approx_fg - approx_bg
        approx_diff = scipy.ndimage.gaussian_filter(approx_diff, 0.9)

        I = gray_img.astype(np.float64) / approx_diff.astype(np.float64)
        diff = (alphaEstimate - I)[ boundary[:-1,1], boundary[:-1,0] ]

        # mvc
        inner_pixel = np.argwhere(unknown)
        R = MVC(boundary, inner_pixel, diff, 1)

        # interpolant
        alphaEstimate[ inner_pixel[:,0], inner_pixel[:,1] ] =  I[ inner_pixel[:,0], inner_pixel[:,1] ] + R
        alphaEstimate [ alphaEstimate > 0.95 ] = 1
        alphaEstimate [ alphaEstimate < 0.05] = 0
        if self.alpha == []:
            self.alpha =  alphaEstimate
            alpha =  Image.fromarray ( np.array(self.alpha*255).astype(np.uint8) )
            alpha.show() 

        matting_alpha = np.zeros_like(target_image, dtype=np.float64)
        matting_alpha[ offset[1] :offset[1]+source_image.shape[0] ,  offset[0] :offset[0]+source_image.shape[1] , :] =  (np.dstack((self.alpha, self.alpha, self.alpha)))

        result = self.mvc_cloning(center, mask)
        # tmp = Image.fromarray(result)
        # tmp.show()
        result = result * matting_alpha  + target_image * (1-matting_alpha)

        return Image.fromarray(result.astype(np.uint8))