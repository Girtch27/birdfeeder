Features to add in the future:
(1) gui, or
(2) turn into a web app or webserver to view gui from a browser\TV\phone etc
(3) allow different user configurations:1] pictures or videos, 2]number of pics or Xsec long video, 3] set tweet schedule times, 4] allow someone to create a tweet and select pic or video and send manually rather then wait for automatic tweet to happen
(4) use opencv and\or TensorFlow to analyze pics and\or videos to classify which birds are present then organize tweet by bird type. Ex tweet here is some cardinals OR see this blue jay

This project use a Raspberry Pi and Rpi's camera. Camera continually takes a videos and analyzes it to detect a change (motion), if frame's changes exceeds a threshold it considers it a bird, if too much motion then likely a squirrel. If a bird is deteced it takes a 2nd video and joins the original with the new video, converts to mp4 and tweets it during certain times automatically, morning, noon and late afternoon.

Requires Twython and picamera

Some code disabled which does:
(1) tweet on schedules
(2) take pictures when bird detected instead of videos, combine multiple pictures into a video then tweet the video, like a timelapse video
