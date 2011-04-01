# This is everything needed to make the sintel clip used for the class.


# Download pre-requisites (the raw files), you´ll need to uncomment these.
# Get Video
#wget http://media.xiph.org/sintel/sintel_trailer-1080-png.tar.gz
#tar -xzvf sintel_trailer-1080-png.tar.gz

# Get Audio
#wget http://media.xiph.org/sintel/sintel_trailer-audio.flac


#  For this exercise, we´re going to use seconds 7.0-17.0 (10sec)
# Clip the audio, this still doesn´t line up correctly, but its not our fault.  The stuff on the site doesn´t lineup.
ffmpeg -i sintel_trailer-audio.flac -ss 7.0 -t 10.0 -acodec flac sintel_clip.flac

# Clip the video and put into y4m container 
# Total size approx 1.1GB
# Cropping off black space at top and bottom
ffmpeg -i 1080/sintel_trailer_2k_%04d.png -ss 7.0 -t 10.0 -vf crop=1920:816:0:132 -vcodec rawvideo -pix_fmt yuv444p sintel_clip.y4m

