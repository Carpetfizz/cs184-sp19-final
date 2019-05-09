import pickle
import glob
import math
import argparse
import cv2
import numpy as np
import numpy.linalg as LA
import json
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from skimage.feature import (match_descriptors,ORB)
from skimage import transform as tf
from filters import VO_Filter

# Given a video file outputs a tuple of numpy arrays
# The first array is the translations undergone by the camera
# The second array is rotations undergone by the camera

class Features:
    def __init__(self, keypoints, descriptors):
        self.keypoints = keypoints
        self.descriptors = descriptors
    def get_keypoints(self, indices):
        k = self.keypoints[indices]
        # NOTE: keypoints are organized as [row, col]
        return np.column_stack((k[:,1], k[:,0]))

def rotm_to_eul(R):
    # SOURCE: 
    # https://www.learnopencv.com/rotation-matrix-to-euler-angles/     
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return np.array([x, y, z]) * 180 / np.pi


def apply_so3(R, t, p):
    p_ = R.dot(p)
    return p_ + t

def generate_path(rotations, translations):
    path = []
    current_point = np.array([0, 0, 0])

    for R, t in zip(rotations, translations):
        path.append(current_point)
        # don't care about rotation of a single point
        current_point = apply_so3(np.eye(3), t.reshape((3,)), current_point)
    return np.array(path)


def count_frames(path):
    video = cv2.VideoCapture(path)
    total = 0
    while True:
        f, _ = video.read()
        if not f:
            break
        total += 1
    return total


def vo(source, scale_factor = 0.25):
    count = 0
    prev_image = None
    cur_image = None
    prev_features = None
    cur_features = None
    cap = cv2.VideoCapture(source)
    scale_factor = 0.25

    NUM_FRAMES = count_frames(source)
    LIMIT = 300

    translations = []
    rotations = []

    prev_image = None
    cur_image = None

    descriptor_extractor = ORB(n_keypoints=200)

    count = 0

    while(cap.isOpened() and count < LIMIT):
        print("Frame: %d/%d" % (count, LIMIT))
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = tf.rescale(gray, scale_factor, multichannel = False)
        
        descriptor_extractor.detect_and_extract(gray)
        keypoints = descriptor_extractor.keypoints
        descriptors = descriptor_extractor.descriptors
        features = Features(keypoints, descriptors)
        
        prev_features = cur_features
        cur_features = features
        
        prev_image = cur_image
        cur_image = gray

        count += 1
        if count > 1:
            matches = match_descriptors(prev_features.descriptors, cur_features.descriptors, cross_check=True)
            k1 = prev_features.get_keypoints(matches[:,0])
            k2 = cur_features.get_keypoints(matches[:,1])
            
            E, mask = cv2.findEssentialMat(k1, k2, 
                                    focal = scale_factor * 2868, # 3.5mm / 1.22um pitch
                                    pp = (1920/2 * scale_factor, 1080/2 * scale_factor), 
                                    method = cv2.RANSAC, 
                                    prob = 0.999, 
                                    threshold = 1.0)
            
            points, R, t, mask = cv2.recoverPose(E, k1, k2)
            
            # assume dominant motion is forward
            if (t[2] >= 0):
                translations.append(-t)
                rotations.append(R)

    cap.release()

    return rotations, translations

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('path_out')
    parser.add_argument('rot_out')
    args = parser.parse_args()

    rotations, translations = vo(args.source)

    angles = np.row_stack([rotm_to_eul(r) for r in rotations])
    path_raw = np.array(generate_path(rotations, translations))

    print(angles.shape)
    print(path_raw.shape)
    
    angles_filtered, path_filtered = VO_Filter(angles, path_raw)

    l = []
    for i in range(np.size(path_filtered, 0)):
        point = path_filtered[i, :]
        l.append([point[0], 0, point[1]])
    d = {}
    d['path'] = l
    with open(args.path_out,'w') as fp:
    	json.dump(d, fp)

    r = angles_filtered.tolist()
    d = {}
    d['rotations'] = r
    with open(args.rot_out,'w') as fp:
    	json.dump(d, fp)