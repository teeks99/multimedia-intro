
# Get the high-res version
#wget http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_h264.mov

# Get the low-res version
#wget http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_480p_h264.mov

# Get the Audio
#wget http://media.xiph.org/BBB/BigBuckBunny-DVDMaster-5_1-FLAC.zip
#wget http://media.xiph.org/BBB/BigBuckBunny-stereo.flac


# Intro
ffmpeg -i big_buck_bunny_480p_h264.mov -ss 00:00:30.250 -t 41 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k Intro.mkv

# Bunny Prep
ffmpeg -i big_buck_bunny_480p_h264.mov -ss 00:03:53.583 -t 66 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k BunnyPrep.mkv

# Clips for compositing on one screen
ffmpeg -i big_buck_bunny_480p_h264.mov -ss 00:05:32.583 -t 7 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k RedSquirrel.mkv
ffmpeg -i big_buck_bunny_480p_h264.mov -ss 00:05:40.083 -t 35.125 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k GraySquirrel.mkv
ffmpeg -i big_buck_bunny_480p_h264.mov -ss 00:06:18.708 -t 66.083 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k FlyingSquirrel.mkv

