import numpy as np
import picamera
import picamera.array
from time import sleep, strftime
from datetime import datetime
from picamera import Color
import subprocess
from random import randint
import schedule
import os, shutil
from twython import Twython

'''
*********************
git
*********************
1] git clone git://github.com/ryanmcgrath/twython.git
2]then run the install:
3]cd twython
4]sudo python3 setup.py install

*********************
segmentation fault -do this:
*********************
The way to do it, is operating system dependant. In linux, you can check with the command ulimit -s your current value and you can increase it with ulimit -s <new_value>
Try doubling the previous value and continue doubling if it does not work, until you find one that does or run out of memory.
'''

class DetectMotion(picamera.array.PiMotionAnalysis):
    def analyze(self, a):
        global birdDetected, squirrelDetected, birdframe, squirrelframe, vectorBird, magnitudeSquirrel, vectorSquirrel
        
        #sent some limits
        magnitudeSquirrel = 200
        vectorBird = 400  #try 100 when a>100, 1050 for windy days #500 #30 fo 640x480
        vectorSquirrel = 2000 #1500 # 300 for 640x480

        now = datetime.now()
        TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
        
        '''
        array math example: If there're more than 10 vectors with a magnitude greater than 60, then say we've detected motion
        if (a > 60).sum() > 10:
        '''        
        a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
        vectorNum = (a > 65).sum()
        
        #bird found, something above low limit and below max limit
        if (vectorBird <= vectorNum <= vectorSquirrel):
            birdframe =  birdframe + 1
            birdDetected = 1

        #something larger found [squirrel???], something above max limit
        if (vectorNum > vectorSquirrel):
            squirrelframe = squirrelframe + 1
            squirrelDetected = 1
            if squirrelframe > 200:
                squirrelframe = 0
        
#class DetectMotion(picamera.array.PiMotionAnalysis):


def my_TimeStampComment(comment):
    global TimeStamp
    now = datetime.now()
    myTimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    TimeStamp = myTimeStamp #used for filenames
    print(myTimeStamp + "-> " + comment)


def my_ScheduledTimeLapseTweet():
    global birdframe, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN, videoFNcreated
    if videoFNcreated == 1:
        my_TimeStampComment("Tweet stop animation video..." + videoFN)
        
        #set tweet video and message
        video = open(videoFN, 'rb')
        message = ("#Birdfeeder stop motion animation (time lapse) video. @Raspberry_Pi automatically takes images & creates the mp4 video.\n#birds #birdwatching #RaspberryPi")
        
        #reference this https://github.com/ryanmcgrath/twython/issues/438, post videos of up to 2:20 in length
        #load mp4 video to twitter and get the media ID, then send tweet message with media ID
        response = myTweet.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
        myTweet.update_status(status=message, media_ids=[response['media_id']])
        
        videoFNcreated = 0 #set it back to 0 after sending tweet, so doesn't send the same video next tweet
    else:
        my_TimeStampComment('no video, no tweeting...')

def my_SendVideoTweet(videoFN):
    global videoReady
    if videoReady == 1:
        my_TimeStampComment("Tweet video..." + videoFN)
        
        #set tweet video and message
        video = open(videoFN, 'rb')
        message = ("#Birdfeeder video. #RaspberryPi automatically takes a mp4 video.\n#birds #birdwatching")

        #reference this https://github.com/ryanmcgrath/twython/issues/438, post videos of up to 2:20 in length
        #load mp4 video to twitter and get the media ID, then send tweet message with media ID
        response = myTweet.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
        myTweet.update_status(status=message, media_ids=[response['media_id']])
        
        #save tweeted video as new name to reference later if neede
        os.rename('/home/pi/Desktop/Birdfeeder/images/video.mp4', '/home/pi/Desktop/Birdfeeder/images/videoTweeted ' + TimeStamp + '.mp4')
        videoFNcreated = 0
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
               
    videoFNcreated = 1 #video created, ok to tweet it
    my_TimeStampComment("timelapse video created, waiting...")

def my_CreateVideo(length):
    global videoReady
    camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video2.h264', format='h264', motion_output=output)
    camera.wait_recording(length)
    camera.stop_recording()
    my_TimeStampComment("create & combine videos...")
    if os.path.exists('/home/pi/Desktop/Birdfeeder/images/video.mp4'): #delete mp4 file incase one still there when re-start program, ffmeg will crash if file there
        os.remove('/home/pi/Desktop/Birdfeeder/images/video.mp4')       
    subprocess.call(["/usr/bin/ffmpeg","-i","concat:/home/pi/Desktop/Birdfeeder/images/video1.h264|/home/pi/Desktop/Birdfeeder/images/video2.h264","-c","copy","/home/pi/Desktop/Birdfeeder/images/video.h264"]) #worked
    #ffmpeg -i v1.h264 -c:av copy v1.mp4
    subprocess.call(["/usr/bin/ffmpeg","-i","/home/pi/Desktop/Birdfeeder/images/video.h264","-c:av","copy","/home/pi/Desktop/Birdfeeder/images/video.mp4"])
    shutil.copy2('/home/pi/Desktop/Birdfeeder/images/video.mp4', '/home/pi/Desktop/Birdfeeder/Animation/video ' + TimeStamp + '.mp4') #copy video to animation dir with timestamp
    os.remove('/home/pi/Desktop/Birdfeeder/images/video1.h264')
    os.remove('/home/pi/Desktop/Birdfeeder/images/video2.h264')
    os.remove('/home/pi/Desktop/Birdfeeder/images/video.h264')
    videoReady = 1


