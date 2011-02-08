#!/bin/sh

rm -rf temp > /dev/null
mkdir temp > /dev/null
cd temp

BASEFILE=${1%\.*}

cp ../$BASEFILE.tex .
cp ../$BASEFILE.bib .
pdflatex $BASEFILE.tex > /dev/null
bibtex $BASEFILE.aux > /dev/null
pdflatex $BASEFILE.tex > /dev/null
pdflatex $BASEFILE.tex > /dev/null

cp $BASEFILE.pdf ..
cd ..
rm -rf temp

