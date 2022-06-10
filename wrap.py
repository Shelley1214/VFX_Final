import ctypes 
import numpy as np

handle = ctypes.CDLL( "mvc.so")
handle.MVC_Function.argtypes = [ctypes.POINTER((ctypes.c_int)), (ctypes.POINTER(ctypes.c_int)), ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, ctypes.c_int]
handle.MVC_Function.restype =  ctypes.POINTER(ctypes.c_double)
handle.dealloc.argtypes = [ctypes.POINTER(ctypes.c_double)]

def MVC_Function(boundary, inner_pixel, diff, x, y, c):
    boundary = (ctypes.c_int * len(boundary))(*boundary)
    inner_pixel = (ctypes.c_int * len(inner_pixel))(*inner_pixel)
    diff = (ctypes.c_double * len(diff))(*diff)
    return handle.MVC_Function(boundary, inner_pixel, diff, x, y, c)   

def MVC(boundary, inner_pixel, diff, c):
    x, y  = inner_pixel.shape[0], boundary.shape[0]-1
    boundary = boundary.flatten()
    inner_pixel = inner_pixel.flatten()
    diff = diff.flatten()
    out_ptr = MVC_Function(boundary, inner_pixel, diff, x, y, c)
    out_mat = np.array(out_ptr[:x*c])
    handle.dealloc(out_ptr)
    return out_mat
