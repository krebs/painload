#!/bin/sh
if [ -f animation.lcd ] ;then
  rm animation.lcd
fi

echo -n "Frames to convert: "
ls *.png |wc -l

for filename in *.png
do
  echo -n "create mono gif $filename.gif from $filename:"
  convert -monochrome $filename $filename.gif && echo "ok"
  echo -n "converting to lcd file... "
  ../../../r0ket/tools/image/img2lcd.pl $filename.gif && echo "ok"
  echo -n "adding ${filename%\.*}.lcd to animation "
  cat ${filename%\.*}.lcd >> animation.lcd && echo "ok"
done
echo "done"
