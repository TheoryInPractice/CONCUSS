#!/bin/sh
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

# test_coloring.sh - Run generate_coloring.py with different configurations through
# CPython.

. $(dirname $(which $0))/test_common.sh

color_graph $1 $2 config/so_tfa_max.cfg
color_graph $1 $2 config/so_tfa_min.cfg
color_graph $1 $2 config/so_tfa_dsat.cfg
color_graph $1 $2 config/so_dtfa_max.cfg
color_graph $1 $2 config/so_dtfa_min.cfg
color_graph $1 $2 config/so_dtfa_dsat.cfg
color_graph $1 $2 config/ldo_tfa_max.cfg
color_graph $1 $2 config/ldo_tfa_min.cfg
color_graph $1 $2 config/ldo_tfa_dsat.cfg
color_graph $1 $2 config/ldo_dtfa_max.cfg
color_graph $1 $2 config/ldo_dtfa_min.cfg
color_graph $1 $2 config/ldo_dtfa_dsat.cfg

