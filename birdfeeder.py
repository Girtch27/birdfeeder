import numpy as np
import picamera
import picamera.array
from time import sleep, strftime
from datetime import datetime
from picamera import Color
import subprocess
from random import randint
import schedule
import os
from twython import Twython
#git clone git://github.com/ryanmcgrath/twython.git
#
#then run the install:
#
#cd twython
#sudo python3 setup.py install

'''
segmentation fault -do this:
The way to do it, is operating system dependant. In linux, you can check with the command ulimit -s your current value and you can increase it with ulimit -s <new_value>
Try doubling the previous value and continue doubling if it does not work, until you find one that does or run out of memory.
'''

class DetectMotion(picamera.array.PiMotionAnalysis):
    def analyze(self, a):
        global birdDetected, squirrelDetected, birdframe, squirrelframe, vectorMagLimit, vectorBird, magnitudeSquirrel, vectorSquirrel
        a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        #if (a > 60).sum() > 10:
        vectorMagLimit = 100
        magnitudeSquirrel = 200
        
        vectorBird = 30 #1050 for windy days #500 #30 fo 640x480
        vectorSquirrel = 1800 #1500 # 300 for 640x480

        now = datetime.now()
        TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
        vectorNum = (a > 60).sum()
        if (vectorNum > vectorBird):   #found something
            if (vectorNum < vectorSquirrel):
                birdframe =  birdframe + 1
                birdDetected = 1
            else:                      #found a squirrel
                squirrelframe = squirrelframe + 1
                squirrelDetected = 1
                if squirrelframe > 200:
                    squirrelframe = 0
        #else: #no birds or squirrels code goes here
            

#******************


#******************

def my_TimeStampComment(comment):
    global TimeStamp
    now = datetime.now()
    myTimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    TimeStamp = myTimeStamp #used for filenames
    print(myTimeStamp + "-> " + comment)


def my_ScheduledTimeLapseTweet():
    global birdframe, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN, videoFNcreated
    #videoFNcreated = 1
    #videoFN = '/home/pi/Desktop/Birdfeeder/Animation/Animation test.mp4'
    if videoFNcreated == 1:
        video = open(videoFN, 'rb')
        #load mp4 video to twitter and get the media ID
        my_TimeStampComment("Tweet stop animation video..." + videoFN)
        message = ("#Birdfeeder stop motion animation (time lapse) video. @Raspberry_Pi automatically takes images & creates the mp4 video.\n#birds #birdwatching #RaspberryPi")
        #response = myTweet.upload_video(media=video, media_type='video/mp4') #previous method, worked for 20sec length
        #https://github.com/ryanmcgrath/twython/issues/438, post videos of up to 2:20 in length
        response = myTweet.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
        myTweet.update_status(status=message, media_ids=[response['media_id']])
        videoFNcreated = 0 #set it back to 0 after sending tweet, so doesn't send the same video next tweet
    else:
        my_TimeStampComment('no video, no tweeting...')

def my_SendVideoTweet():
    global videoReady
    #videoFNcreated = 1
    #videoFN = '/home/pi/Desktop/Birdfeeder/Animation/Animation test.mp4'
    if videoReady == 1:
        video = open(videoFN, 'rb')
        #load mp4 video to twitter and get the media ID
        my_TimeStampComment("Tweet stop animation video..." + videoFN)
        message = ("#Birdfeeder video. @Raspberry_Pi automatically takes a mp4 video.\n#birds #birdwatching #RaspberryPi")
        #response = myTweet.upload_video(media=video, media_type='video/mp4') #previous method, worked for 20sec length
        #https://github.com/ryanmcgrath/twython/issues/438, post videos of up to 2:20 in length
        response = myTweet.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
        myTweet.update_status(status=message, media_ids=[response['media_id']])
        videoFNcreated = 0 #set it back to 0 after sending tweet, so doesn't send the same video next tweet
    else:
        my_TimeStampComment('no video, no tweeting...')
        
def my_CreateAnimation():
    global birdframe, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN, videoFNcreated

    my_TimeStampComment('create animation...' + str(birdframe) + ' images')
    subprocess.call(["/usr/bin/ffmpeg","-r","2","-i","/home/pi/Desktop/Birdfeeder/images/image%03d.jpg","-qscale","2","/home/pi/Desktop/Birdfeeder/Animation/Animation " + TimeStamp + ".mp4"]) #worked
    videoFN =  "/home/pi/Desktop/Birdfeeder/Animation/Animation " + TimeStamp + ".mp4" #set videoFN to the name offile to tweet when its time
    
    my_TimeStampComment("check files before delete " + str(birdframe) + " files...")
    for i in range(1,birdframe):
        if os.path.exists('/home/pi/Desktop/Birdfeeder/images/image%03d.jpg' % i):
            #my_TimeStampComment("delete file " + str(i) + " of " +str(frame))
            os.remove('/home/pi/Desktop/Birdfeeder/images/image%03d.jpg' % i)
    if os.path.exists('/home/pi/Desktop/Birdfeeder/images/image000.jpg'):
            #my_TimeStampComment("delete file " + str(i) + " of " +str(frame))
            os.remove('/home/pi/Desktop/Birdfeeder/images/image000.jpg')       
    my_TimeStampComment(str(birdframe) + " files deleted and image000...")
    my_TimeStampComment("set bird frame = 0")
    birdframe = 0 #reset counter to start over
               
    '''if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4"):
    now = datetime.now()
    TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4")
    '''
    videoFNcreated = 1 #video created, ok to tweet it
    my_TimeStampComment("timelapse video created, waiting...")

