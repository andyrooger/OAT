#!/bin/bash

echo -n Setup...
rm -rf temp &> /dev/null
mkdir temp &> /dev/null
cd temp &> /dev/null

BASEFILE=${1%\.*}

cp ../$BASEFILE.tex . &> /dev/null
cp ../$BASEFILE.bib . &> /dev/null

echo -n Compilation...

latex $BASEFILE.tex &> /dev/null
bibtex $BASEFILE.aux &> $BASEFILE.bib.log
latex $BASEFILE.tex &> /dev/null
latex $BASEFILE.tex &> $BASEFILE.tex.log

echo -n Conversion...

dvips $BASEFILE.dvi &> /dev/null
ps2pdf $BASEFILE.ps &> /dev/null

echo -n Cleanup...

cp $BASEFILE.pdf ..
cp $BASEFILE.bib.log ..
cp $BASEFILE.tex.log ..
cd ..
rm -rf temp

echo Done
