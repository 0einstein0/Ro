
# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
from pynput.mouse import Button
import imutils
import time
from pynput.mouse import Listener
import pyautogui
import cv2
import json 

def append_track(filepath,obj,x, y, w,h,object):
	with open(filepath, 'r') as fp:
		information = json.load(fp)
	information["trackobj"].append({
					"frame":object.get(1) ,	
					"object":obj,		
    				"x" : x, 
    				"y" : y, 
    				"w" : w, 
   					"h" : h
    				})
	with open(filepath, 'w') as fp:
		json.dump(information, fp, indent=2)  


def getFrame(object):
	return object.get(1)



# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
	help="drone.mp4")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
	help="OpenCV object tracker type")
args = vars(ap.parse_args())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
	tracker = cv2.Tracker_create(args["tracker"].upper())

# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
	# initialize a dictionary that maps strings to their corresponding
	# OpenCV object tracker implementations
	OPENCV_OBJECT_TRACKERS = {
		"csrt": cv2.TrackerCSRT_create,
		"kcf": cv2.TrackerKCF_create,

	}

	# grab the appropriate object tracker using our dictionary of
	# OpenCV object tracker objects
	tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

	
img1 = cv2.imread('pistol1.jpg')
img2  = cv2.imread('pist.jpg')
img3  = cv2.imread('pistol2.jpg')
# Get Image dimensions
img_height, img_width,_ = img1.shape

# initialize the bounding box coordinates of the object we are going
# to track
initBB = None


# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# initialize the FPS throughput estimator
fps = None

# loop over frames from the video stream
while True:
	

	

	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	
	
	frame = frame[1] if args.get("video", False) else frame
	
	

	# check to see if we have reached the end of the stream
	if frame is None:
		break

	# resize the frame (so we can process it faster) and grab the
	# frame dimensions
	frame = imutils.resize(frame, width=900)
	(H, W) = frame.shape[:2]

	# check to see if we are currently tracking an object
	if initBB is not None:
		# grab the new bounding box coordinates of the object
		(success, box) = tracker.update(frame)

		# check to see if the tracking was a success
		if success:
			(x, y, w, h) = [int(v) for v in box]
			cv2.rectangle(frame, (x, y), (x + w, y + h),
				(0, 255, 0), 2)
			append_track('rec1.json',6,x, y, w,h,vs)	# Data to be written 
			

		
				
				
		# update the FPS counter
		fps.update()
		fps.stop()

	
	# show the output frame
	cv2.imshow("NFS", frame)
	cv2.moveWindow('NFS',240,100)
	key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track
		initBB = cv2.selectROI("NFS", frame, fromCenter=False,
			showCrosshair=True)
	
		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
		tracker.init(frame, initBB)
		fps = FPS().start()
	
		   

		 
				    
	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# if we are using a webcam, release the pointer
if not args.get("video", False):
	vs.stop()

# otherwise, release the file pointer
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()


