# This is everything needed to make the sintel trailer and clip used for the class.


# Download pre-requisites (the raw files), you´ll need to uncomment these.
# Get Video
#wget http://media.xiph.org/sintel/sintel_trailer-1080-png.tar.gz
#tar -xzvf sintel_trailer-1080-png.tar.gz # Creates directory 1080/

# Get Audio
#wget http://media.xiph.org/sintel/sintel_trailer-audio.flac
#cp -l ../../../Audio/Audio/sintel_trailer-audio.flac .

# Crop down the PNGs to the resolution of the video
#Too Big: ffmpeg -i 1080/sintel_trailer_2k_%04d.png -vf crop=1920:816:0:132 -vcodec rawvideo -pix_fmt yuv444p sintel_trailer.y4m
# Covert to a not super-huge format
ffmpeg -i 1080/sintel_trailer_2k_%04d.png -vf crop=1920:816:0:132 -vcodec libx264 -vpre lossless_max -pix_fmt yuv444p -r 24 sintel_trailer-lossless.mkv

#  We want the whole thing, but at low-res
ffmpeg -i sintel_trailer-lossless.mkv -i sintel_trailer-audio.flac -pass 1 -vcodec libx264 -vpre slow_firstpass -s 960x408 -b 1200k -bt 1200k -an -f rawvideo -y /dev/null
ffmpeg -i sintel_trailer-lossless.mkv -i sintel_trailer-audio.flac -pass 2 -vcodec libx264 -vpre slow -s 960x408 -b 1200k -bt 1200k -acodec libfaac -ab 192k output.mp4
qt-faststart output.mp4 sintel_trailer-408p-x264_slow2p-1200k-faac-192k.mp4
rm output.mp4
rm *log*

#  Same thing, but mpeg4-mp3
ffmpeg -i sintel_trailer-lossless.mkv -i sintel_trailer-audio.flac -pass 1 -vcodec mpeg4 -s 960x408 -b 2400k -bt 2400k -an -f rawvideo -y /dev/null
ffmpeg -i sintel_trailer-lossless.mkv -i sintel_trailer-audio.flac -pass 2 -vcodec mpeg4 -s 960x408 -b 2400k -bt 2400k -acodec libmp3lame -ab 256k sintel_trailer-408p-mpeg4-mp3.mp4

# Create a fully-muxed MKV
"mkvmerge" -o "sintel_trailer-lossless-flac.mkv"  "--language" "0:eng" "--track-name" "0:Main Audio" "--default-track" "0:yes" "--forced-track" "0:no" "-a" "0" "-D" "-S" "-T" "--no-global-tags" "--no-chapters" "sintel_trailer-audio.flac" "--language" "0:eng" "--default-track" "0:no" "--forced-track" "0:no" "-s" "0" "-D" "-A" "-T" "--no-global-tags" "--no-chapters" "sintel_trailer_en.srt" "--language" "0:spa" "--default-track" "0:no" "--forced-track" "0:no" "-s" "0" "-D" "-A" "-T" "--no-global-tags" "--no-chapters" "sintel_trailer_es.srt" "--default-track" "1:no" "--forced-track" "1:no" "--display-dimensions" "1:1920x816" "-d" "1" "-A" "-S" "-T" "--no-chapters" "sintel_trailer-lossless.mkv" "--track-order" "0:0,1:0,2:0,3:1"

# === For this exercise, we´re going to use seconds 7.0-17.0 (10sec) ===
ffmpeg -i sintel_trailer-audio.flac -ss 7.0 -t 10.0 -acodec flac sintel_clip.flac
ffmpeg -i sintel_trailer-lossless.mkv -ss 7.0 -t 10.0 -vcodec libx264 -vpre lossless_max -pix_fmt yuv444p sintel_clip-lossless.mkv

# 408p (~480p) y4m
ffmpeg -i sintel_clip-lossless.mkv -vcodec libx264 -vpre lossless_max -s 960x408 -pix_fmt yuv444p sintel_clip-lossless-408p.mkv

# Lossy
ffmpeg -i sintel_trailer-408p-mpeg4-mp3.mp4 -ss 7.0 -t 10.0 -vcodec copy -acodec copy sintel_clip-408p-mpeg4-mp3.mp4

# Muxed file
ffmpeg -i sintel_trailer-lossless-flac.mkv -ss 7.0 -t 10.0 -vcodec copy -acodec copy -scodec copy sintel_clip-lossless-flac.mkv -scodec copy -newsubtitle

# === Create Example Encodings ===
run_encoding(){
    mkdir -p $1
    cp FFMpegTester.py jquery-1.5.2.js $1.json $1/
    cp -l sintel_clip-lossless.mkv sintel_clip-lossless-408p.mkv sintel_clip.flac $1/
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

# === Create example of slow frame rate ===
ffmpeg -i sintel_clip-408p-mpeg4-mp3.mp4 -vcodec mpeg4 -b 6000k -r 30 -an sintel_clip-408p-mpeg4-30fps.mkv
ffmpeg -i sintel_clip-408p-mpeg4-mp3.mp4 -vcodec mpeg4 -b 6000k -r 5 -an sintel_clip-408p-mpeg4-5fps.mkv


