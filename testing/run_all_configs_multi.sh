#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)
FILES='testing/config/*'

for f in $FILES
  do
    echo Config file ${bold} $f ${normal}:
    echo
    ./concuss.py $1 multi $f -m testing/graphs/motifs/multifile.txt
    echo
  done
