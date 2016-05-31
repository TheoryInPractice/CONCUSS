#!/bin/bash

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

# test_pypy.sh - Run concuss.py with the same arguments through both CPython
# and PyPy so that we can automatically see how much better (or in some cases,
# worse) PyPy is.

. $(dirname $(which $0))/test_common.sh

args="$@"

test_pipeline() {
	log_bold "Running $1 test..."
	filename="/tmp/concuss_out_${1}.txt"
	# Run concuss.py with profiling, keeping only the "Stats from" lines
	# and the one line after them
	$1 ${path}/../concuss.py $args -c "${coloring_file}" -C -p > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/concuss_test_${1}.txt"
	grep "Number of occurrences" "${filename}"
}

run_nx_test
color_graph $1 $2
run_test python2.7
python2_time=$time
run_test pypy
pypy_time=$time
echo "PyPy took $(echo "scale=3;100*${pypy_time}/${python2_time}" | bc)% as long as CPython."
