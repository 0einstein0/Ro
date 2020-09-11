from imutils.video import VideoStream
from imutils.video import FPS
# import argparse
from pynput.mouse import Listener


import json 

import imutils
import time
import cv2
import numpy as np

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video", type=str)
# ap.add_argument("-t", "--tracker", type=str)
# args = vars(ap.parse_args())

def getFrame(object):
    return object.get(1)

obj=0;
hit=0;
def checkhit(x, y, button, pressed):
    global hit; 
    global obj;
    cframe=getFrame(vs)
    x=x-240
    y=y-100
    if pressed==True:
        with open('rec1.json') as json_file:
            data = json.load(json_file)
            
        for p in data['trackobj']:
            if cframe==p['frame']:
                if(x>p['x'] and x<p['x']+p['w'] and y>p['y'] and y<p['y']+p['h']): 
                    obj = p['object']
                    print(x,y,cframe,obj)
                    print("HIT!")
                    hit+=1
                    return 1
                elif (p['object']!=7):
                    continue                 
                else:
                    obj = p['object']
                    print(x,y,cframe,obj)  



# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

args = {'tracker': 'csrt', 'video': 'dashcam_boston.mp4', 'image': 'pist.jpg'}

# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())
else:
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
    }
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()



# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)

# grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

run_once=0
# loop over frames from the video stream
while True:


    # grab the current frame

    frame = vs.read()
    
    if run_once==0:
        listener = Listener(on_click=checkhit)
        listener.start()
        run_once=1
    
    frame = frame[1] if args.get("video", False) else frame
    # check to see if we have reached the end of the stream
    if frame is None:
        break

    # resize the frame (so we can process it faster) and grab the
    # frame dimensions
    frame = imutils.resize(frame, width=900)
    (H, W) = frame.shape[:2]


   
    bg=frame.copy()
   
    if(hit!=0):           
        with open('rec1.json') as json_file:
            data = json.load(json_file)
            for d in data['trackobj']:
                cframe=getFrame(vs)
                if cframe==d['frame'] and d['object']==obj:
                    cv2.rectangle(frame,(d['x'],d['y']+d['h']),(d['x']+d['w'],d['y']),(0,0,255),-1)
                    cv2.addWeighted(bg, 0.5, frame, 1 - 0.5,0, frame) 
                    text = 'Hit: '+str(hit)    
                    cv2.putText(frame, text, (10,  420), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (19, 165, 15), 5)
       

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
 
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        listener.stop()
        break

# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()