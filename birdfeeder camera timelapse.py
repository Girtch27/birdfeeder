from gpiozero import LED, PWMLED, RGBLED, MotionSensor, Button, LightSensor, CPUTemperature
from picamera import PiCamera, Color
from time import sleep, strftime
from random import randint
from datetime import datetime
import shutil
import subprocess
import schedule
import os


from twython import Twython
#git clone git://github.com/ryanmcgrath/twython.git
#
#then run the install:
#
#cd twython
#sudo python3 setup.py install

REDled = PWMLED(18)
IRled = PWMLED(17)

REDled.on()

#********************************************
pir = MotionSensor(26, queue_len=500, sample_rate=100, threshold=0.999) #100 samples, 100 samples /sec, need 1/2sec with 0.9 or 45/50, PIR motion sensor
#pir = MotionSensor(26, queue_len=10) #100s per second, retroflective sensor

button = Button(13) #pull-up
camera = PiCamera()
camera.rotation = 270
camera.resolution = (1920,1080)  #(2592, 1944) (1920, 1080) (1280,720) (1024, 768)
                                #camera.resolution = max picture #(2592, 1944) (1280,720) (1024, 768),
                                #max video (1920,1080), max twitter video (1820, 720)
camera.iso = 100                #0 which is auto, 100 to 800
meter_mode = 'average'             #'average', 'spot', 'backlit', 'matrix'

camera.brightness = 50          #0 to 50, default 50
camera.exposure_mode = 'auto'   #'off','auto','sun', 'night','nightpreview','backlight'
camera.awb_mode = 'sunlight'    #'off', 'auto', 'sunlight', 'cloudy'
camera.exposure_compensation = 0 #-25 and 25
camera.contrast = 0            #-100 to 100
camera.drc_strength = 'off'     #'off' ,'low', 'medium', 'high'
camera.annotate_background = Color('black')
#camera.annotate_foreground = Color('black') #defaults to white if not set to a colour

NumPics = 1     #number of pictures to take
DelayPics = 0   #delay in secs between pictures

NumVids = 1     #number of pictures to take
DelayVids = 0   #delay in secs between videos
VidLength = 10   #video length in seconds, 17s is 20s on tweeter

global r, BirdCount
#r = 0           #set first message if not using random message
FirstRun = 1    #take pics and video and tweet them on start, then wait for motion
BirdCount = 0   #Count number of birds detected
TempBirdCount = 0

global frame
frame = 1 #set pics for stop motion video
firstFrame = "n\a" #just incase it doesn't get set with an actual time, start with an frame not equal to 1 if it stops and I restart
lastFrame = "n\a" #just incase it doesn't get set with an actual time



# fill in your 4 keys in following variables 
C_key = "DCSBGe1eNi3onHKGYDYbfR4Yv"
C_secret = "6JKkOcCDOfedC6HymmocSUdworjwdegkdDNcS4uSDB6cAA5l2I"
A_token = "1041181598618542080-LcE0VvPGyAvoPE1pi1zbOXkwih3J6i"
A_secret = "bSuQYx6AsrbqST6gk8nIUbaGVrn4Zf0IzG8LwREWjuhhW"
myTweet = Twython(C_key,C_secret,A_token,A_secret)

# Twitter messages to use when tweeting
messages = []
messages.append("Thanks for visiting the auto tweeting #birdfeeder.")
messages.append("The early bird gets the worm but the 2nd mouse gets the cheese!")
messages.append("I think I should make a TikTok with these...")
messages.append("This bird just took a selfie.")
messages.append("I feel as if someone is watching me...")
messages.append("The early bird gets the worm or seeds.")
messages.append("Bird @Ubereats just arrived!")

#messages.append("Self isolating, wish I could watch Youtube or Netflix.")
#messages.append("A #bird in the #Birdfeeder is worth two tweets. #RaspberryPi #birdwatching")
#messages.append("Another happy bird served. #RaspberryPi #Birdfeeder #birdwatching")
#messages.append("Who ruffled her feathers? #RaspberryPi #Birdfeeder #birdwatching")
#messages.append("Yum free food! #RaspberryPi #Birdfeeder #birdwatching")
#messages.append("Knock knock? Who's there... #RaspberryPi #Birdfeeder #birdwatching")

#pick one tweet randomly
r = randint(0, len(messages)-1)
RandomMessage = messages[r]
#myTweet.update_status(status=message)

def my_TimeStampComment(comment):
    now = datetime.now()
    myTimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    print(myTimeStamp + "-> " + comment)

   
