import numpy as np
import picamera
import picamera.array
from time import sleep, strftime
from datetime import datetime
from picamera import Color
import subprocess
import schedule
import os



class DetectMotion(picamera.array.PiMotionAnalysis):
    def analyze(self, a):
        global motionDetected, frame, vectorMagLimit, vectorLimit, magnitudeSquirrel, vectorSquirrel
        a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        #if (a > 60).sum() > 10:
        vectorMagLimit = 100
        vectorLimit = 10
        magnitudeSquirrel = 200
        vectorSquirrel = 20


        if (a > 60).sum() > 30:
            vectorNum = (a > 60).sum()
            camera.annotate_text = ("vectorNum:" + str(vectorNum))
            camera.capture ('/home/pi/Desktop/Birdfeeder/images/image%03d.jpg' %frame) #('./camera/recent.jpg') or %03d.jpg' % frame
            if (a > 60).sum() < 300: #squirrel check
                my_TimeStampComment('Motion detected, take image' + str(frame) + ', motion status:' + str(vectorNum)) # + str(a))
            else:
                my_TimeStampComment('Squirrel detected, take image' + str(frame) + ', motion status:' + str(vectorNum)) # + str(a))
            lastFrame = frame
            frame =  frame + 1
            motionDetected = 1
            sleep(1)

        else:
            if motionDetected == 1:
                vectorNum = (a > 60).sum()
                my_TimeStampComment('Waiting NO Motion after motion was detected....' + str(vectorNum))
                motionDetected = 0
                #sleep(1)
#******************


#******************
def my_TimeStampComment(comment):
    global TimeStamp
    now = datetime.now()
    myTimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    TimeStamp = myTimeStamp #used for filenames
    print(myTimeStamp + "-> " + comment)


def my_ScheduledTweet():
    global frame, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN, videoFNcreated
    if videoFNcreated == 1:
        video = open(videoFN, 'rb')
        #load mp4 video to twitter and get the media ID
        my_TimeStampComment("Tweet stop animation video..." + videoFN)
        message = ("#Birdfeeder stop motion animation (time lapse) video. @Raspberry_Pi automatically takes images & creates the mp4 video.\n#birds #birdwatching #RaspberryPi" + "\n\nFrom:\n" + firstFrameTweet + ", To:\n" + lastFrameTweet)
        #response = myTweet.upload_video(media=video, media_type='video/mp4') #previous method, worked for 20sec length
        #https://github.com/ryanmcgrath/twython/issues/438, post videos of up to 2:20 in length
        response = myTweet.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
        myTweet.update_status(status=message, media_ids=[response['media_id']])
    else:
        my_TimeStampComment('no video, no tweeting...')

        
def my_CreateAnimation():
    global frame, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN, videoFNcreated

    my_TimeStampComment('create animation...' + str(frame) + ' images')
    subprocess.call(["/usr/bin/ffmpeg","-r","2","-i","/home/pi/Desktop/Birdfeeder/images/image%03d.jpg","-qscale","2","/home/pi/Desktop/Birdfeeder/Animation/Animation " + TimeStamp + ".mp4"]) #worked
    videoFN =  "/home/pi/Desktop/Birdfeeder/Animation/Animation " + TimeStamp + ".mp4" #set videoFN to the name offile to tweet when its time
    #os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4","/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4")
    
    '''
    if frame > 0:
        firstFrameTweet = firstFrame
        lastFrameTweet = lastFrame
    '''
    
    my_TimeStampComment("check files before delete " + str(frame) + " files...")
    for i in range(1,frame):
        if os.path.exists('/home/pi/Desktop/Birdfeeder/images/image%03d.jpg' % i):
            #my_TimeStampComment("delete file " + str(i) + " of " +str(frame))
            os.remove('/home/pi/Desktop/Birdfeeder/images/image%03d.jpg' % i)
        my_TimeStampComment(str(frame) + " files deleted...")
  
        my_TimeStampComment("setframe = 0")
        frame = 0 #reset counter to start over
               
        '''if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4"):
            now = datetime.now()
            TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
            os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4")
        '''
        videoFNcreated = 1 #video created, ok to tweet it
        my_TimeStampComment("timelapsve video created, waiting...")



#******************
frame = 0
firstFrame = 0
videoFNcreated = 0

schedule.every().day.at("10:00").do(my_ScheduledTweet)
schedule.every().day.at("14:00").do(my_ScheduledTweet)
schedule.every().day.at("19:59").do(my_ScheduledTweet)






#******************

with picamera.PiCamera() as camera:
    global motionDetected
    motionDetected = 0

    camera.rotation = 270
    camera.resolution = (640,480)  #(2592, 1944) (1920, 1080) (1280,720) (1024, 768)
                                #camera.resolution = max picture #(2592, 1944) (1280,720) (1024, 768),
                                #max video (1920,1080), max twitter video (1820, 720)
    camera.framerate = 10  #various speeds based on resolution
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
            if 6 <= datetime.now().hour  < 20:

                schedule.run_pending()
                camera.start_preview()
                sleep(2)
                my_TimeStampComment('started & waiting...')
                #camera.resolution = (640, 480)
                camera.start_recording('/home/pi/Desktop/Birdfeeder/images/video ' + TimeStamp + '.h264', format='h264', motion_output=output)
                camera.wait_recording(600)
                camera.stop_recording()
                #my_TimeStampComment('motion is...' + str(motionDetected))
                #if motionDetected == 0:
                #my_TimeStampComment('delete file...' + str(motionDetected))
                
                #os.remove('/home/pi/Desktop/Birdfeeder/images/video.h264')
                if frame >= 10: # video set to make 2 frames / sec, 5sec
                    my_CreateAnimation()
                my_TimeStampComment('finished')
                sleep(1)


        
