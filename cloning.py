import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from PIL import Image
import triangle as  tr
import matplotlib.tri as mtri
import scipy.ndimage
from wrap import MVC


class Cloning:

    def __init__(self):
        self.source_image = []
        self.target_image = []
        self.trimap_image = []
        self.pts = np.empty((0, 2), dtype=int)

    def in_image(self, boundary, shape):
        index = np.where((boundary[:, 1] >= 0) & (boundary[:, 0] >= 0) & (boundary[:, 1] < shape[0]) & (boundary[:, 0] < shape[1]))[0]
        return index

    def seamlessClone(self, center, mask=[]):

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

        in_image_idx = self.in_image(target_boundary, target_image.shape)
        target_boundary = target_boundary[in_image_idx]
        boundary = boundary[in_image_idx]
        diff = target_image[target_boundary[:,1], target_boundary[:,0],:] - source_image[boundary[:,1], boundary[:,0],:]

        # MVC
        R= MVC(boundary, inner_pixel, diff, 3)
        R = R.reshape((inner_pixel.shape[0],3))
        
        # interpolant
        index = offset + inner_pixel[:, [1,0]]
        in_image_idx = self.in_image(index, target_image.shape)
        index = index[in_image_idx]
        inner_pixel = inner_pixel[in_image_idx]
        R = R[in_image_idx]

        target_image[ index[:,1], index[:,0], : ] = source_image[ inner_pixel[:,0], inner_pixel[:,1], : ] + R
        target_image = np.clip(0, target_image, 255)

        return target_image.astype(np.uint8)

    
    def seamlessClone_mesh(self, center, mask=[]):

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

        # generate adaptive mesh
        inner_boundary = cv.findContours(src_mask.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2][0].reshape(-1, 2)
        patch = {}
        patch['vertices'] = inner_boundary
        patch['segments'] = [[i, (i+1)%len(inner_boundary)] for i in range(len(inner_boundary))]
        mesh = tr.triangulate(patch, 'pqD')
        
        inner_mesh = mesh['vertices'][:, [1, 0]].astype(int)

        # boundary difference
        offset =  center - (np.mean(boundary, axis=0, dtype=np.int))
        target_boundary = boundary + offset

        in_image_idx = self.in_image(target_boundary, target_image.shape)
        target_boundary = target_boundary[in_image_idx]
        boundary = boundary[in_image_idx]

        diff = target_image[target_boundary[:, 1], target_boundary[:, 0], :] - source_image[boundary[:, 1], boundary[:, 0], :]

        R = MVC(boundary, inner_mesh, diff, 3)
        R = R.reshape((inner_mesh.shape[0],3))
        
        # interpolant
        triang = mtri.Triangulation(inner_mesh[:, 1], inner_mesh[:, 0])
        
        index = offset + inner_pixel[:, [1,0]]
        in_image_idx = self.in_image(index, target_image.shape)
        index = index[in_image_idx]
        inner_pixel = inner_pixel[in_image_idx]

        result = []
        for rgb in range(3):
            interpolator = mtri.LinearTriInterpolator(triang, R[:, rgb])
            Xi, Yi = np.meshgrid(np.array(range(source_image.shape[1])), np.array(range(source_image.shape[0])))
            value = interpolator(Xi, Yi)
            result.append(value[inner_pixel[:,0], inner_pixel[:,1]])
        result = np.array(result).T

        target_image[ index[:,1], index[:,0], : ] = source_image[ inner_pixel[:,0], inner_pixel[:,1], : ] + result
        target_image = np.clip(0, target_image, 255)

        return target_image.astype(np.uint8)


    def OpenCV_Cloning(self, center):

        source_image = np.array(self.source_image, dtype=np.uint8)
        target_image = np.array(self.target_image, dtype=np.uint8)
        # src_shape = np.array(source_image.shape[:2])
        # trg_shape = np.array(target_image.shape[:2])

        # min_x, min_y = np.maximum(src_shape / 2 - center[[1, 0]], 0).astype(int)
        # max_x, max_y = np.minimum(src_shape / 2 - center[[1, 0]] + trg_shape, src_shape).astype(int)

        src_mask = np.zeros_like(source_image)
        cv.fillPoly(src_mask,  [np.array(self.pts)], (255, 255, 255))
        # src_mask = src_mask[min_x:max_x, min_y:max_y]
        # source_image = source_image[min_x:max_x, min_y:max_y]

        # center = center + [(src_shape[1] - max_y  + min_y) // 2, (src_shape[0] - max_x  + min_x) // 2]
        # print("min", min_x, min_y, max_x, max_y)
        # print("center", center)

        result = cv.seamlessClone( source_image, target_image, src_mask, center, cv.NORMAL_CLONE) 
        # cv.circle(result, center, 2, [255, 0, 0], 5)
        return result       


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
        alpha =  alphaEstimate

        # matting_cloning
        result = self.seamlessClone_mesh(center, mask)

        inner_pixel = np.argwhere(mask == 255)
        index = offset + inner_pixel[:, [1,0]]
        in_image_idx = self.in_image(index, target_image.shape)
        index = index[in_image_idx]
        inner_pixel = inner_pixel[in_image_idx]
        matting_alpha = np.zeros_like(target_image, dtype=np.float64)
        matting_alpha[ index[:,1], index[:,0], : ] = np.dstack((alpha, alpha, alpha))[ inner_pixel[:,0], inner_pixel[:,1], : ]

        result = result * matting_alpha  + target_image * (1-matting_alpha)

        return Image.fromarray(result.astype(np.uint8))