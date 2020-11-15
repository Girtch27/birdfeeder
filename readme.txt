This project use a Raspberry Pi and Rpi's camera. Camera takes takes videos and analyzes when there is motion, if motion takes a 2nd video and
joins them together and tweets them out during certain times automatically. Picamera video format is converted to mp4 for Twitter.

Requires Twython and picamera

Some code disabled which does:
(1) tweet on schedules
(2) take pictures when bird detected instead of videos, combine multiple pictures into a video then tweet the video, like a timelapse video
