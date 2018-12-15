#!/bin/bash

img_date=`date +%Y_%m_%d_%H`

raspistill -vf -hf -o /home/pi/Desktop/camera/$img_date.jpg

# start virtual environment
#source ~/cvpi/bin/activate

# anaylize the image capture
#python ~/cvpi/face/face_detect_cv3.py /home/pi/Desktop/camera/$img_date.jpg ~/cvpi/face/haarcascade_frontalface_default.xml




