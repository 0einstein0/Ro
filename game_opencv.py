# USAGE
# python opencv_object_tracking.py
# python opencv_object_tracking.py --video dashcam_boston.mp4 --tracker csrt

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
"""
def append_track(filepath,x, y, w,h,object):

	with open(filepath, 'r') as fp:
		information = json.load(fp)

	information["trackobj"].append({
					"frame":object.get(1) ,			
    				"x" : x, 
    				"y" : y, 
    				"w" : w, 
   					"h" : h
    				})
	with open(filepath, 'w') as fp:
		json.dump(information, fp, indent=2)  
"""

def getFrame(object):
	return object.get(1)

def checkhit(x, y, button, pressed):
	cframe=getFrame(vs)
	x=x-240
	y=y-100
	if pressed==True:
		with open('track_record.json') as json_file:
			data = json.load(json_file)
		for p in data['trackobj']:
			if cframe==p['frame']:
				if(x>p['x'] and x<p['x']+p['w'] and y>p['y'] and y<p['y']+p['h']):
					print(x,y,cframe)
					print("HIT!")
				else:
					print(x,y,cframe)
					print("MISS")
	return
	

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
		"boosting": cv2.TrackerBoosting_create,
		"mil": cv2.TrackerMIL_create,
		"tld": cv2.TrackerTLD_create,
		"medianflow": cv2.TrackerMedianFlow_create,
		"mosse": cv2.TrackerMOSSE_create
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
initBB2=None

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
run_once=0
# loop over frames from the video stream
while True:
	
	xm,ym=pyautogui.position()
	

	# grab the current frame, then handle if we are using a
	# VideoStream or VideoCapture object
	frame = vs.read()
	if run_once==0:
		listener = Listener(on_click=checkhit)
		listener.start()
		run_once=1
	
	frame = frame[1] if args.get("video", False) else frame
	
	img1 = imutils.resize(img1, width=380)
	img2 = imutils.resize(img2, width=380)
	img3 = imutils.resize(img3, width=380)
	bg, fg1,fg2,fg3 = frame.copy(), img1.copy(), img2.copy(), img3.copy()

	offset_x, offset_y = 447, 440
	fg_rows, fg_cols, fg_channels = fg1.shape
	roi = bg[offset_x:fg_rows + offset_x, offset_y:fg_cols + offset_y]
#img1
	fg2gray1 = cv2.cvtColor(fg1, cv2.COLOR_BGR2GRAY)
	ret1, mask1 = cv2.threshold(fg2gray1, 254, 255, cv2.THRESH_BINARY_INV)
	mask_inv1 = cv2.bitwise_not(mask1)
#img2
	fg2gray2 = cv2.cvtColor(fg2, cv2.COLOR_BGR2GRAY)
	ret2, mask2 = cv2.threshold(fg2gray2, 254, 255, cv2.THRESH_BINARY_INV)
	mask_inv2 = cv2.bitwise_not(mask2)
#img3
	fg2gray3 = cv2.cvtColor(fg3, cv2.COLOR_BGR2GRAY)
	ret3, mask3 = cv2.threshold(fg2gray3, 254, 255, cv2.THRESH_BINARY_INV)
	mask_inv3 = cv2.bitwise_not(mask3)
	
	if(xm<600):
		img_fg = cv2.bitwise_and(fg1, fg1, mask=mask1)
		img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv1)
		out_img = cv2.add(img_bg, img_fg)
	elif(xm>600 and xm<800):
		img_fg = cv2.bitwise_and(fg2, fg2, mask=mask2)
		img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv2)
		out_img = cv2.add(img_bg, img_fg)
	else:
		img_fg = cv2.bitwise_and(fg3, fg3, mask=mask3)
		img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv3)
		out_img = cv2.add(img_bg, img_fg)
	bg[offset_x:fg_rows + offset_x, offset_y:fg_cols + offset_y] = out_img

	frame = bg.copy()

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
			#append_track('track_record.json',x, y, w,h,vs)	# Data to be written 
			

		
				
				
		# update the FPS counter
		fps.update()
		fps.stop()

		# initialize the set of information we'll be displaying on
		# the frame
		info = [
			("Tracker", args["tracker"]),
			("Success", box if success else "No"),
			("FPS", "{:.2f}".format(fps.fps())),
		]

		# loop over the info tuples and draw them on our frame
		for (i, (k, v)) in enumerate(info):
			text = "{}: {}".format(k, v)
			cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
	
	# show the output frame
	cv2.imshow("NFS", frame)
	cv2.moveWindow('NFS',240,100)
	key = cv2.waitKey(1) & 0xFF

	# if the 's' key is selected, we are going to "select" a bounding
	# box to track
	if key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		initBB = cv2.selectROI("NFS", frame, fromCenter=False,
			showCrosshair=True)
	
		# start OpenCV object tracker using the supplied bounding box
		# coordinates, then start the FPS throughput estimator as well
		tracker.init(frame, initBB)
		fps = FPS().start()
		if initBB is not None:
		   

		   initBB2 = cv2.selectROI("NFS", frame, fromCenter=False,
			showCrosshair=True)
		   tracker.init(frame, initBB2)
		   fps = FPS().start()
				    
	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
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
