import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

import triangle as  tr
import matplotlib.tri as mtri

class Cloning:

    def __init__(self):
        self.source_image = []
        self.target_image = []
        self.pts = []

    def in_image(self, boundary, shape):
        index = np.where((boundary[:, 1] >= 0) & (boundary[:, 0] >= 0) & (boundary[:, 1] < shape[0]) & (boundary[:, 0] < shape[1]))[0]
        return index

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
            w /= np.sum(w)
            Lambda[i, :] = w

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

    
    def seamlessClone_mesh(self, center):

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

        # generate adaptive mesh
        inner_boundary = cv.findContours(src_mask.astype(np.uint8), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2][0].reshape(-1, 2)
        patch = {}
        patch['vertices'] = inner_boundary
        patch['segments'] = [[i, (i+1)%len(inner_boundary)] for i in range(len(inner_boundary))]
        mesh = tr.triangulate(patch, 'pqD')
        
        inner_mesh = mesh['vertices'][:, [1, 0]].astype(int)

        # MVC
        Lambda = np.zeros(( inner_mesh.shape[0], boundary.shape[0]))
        for i, (r, c) in enumerate(inner_mesh):
            vec =  boundary - [c, r] 
            a_vec = vec
            b_vec = np.vstack((vec[1:], vec[0]))
            cosine_angle = np.sum(a_vec*b_vec, axis=1) / (np.linalg.norm(a_vec,axis=1) * np.linalg.norm(b_vec,axis=1))
            cosine_angle = np.clip(-1,cosine_angle,1)
            tan_val = np.tan(np.arccos(cosine_angle)/2)

            a_tan = np.r_[tan_val[-1], tan_val[0:-1]]
            b_tan = tan_val
            w = (a_tan + b_tan) / np.linalg.norm(a_vec, axis=1)
            Lambda[i, :] = w
        Lambda /= Lambda.sum(axis=1, keepdims=True)

        # boundary difference
        offset =  center - (np.mean(boundary, axis=0, dtype=np.int))
        target_boundary = boundary + offset

        in_image_idx = self.in_image(target_boundary, target_image.shape)
        target_boundary = target_boundary[in_image_idx]
        boundary = boundary[in_image_idx]
        Lambda = Lambda[:, in_image_idx]

        diff = target_image[target_boundary[:, 1], target_boundary[:, 0], :] - source_image[boundary[:, 1], boundary[:, 0], :]

        # interpolant
        R = np.dot(Lambda, diff)
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