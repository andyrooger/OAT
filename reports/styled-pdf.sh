#!/bin/sh

rm -rf temp > /dev/null
mkdir temp > /dev/null
cd temp

BASEFILE=${1%\.*}

#pandoc -t latex --template=../report.template --base-header-level=2 -o $BASEFILE.tex ../$1 &&
#pdflatex $BASEFILE.tex > /dev/null
pdflatex ../$BASEFILE.tex > /dev/null

cp $BASEFILE.pdf ..
cd ..
rm -rf temp

