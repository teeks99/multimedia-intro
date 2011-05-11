
# Get the high-res version
#wget http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_h264.mov
#wget http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_480p_h264.mov
# Get the low-res, stereo version
#wget http://mirrorblender.top-ix.org/peach/bigbuckbunny_movies/big_buck_bunny_480p_stereo.ogg

# Get the Audio
#wget http://media.xiph.org/BBB/BigBuckBunny-DVDMaster-5_1-FLAC.zip
#wget http://media.xiph.org/BBB/BigBuckBunny-stereo.flac

# A random background music track
#wget http://ccmixter.org/contests/freestylemix/hisboyelroy/freestylemix_-_hisboyelroy_-_Revolve.mp3

# Intro
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:00:30.250 -t 17 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k Intro.mkv

# Bunny
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:03:53.583 -t 66 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k BunnyPrep.mkv
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:07:52.875 -t 7.25 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k BunnyRelax.mkv


# Clips for compositing on one screen
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:05:32.583 -t 5 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k RedSquirrel.mkv
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:05:40.083 -t 10 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k GraySquirrel.mkv
ffmpeg -i big_buck_bunny_480p_stereo.ogg -ss 00:06:31.208 -t 15 -vcodec mpeg4 -b 6000k -acodec libfaac -ab 192k FlyingSquirrel.mkv