# fill in your 4 keys in following variables 
C_key = "DCSBGe1eNi3onHKGYDYbfR4Yv"
C_secret = "6JKkOcCDOfedC6HymmocSUdworjwdegkdDNcS4uSDB6cAA5l2I"
A_token = "1041181598618542080-LcE0VvPGyAvoPE1pi1zbOXkwih3J6i"
A_secret = "bSuQYx6AsrbqST6gk8nIUbaGVrn4Zf0IzG8LwREWjuhhW"
myTweet = Twython(C_key,C_secret,A_token,A_secret)

#define variables
birdframe = 0
squirrelframe = 0
firstFrame = 0
videoFNcreated = 0

#Set the schedules, schedule tweets, timelapse tweets, not using schedules currently
#schedule.every().day.at("09:00").do(my_ScheduledTimeLapseTweet)
#schedule.every().day.at("11:00").do(my_SendVideoTweet)
#schedule.every().day.at("14:00").do(my_ScheduledTimeLapseTweet)
#schedule.every().day.at("13:00").do(my_SendVideoTweet()
#schedule.every().day.at("17:50").do(my_ScheduledTimeLapseTweet)
#schedule.every().day.at("20:25").do(my_ScheduledTweet)

my_TimeStampComment('started...')

#use camera to get videos
with picamera.PiCamera() as camera:
    global birdDetected, squirrelDetected
    birdDetected = 0
    squirrelDetected = 0

#define camera setup for video, pics and annotate colors
#check for standard resolutions... (640,480) (2592, 1944) (1920, 1080) (1280,720) (1024, 768)
#max video (1920,1080), max twitter video (1820, 720)
    camera.resolution = (1024, 768)
    camera.framerate = 30 #6  #various speeds based on resolution
    camera.iso = 0                  #0 is auto, 100 to 800
    camera.meter_mode = 'spot'    #'average', 'spot', 'backlit', 'matrix'
    camera.rotation = 270
    camera.brightness = 50          #0 to 50, default 50
    camera.exposure_mode = 'auto'   #'off','sports','auto','sunlight','night','nightpreview','backlight'
    camera.exposure_compensation = 0 #-25 and 25
    camera.contrast = 20             #-100 to 100
    camera.drc_strength = 'high'     #'off' ,'low', 'medium', 'high'
    camera.annotate_background = Color('black')
    #camera.annotate_foreground = Color('black') #defaults to white if not set to a colour
    
    my_TimeStampComment('started & waiting...')
    with DetectMotion(camera) as output:
        while True:
            timecheck = datetime.now().hour
            
            #only take videos and check for motion when daytime & light outside
            if 8 <= timecheck  < 17:
                
                #start\check the schedules
                schedule.run_pending()
                
                #start the camera, let it adjust to the light conditions
                camera.start_preview()
                sleep(2)
                
                #take short video and check if motion
                camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video1.h264', format='h264', motion_output=output)
                camera.wait_recording(2)
                camera.stop_recording()
                
                #if motion in above video is within limits for a bird, consider a bird is found and a longer video and join the two videos together
                if birdDetected == 1:
                        birdDetected = 0
                        my_TimeStampComment('bird detected, make videos')
                        
                        #take the 2nd video for X seconds and combine first video to new video
                        my_CreateVideo(4)
                        
                        my_TimeStampComment('bird detected, finished the videos')
                        SendVideoTweetFN = "/home/pi/Desktop/Birdfeeder/images/video.mp4"
                        my_TimeStampComment('bird detected, finished the filename...')

                        #send latest completed video between certian times, don't want to send too many tweets, limit tweets to 1hr during morning, mid-day, and afternoon
                        if (8 <= timecheck  < 9) or (11 <= timecheck  < 12) or (15 <= timecheck  < 16):
                            my_TimeStampComment('bird detected, send tweet...')

                            my_SendVideoTweet(SendVideoTweetFN)
                            my_TimeStampComment('waiting XX seconds after tweet sent...')
                            
                            #depending on bird activity wait before taking more videos and sending more tweets,
                            sleep(13*60) # wait X seconds between tweets
                
                #no bird detected in initial video so wait then delete video and start checking again
                else:
                    sleep(2)
                    os.remove('/home/pi/Desktop/Birdfeeder/images/video1.h264')
                    
            #if 8 <= timecheck  < 17:  wait X seconds when not during daytime before checking if the time is during the day        
            sleep(2)
#The End