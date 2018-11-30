#!/bin/bash

#$IMG_PATH = $(date+"%Y-%m-%d")
#img_date = ""
img_date=`date +%Y_%m_%d_%H_%M`
#echo $DATE

raspistill -vf -hf -o /home/pi/Desktop/camera/$img_date.jpg
