import cv2
import numpy as np
from cloning import Cloning

def img_load(img_file):
    img = cv2.imread(img_file)
    h, w, _ = img.shape
    img = cv2.resize(img, (int(w/4), int(h/4)), interpolation=cv2.INTER_AREA)
    cv2.namedWindow('Image Selection', cv2.WINDOW_NORMAL)
    r = cv2.selectROI('Image Selection', img, True, False)
    img_roi = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    cv2.destroyWindow("Image Selection")
    cv2.imshow("img_r", img_roi)
    cv2.imwrite("img_r.png", img_roi)
    cv2.waitKey(0)
    return img_roi

def cornersGet_b(frame, bbox):
    feature_param = dict( maxCorners = 100, qualityLevel = 0.3, minDistance = 7, blockSize = 7)
    old_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    (xmin, ymin, boxw, boxh) = cv2.boundingRect(bbox.astype(int))
    old = old_gray[ymin:ymin+boxh, xmin:xmin+boxw]
    
    corners = cv2.goodFeaturesToTrack(old, mask = None, **feature_param)
    corners = np.int0(corners)
    result = []
    for i in corners:
        x, y = i.ravel()
        result.append((x+xmin, y+ymin))
        cv2.circle(frame,(x+xmin,y+ymin),2,(0,0,255),-1)
    cv2.imwrite('feature.jpg', frame)
    return np.array(result)

def cornersGet(frame):
    feature_param = dict( maxCorners = 100, qualityLevel = 0.3, minDistance = 7, blockSize = 7)
    old = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    corners = cv2.goodFeaturesToTrack(old, mask = None, **feature_param)
    corners = np.int0(corners)
    result = []
    for i in corners:
        x, y = i.ravel()
        result.append((x, y))
        cv2.circle(frame,(x,y),2,(0,0,255),-1)
    cv2.imwrite('feature1.jpg', frame)
    return np.array(result)

def video_track(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_num = 20#int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = np.empty((frame_num, ), dtype=np.ndarray)
    
    for i in range(frame_num):
        success, frames[i] = cap.read()
        #print('Read a new frame: ', i)
    
    bboxs = np.empty((frame_num, ), dtype=np.ndarray)
    ##############
    bboxs[0] = np.empty((4, 2), dtype=float)
    (xmin, ymin, boxw, boxh) = cv2.selectROI("Select Area", frames[0], True, False)
    cv2.destroyWindow("Select Area")
    bboxs[0] = np.array([[xmin,ymin],[xmin+boxw,ymin],[xmin,ymin+boxh],[xmin+boxw,ymin+boxh]]).astype(float)
    ###############
    feature_param = dict( maxCorners = 100, qualityLevel = 0.3, minDistance = 7, blockSize = 7)
    lk_param = dict( winSize = (15, 15), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    
    mask = np.zeros_like(frames[0])
    old_gray = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
    corners = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_param)#cornersGet(frames[0])#, bboxs[0])
    
    # TODO: clone = Cloning(source_image, target_image, pts)
    
    for i in range(1, frame_num):
        old_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_RGB2GRAY)
        new_gray = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, new_gray, corners, None, **lk_param)
        p0, st, err = cv2.calcOpticalFlowPyrLK(new_gray, old_gray, p1, None, **lk_param)
        distance = abs(corners-p0).reshape(-1, 2).max(-1)
        good_flag = distance < 1
        new_corners = []
        for c, (x, y), flag in zip(corners, p1.reshape(-1, 2), good_flag):
            if not flag:
                continue
            new_corners.append((int(x), int(y)))
        
        corners = cv2.goodFeaturesToTrack(new_gray, mask = None, **feature_param)#cornersGet(frames[i])

        # TODO: clone.OpenCV_Cloning(center)
        
    cv2.destroyAllWindows()

    cap.release()
    
