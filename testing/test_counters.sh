#!/bin/sh

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


# test_counters.sh - Run concuss.py with different configurations through
# CPython, and run nxCount.py, to test correctness of all configurations of the
# pattern counting pipeline.

. $(dirname $(which $0))/test_common.sh

test_pipeline() {
	log_bold "Running $1 test..."
	replaced_config=`echo "${1}" | sed 's/\//\-/' `
	filename="/tmp/concuss_out_${replaced_config}.txt"
	# Run concuss.py with profiling, keeping only the "Stats from" lines
	# and the one line after them
	${path}/../concuss.py $args "${path}/${1}.cfg" -c "${coloring_file}" -C -p > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/concuss_test_${replaced_config}.txt"
	grep "Number of occurrences" "${filename}"
}

run_nx_test
color_graph $1 $2 ../config/default
run_test config/fast_comb_cc
run_test config/fast_comb_icc
run_test config/fast_comb_inex
run_test config/fast_comb_hybrid
run_test config/fast_comb_ihybrid
run_test config/fast_cs_cc
run_test config/fast_cs_icc
run_test config/fast_cs_inex
run_test config/fast_cs_hybrid
run_test config/fast_cs_ihybrid
