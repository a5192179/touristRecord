import cv2
import sys
sys.path.append('.')
from getVideoOrder import getVideoOrder
from common import readInput
videoList = getVideoOrder()

videoSavePath = '../output'
suffix = 'test'
frameID = 0
imgSize = (1280, 720)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
videoOut = cv2.VideoWriter()
fps = 29.76
videoOut.open(videoSavePath + '/' + suffix + '.mp4', fourcc, fps, imgSize, True)
for video in videoList:
    print(video)
    bStop = False
    reader = readInput.InputReader(video)
    while not bStop:
        frame, bStop = reader.read()
        if bStop or frame is None:
            break
        frameID += 1
        videoOut.write(frame)
        cv2.imshow('frame', frame)
        cv2.waitKey(10)
        print('frameID', frameID)
videoOut.release()