def my_ScheduledPic():
    sleep(2)
    global frame, firstFrame, lastFrame, TimeStamp, videoFN, firstFrameTweet, lastFrameTweet
    #camera.resolution = (3200,2464) #(1920,1080) #(1280,720), 3280x2464   
    #camera.resolution = (1066,600) #(1920, 1080) (1820,720) *(1280,720) (1024, 768) (640, 480)
    camera.zoom = (0, 0.15, 0.85, 1) #rotated so is it this zoom (0, 0.8, 0.2, 0.0)

    now = datetime.now()
    TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
    if frame == 1: #get a big first picture
        camera.zoom = (0, 0, 1, 1)
   
    my_TimeStampComment("Take scheduled pic..." + str(frame))
    camera.start_preview()
   
    camera.annotate_text = "" #clear
    
    
    #camera.annotate_text = "0, 0, 1, 1"
    camera.capture('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % frame)
    sleep(1) #wait for last pic to be saved so file is present

    '''
    camera.zoom = (0, 0, 0.5, 0.5)
    camera.annotate_text = "0, 0, 0.5, 0.5"
    camera.capture('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % frame)
    sleep(1) #wait for last pic to be saved so file is present
    frame += 1 #increment

    camera.zoom = (0.5, 0, 1, 0.5)
    camera.annotate_text = "0.5, 0, 1, 0.5"
    camera.capture('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % frame)
    sleep(1) #wait for last pic to be saved so file is present
    frame += 1 #increment

    camera.zoom = (0, 0.5, 0.5, 1)
    camera.annotate_text = "0, 0.5, 0.5, 1"
    camera.capture('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % frame)
    sleep(1) #wait for last pic to be saved so file is present
    frame += 1 #increment

    camera.zoom = (0.5, 0.5, 1, 1)
    camera.annotate_text = "0.5, 0.5, 1, 1"
    camera.capture('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % frame)
    '''
    
    #number of frames to take for timelapse
    numFrames =  40 #91 #121
    
    if frame == 1:
        firstFrame = TimeStamp
        #print(firstFrame)
    if frame >= numFrames:
        lastFrame = TimeStamp
        #print(lastFrame)
   

        sleep(1) #wait for last pic to be saved so file is present

        my_TimeStampComment("delete file mp4 file...")
        if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4"):
            os.remove("/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4")

        #make stop motion animation, above line check and deletes mp4 just incase or avconv has error as it can't overwrite

        my_TimeStampComment("Create stop animation video..." + TimeStamp)
        #subprocess.call(["/usr/bin/avconv","-r","10","-i","/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg","-qscale","2","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4"]) #worked
        subprocess.call(["/usr/bin/ffmpeg","-r","10","-i","/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg","-qscale","2","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4"]) #worked
        #os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4","/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4")
        videoFN =  "/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4" #set videoFN to the name offile to tweet when its time
        
        firstFrameTweet = firstFrame
        lastFrameTweet = lastFrame
        
        my_TimeStampComment("check files before delete " + str(frame) + " files...")
        for i in range(1,frame+1):
            if os.path.exists('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % i):
                #my_TimeStampComment("delete file " + str(i) + " of " +str(frame))
                os.remove('/home/pi/Desktop/Birdfeeder/Animation/pic%03d.jpg' % i)
        my_TimeStampComment(str(frame) + " files deleted...")
  
        my_TimeStampComment("setframe = 0")
        frame = 0 #reset counter to start over
               
        '''if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4"):
            now = datetime.now()
            TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)
            os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4")
        '''
        
        my_TimeStampComment("waiting...")

    frame += 1 #increment


def my_ScheduledTweet():
    global frame, firstFrameTweet, lastFrameTweet, TimeStamp, videoFN
    
    #if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4"):
        #my_TimeStampComment("open video " + "/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4" )
        #video = open('/home/pi/Desktop/Birdfeeder/Animation/animation.mp4', 'rb')
        #videoFN =  "/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4"
        #videoFN =  "/home/pi/Desktop/Birdfeeder/Animation/animationtweet.mp4"
        #videoFN already set to filename when final picture taken and video made
    video = open(videoFN, 'rb')
    #load mp4 video to twitter and get the media ID
    my_TimeStampComment("Tweet stop animation video..." + videoFN)
    message = ("#Birdfeeder stop motion animation (time lapse) video. @Raspberry_Pi automatically takes images & creates the mp4 video.\n#birds #birdwatching #RaspberryPi" + "\n\nFrom:\n" + firstFrameTweet + ", To:\n" + lastFrameTweet)
    response = myTweet.upload_video(media=video, media_type='video/mp4')
    myTweet.update_status(status=message, media_ids=[response['media_id']])

def my_ScheduledTweeterSearch():
    my_TimeStampComment("searching...")
    #result = myTweet.cursor(myTweet.search, q='python').items(5)
    #result = myTweet.cursor(myTweet.search, q="https://api.twitter.com/1.1/search/tweets.json?q=%40RPi_Camera%20%22take%20a%20picture%20now!%22&src=typed_query")
    #result = myTweet.search(q=keywords, count=100)
    #result = myTweet.search(q=keywords, result_type='popular')
    #keywords = '@RPi_Camera "take a picture now!'
    #results = myTweet.cursor(myTweet.search, q=keywords)

    #https://twitter.com/search?q=python&src=typed_query
    #Replace “https://twitter.com/search” with
    #“https://api.twitter.com/1.1/search/tweets.json” and you will get:
    #https://api.twitter.com/1.1/search/tweets.json?q=twitterdev%20new%20premium

    #keywords = "https://api.twitter.com/1.1/search/tweets.json?q=%40RPi_Camera%20%22take%20a%20picture%20now!%22&src=typed_query"
    #keywords = "@RPi_Camera take a picture now!"

    #https://api.twitter.com/1.1/search/tweets.json?q=python&src=typed_query

    results = myTweet.search(q="@https://api.twitter.com/1.1/search/tweets.json?q=python&src=typed_query", result_type='mixed')


    for result in results:
        print(results)

    my_TimeStampComment("searching complete...")


    #print(results)


    #*********************************


#*******************************************************************************************************************
#*******************************************************************************************************************
#schedule.every().hour.at(":00").do(my_ScheduledPic)

schedule.every(1).minutes.at(":00").do(my_ScheduledPic)
schedule.every(1).minutes.at(":15").do(my_ScheduledPic)
schedule.every(1).minutes.at(":30").do(my_ScheduledPic)
schedule.every(1).minutes.at(":45").do(my_ScheduledPic)
#schedule.every(1).minutes.at(":40").do(my_ScheduledPic)
#schedule.every().day.at("07:00").do(my_ScheduledTweet)
#schedule.every().day.at("10:00").do(my_ScheduledTweet)
#schedule.every().day.at("12:00").do(my_ScheduledTweet)
schedule.every().day.at("19:30").do(my_ScheduledTweet)
#schedule.every().day.at("19:59").do(my_ScheduledTweet)


#schedule.every().hour.at(":00").do(my_ScheduledNoonTweet)
#schedule.every(5).minutes.do(delete_job) 

camera.start_preview()
sleep(2)
if FirstRun == 1:
    FirstRun = 0 #set to "0" false so doesn't run again
    my_TimeStampComment("First run picture check...")
    if os.path.exists('/home/pi/Desktop/Birdfeeder/Animation/animation.mp4'):
        my_TimeStampComment("RETRY on startup open video")
        video = open('/home/pi/Desktop/Birdfeeder/Animation/animation.mp4', 'rb')

        #load mp4 video to twitter and get the media ID
        my_TimeStampComment("RETRY on startup Tweet stop animation video...")
        now = datetime.now()
        TimeStamp = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(now)

        message = ("#Birdfeeder stop motion animation (time lapse) video. @Raspberry_Pi automatically takes images & creates the mp4 video.\n#birds #birdwatching #RaspberryPi" + "\n\nUploaded:\n" +TimeStamp)
        response = myTweet.upload_video(media=video, media_type='video/mp4')
        myTweet.update_status(status=message, media_ids=[response['media_id']])
        if os.path.exists("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4"):
            os.rename("/home/pi/Desktop/Birdfeeder/Animation/animation.mp4","/home/pi/Desktop/Birdfeeder/Animation/animation " + TimeStamp + ".mp4")
        my_TimeStampComment("RETRY complete on startup, waiting...")
    #my_TakePicture(1, 0) #take 1 test picture and video to make sure its OK, overwrite pic
    #my_TakeVideo(1, 0, 3)
    #my_TimeStampComment("waiting for motion...")
my_TimeStampComment("waiting...")

while True:
    if 7 <= datetime.now().hour  < 20:
        #my_ScheduledTweeterSearch()
        #print("Time hr is: " + str(datetime.now().hour))
        schedule.run_pending()
    RandomMessage = messages[r]
    sleep(1)
 

#end
#*******************************************************************************************************************
#*******************************************************************************************************************
