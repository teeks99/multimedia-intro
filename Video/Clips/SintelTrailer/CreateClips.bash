# This is everything needed to make the sintel trailer and clip used for the class.


# Download pre-requisites (the raw files), you´ll need to uncomment these.
# Get Video
#wget http://media.xiph.org/sintel/sintel_trailer-1080-png.tar.gz
#tar -xzvf sintel_trailer-1080-png.tar.gz

# Get Audio
#wget http://media.xiph.org/sintel/sintel_trailer-audio.flac

# Crop down the PNGs to the resolution of the video
ffmpeg -i 1080/sintel_trailer_2k_%04d.png -vf crop=1920:816:0:132 -vcodec rawvideo -pix_fmt yuv444p sintel_trailer.y4m

#  We want the whole thing, but at low-res
ffmpeg -i sintel_trailer.y4m -i sintel_trailer-audio.flac -pass 1 -vcodec libx264 -vpre slow_firstpass -s 960x408 -b 1200k -bt 1200k -an -f rawvideo -y /dev/null
ffmpeg -i sintel_trailer.y4m -i sintel_trailer-audio.flac -pass 2 -vcodec libx264 -vpre slow -s 960x408 -b 1200k -bt 1200k -acodec libfaac -ab 192k output.mp4
qt-faststart output.mp4 sintel_trailer-408p-x264_slow2p-1200k-faac-192k.mp4
rm output.mp4
rm *log*

#  Same thing, but mpeg4-mp3
ffmpeg -i sintel_trailer.y4m -i sintel_trailer-audio.flac -pass 1 -vcodec mpeg4 -s 960x408 -b 2400k -bt 2400k -an -f rawvideo -y /dev/null
ffmpeg -i sintel_trailer.y4m -i sintel_trailer-audio.flac -pass 2 -vcodec mpeg4 -s 960x408 -b 2400k -bt 2400k -acodec libmp3lame -ab 256k sintel_trailer-408p-mpeg4-mp3.mp4

# === For this exercise, we´re going to use seconds 7.0-17.0 (10sec) ===
# Clip the audio, this still doesn´t line up correctly, but its not our fault.  The stuff on the site doesn´t lineup.
ffmpeg -i sintel_trailer-audio.flac -ss 7.0 -t 10.0 -acodec flac sintel_clip.flac

# Clip the video and put into y4m container 
# Total size approx 1.1GB
# Cropping off black space at top and bottom
ffmpeg -i sintel_trailer.y4m -ss 7.0 -t 10.0 -vcodec rawvideo -pix_fmt yuv444p sintel_clip.y4m

# Finally with the two combined, x264 lossless
ffmpeg -i sintel_clip.y4m -i sintel_clip.flac -pass 1 -vcodec libx264 -vpre lossless_max -acodec flac sintel_clip-x264-lossless-flac.mkv

# 408p (~480p) y4m
ffmpeg -i sintel_clip.y4m -vcodec rawvideo -s 960x408 -pix_fmt yuv444p sintel_clip-408p.y4m

# Lossy
ffmpeg -i sintel_trailer-408p-mpeg4-mp3.mp4 -ss 7.0 -t 10.0 -vcodec copy -acodec copy sintel_clip-408p-mpeg4-mp3.mp4


# === Create Example Encodings ===
run_encoding(){
    mkdir -p $1
    cp FFMpegTester.py jquery-1.5.2.js $1.json $1/
    cp -l sintel_clip.y4m sintel_clip-408p.y4m sintel_clip.flac $1/
    cd $1
    python FFMpegTester.py --input=$1.json --html
    cd ..
}
run_encoding sintel_constant_demo
run_encoding sintel_good
run_encoding sintel_perfect
run_encoding sintel_rate_demo
run_encoding sintel_small_good
run_encoding sintel_small_perfect