def my_CreateVideo(length):
    global videoReady
    os.rename('/home/pi/Desktop/Birdfeeder/images/video.h264', '/home/pi/Desktop/Birdfeeder/images/video1.h264')
    camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video2.h264', format='h264', motion_output=output)
    camera.wait_recording(length)
    camera.stop_recording()
    subprocess.call(["/usr/bin/ffmpeg","-i","concat:/home/pi/Desktop/Birdfeeder/images/video1.h264|/home/pi/Desktop/Birdfeeder/images/video2.h264","-c","copy","/home/pi/Desktop/Birdfeeder/images/video3.h264"]) #worked
    #ffmpeg -i v1.h264 -c:av copy v1.mp4
    subprocess.call(["/usr/bin/ffmpeg","-i","/home/pi/Desktop/Birdfeeder/images/video3.h264","-c:av","copy","/home/pi/Desktop/Birdfeeder/images/video3.mp4"])
    os.remove('/home/pi/Desktop/Birdfeeder/images/video1.h264')
    os.remove('/home/pi/Desktop/Birdfeeder/images/video2.h264')
    videoReady = 1


#******************
# fill in your 4 keys in following variables 
C_key = "DCSBGe1eNi3onHKGYDYbfR4Yv"
C_secret = "6JKkOcCDOfedC6HymmocSUdworjwdegkdDNcS4uSDB6cAA5l2I"
A_token = "1041181598618542080-LcE0VvPGyAvoPE1pi1zbOXkwih3J6i"
A_secret = "bSuQYx6AsrbqST6gk8nIUbaGVrn4Zf0IzG8LwREWjuhhW"
myTweet = Twython(C_key,C_secret,A_token,A_secret)


birdframe = 0
squirrelframe = 0
firstFrame = 0
videoFNcreated = 0

schedule.every().day.at("09:00").do(my_ScheduledTimeLapseTweet)
schedule.every().day.at("11:00").do(my_ScheduledVideoTweet)
schedule.every().day.at("14:00").do(my_ScheduledTimeLapseTweet)
schedule.every().day.at("16:00").do(my_ScheduledVideoTweet)
schedule.every().day.at("17:50").do(my_ScheduledTimeLapseTweet)

#schedule.every().day.at("20:25").do(my_ScheduledTweet)


#******************

with picamera.PiCamera() as camera:
    global birdDetected, squirrelDetected
    birdDetected = 0
    squirrelDetected = 0

    camera.rotation = 270
    camera.resolution = (1024, 768) #(640,480)  #(2592, 1944) (1920, 1080) (1280,720) (1024, 768)
                                #camera.resolution = max picture #(2592, 1944) (1280,720) (1024, 768),
                                #max video (1920,1080), max twitter video (1820, 720)
    camera.framerate = 30 #6  #various speeds based on resolution
    camera.iso = 600                #0 which is auto, 100 to 800
    camera.meter_mode = 'matrix'    #'average', 'spot', 'backlit', 'matrix'

    camera.brightness = 50          #0 to 50, default 50
    camera.exposure_mode = 'sports'   #'off','auto','sunlight','night','nightpreview','backlight'
    camera.exposure_compensation = 0 #-25 and 25
    camera.contrast = 0             #-100 to 100
    camera.drc_strength = 'off'     #'off' ,'low', 'medium', 'high'
    camera.annotate_background = Color('black')
    #camera.annotate_foreground = Color('black') #defaults to white if not set to a colour

    with DetectMotion(camera) as output:
        while True:
            timecheck = datetime.now().hour
            if 6 <= timecheck  < 18:
                schedule.run_pending()
                camera.start_preview()
                sleep(2)
                my_TimeStampComment('started & waiting...')
                #timestamp videos, save all or save same filename and delete
                #camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video ' + TimeStamp + '.h264', format='h264', motion_output=output)
                camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video.h264', format='h264', motion_output=output)
                camera.wait_recording(2)
                camera.stop_recording()
                if birdDetected == 1:
                        my_TimeStampComment('bird detected, make videos')
                        my_CreateVideo(4)
                        my_SendVideoTweet()
                        birdDetected = 0
                else:
                    sleep(1)
                    os.remove('/home/pi/Desktop/Birdfeeder/images/video.h264')
            sleep(2)


# reference code
# camera.capture ('/home/pi/Desktop/Birdfeeder/images/imagesquirrel%03d.jpg' %squirrelframe) #('./camera/recent.jpg') or %03d.jpg' % frame
# my_TimeStampComment('Squirrel detected, take image ' + str(squirrelframe) + ', limit: ' + str(vectorSquirrel) + ' < ' + str(vectorNum))
