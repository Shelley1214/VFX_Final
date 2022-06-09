import cv2
import numpy as np
from cloning import Cloning
from klt_utils import getFeatures, estimateAllTranslation, applyGeometricTransformation

def get_bbox(video_file, click_center):
    cap = cv2.VideoCapture(video_file)
    frame_num = 150#int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = np.empty((frame_num, ), dtype=np.ndarray)

    for i in range(frame_num):
        success, frames[i] = cap.read()
    
    cx = click_center[0]
    cy = click_center[1]
    
    bboxs = np.empty((frame_num,), dtype=np.ndarray)
    bboxs[0] = np.empty((4,2), dtype=float)
    bboxs[0] = np.array([[cx-50, cy-50],[cx+50, cy-50],[cx-50, cy+50],[cx+50, cy+50]]).astype(float)
    startXs, startYs = getFeatures(cv2.cvtColor( frames[0], cv2.COLOR_RGB2GRAY), bboxs[0])
    for i in range(1, frame_num):
       print('Processing Frame',i)
       newXs, newYs = estimateAllTranslation(startXs, startYs, frames[i-1], frames[i])
       Xs, Ys ,bboxs[i] = applyGeometricTransformation(startXs, startYs, newXs, newYs, bboxs[i-1])
       
       # update coordinates
       startXs = Xs
       startYs = Ys

       # update feature points as required
       n_features_left = np.sum(Xs!=-1)
       #print('# of Features: %d'%n_features_left)
       if n_features_left < 15:
           startXs,startYs = getFeatures(cv2.cvtColor(frames[i],cv2.COLOR_RGB2GRAY),bboxs[i])

    cap.release()
    return bboxs

def get_center(bbox):
    sx = int(bbox[0][0])
    sy = int(bbox[0][1])
    ex = int(bbox[3][0])
    ey = int(bbox[3][1])
    center_x = int((ex-sx)/2)+sx
    center_y = int((ey-sy)/2)+sy
    return (center_x, center_y)

def video_track(img, pts, video_file, click_center, mode):
    bbox = get_bbox(video_file, click_center)
    
    cap = cv2.VideoCapture(video_file)
    frame_num = 150#int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = np.empty((frame_num, ), dtype=np.ndarray)
    
    result = []
    for i in range(frame_num):
        succes, frame = cap.read()
        center = get_center(bbox[i])
        clone = Cloning(img, frame, np.array(pts))
        if mode == "cv2":
            clone_image = clone.OpenCV_Cloning(center)
        elif mode == "mvc":
            clone_image = clone.seamlessClone(center)
        else:
            clone_image = clone.seamlessClone_mesh(center)
        #cv2.imwrite("frame %d.jpeg" %i, clone_image)
        result.append(clone_image)
        img_h, img_w, _ = clone_image.shape
        size = (img_w, img_h)

    # Output frames to video
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'DIVX'), 40, size)
    for i in range(len(result)):
        out.write(result[i])
    out.release()
    print("Video is saved.")
    cv2.destroyAllWindows()
    cap.release()
