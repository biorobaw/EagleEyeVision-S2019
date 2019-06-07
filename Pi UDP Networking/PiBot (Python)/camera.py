import cv2
import time
from ThreadedWebcam import ThreadedWebcam
import math

FPS_SMOOTHING = 0.9

class Camera(object):
    def __init__(self):
        #Zachary's house test
        # self.minH =   169; self.minS = 109; self.minV =   56
        # self.maxH = 180; self.maxS = 235; self.maxV = 135
        #Zachary's red trash can
        # self.minH =   169; self.minS = 105; self.minV =   41
        # self.maxH = 179; self.maxS = 194; self.maxV = 76
        #C4 Pink Goal
        self.minH =   152; self.minS = 120; self.minV =   85
        self.maxH = 180; self.maxS = 255; self.maxV = 255
        
        self.fps = 0; self.prev = 0
        self.capture = ThreadedWebcam() # UnthreadedWebcam()
        self.capture.start()
        params = cv2.SimpleBlobDetector_Params()
        self.detector = cv2.SimpleBlobDetector_create(params)
        fs = cv2.FileStorage("params.yaml", cv2.FILE_STORAGE_READ)
        if not fs.isOpened():
                print("No params")
                exit(1)
        self.detector.read(fs.root())
        fs.release()

    def getBlobs(self):
        frame = self.capture.read()
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frame_hsv, (self.minH, self.minS, self.minV), (self.maxH, self.maxS, self.maxV))
        keypoints = self.detector.detect(mask)
        frame_with_keypoints = cv2.drawKeypoints(frame, keypoints, None, color = (0, 255, 0), flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.putText(frame_with_keypoints, "{} blobs".format(len(keypoints)), (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
        return keypoints       
    
    def getBlobsColored(self, color):
        frame = self.capture.read()
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(frame_hsv, (color['minH'], color['minS'], color['minV']), (color['maxH'], color['maxS'], color['maxV']))
        keypoints = self.detector.detect(mask)
        frame_with_keypoints = cv2.drawKeypoints(frame, keypoints, None, color = (0, 255, 0), flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.putText(frame_with_keypoints, "{} blobs".format(len(keypoints)), (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))
        return keypoints   

    def getBlobStats(self):
        stats = {
            'leftmost': 640,
            'rightmost': 0,
            'highest': 0,
            'lowest': 480,
            'averageX': 0,
            'averageY': 0,
            'blobs': False,
            'maxDiameter': 0,
            'totalArea': 0
        }
        keypoints = self.getBlobs('unknown')
        for key in keypoints:
            stats['blobs'] = True
            x = key.pt[0]
            y = key.pt[1]
            diameter = key.size
            if x < stats['leftmost']:
                stats['leftmost'] = x
            if x > stats['rightmost']:
                stats['rightmost'] = x
            if y < stats['lowest']:
                stats['lowest'] = y
            if y > stats['highest']:
                stats['highest'] = y
            if diameter > stats['maxDiameter']:
                stats['maxDiameter'] = diameter
            stats['averageX'] += x
            stats['averageY'] += y
            stats['totalArea'] += (diameter / 2) * (diameter / 2) * math.pi
        if len(keypoints) > 0:
            stats['averageX'] /= len(keypoints)
            stats['averageY'] /= len(keypoints)
        return stats

    def getBlobStatsColored(self, color):
        stats = {
            'leftmost': 640,
            'rightmost': 0,
            'highest': 0,
            'lowest': 480,
            'averageX': 0,
            'averageY': 0,
            'blobs': False,
            'maxDiameter': 0,
            'totalArea': 0
        }
        keypoints = self.getBlobsColored(color)
        for key in keypoints:
            stats['blobs'] = True
            x = key.pt[0]
            y = key.pt[1]
            diameter = key.size
            if x < stats['leftmost']:
                stats['leftmost'] = x
            if x > stats['rightmost']:
                stats['rightmost'] = x
            if y < stats['lowest']:
                stats['lowest'] = y
            if y > stats['highest']:
                stats['highest'] = y
            if diameter > stats['maxDiameter']:
                stats['maxDiameter'] = diameter
            stats['averageX'] += x
            stats['averageY'] += y
            stats['totalArea'] += (diameter / 2) * (diameter / 2) * math.pi
        if len(keypoints) > 0:
            stats['averageX'] /= len(keypoints)
            stats['averageY'] /= len(keypoints)
        return stats