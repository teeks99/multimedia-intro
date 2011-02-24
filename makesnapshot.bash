#!/bin/bash
# Create a snapshot of the current text and put it in a zip file

dateString=`date +%Y`-`date +%m`-`date +%d`

cd ..
mkdir mmedia-intro-$dateString
cp -lR multimedia-intro/* mmedia-intro-$dateString
zip -r mmedia-intro-$dateString.zip mmedia-intro-$dateString
rm -rf mmedia-intro-$dateString

