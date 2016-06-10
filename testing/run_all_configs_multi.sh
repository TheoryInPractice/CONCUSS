#!/bin/bash
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

# This script runs the multi-motif pipeline against all configuration files
# in testing/config/
# It takes two arguments - 1. graph, 2. multi-motif file.

bold=$(tput bold)
normal=$(tput sgr0)
FILES='testing/config/*'

for f in $FILES
  do
    echo Config file ${bold} $f ${normal}:
    echo
    ./concuss.py $1 multi $f -m $2
    echo
  done
