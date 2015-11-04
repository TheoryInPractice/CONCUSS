#!/usr/bin/env bash
. $(dirname $(which $0))/test_common.sh

test_pipeline() {
	log_bold "Running $1 test..."
	replaced_config=`echo "${1}" | sed 's/\//\-/' `
	filename="/tmp/concuss_out_${replaced_config}.txt"
	# Run concuss.py with profiling, keeping only the "Stats from" lines
	# and the one line after them
	${path}/../concuss.py $args "${path}/${1}" -c "${coloring_file}" -C -m "${path}/${2}" > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/concuss_test_${replaced_config}.txt"
	grep "Number of occurrences" "${filename}"
}

color_graph $1 $2 ../config/default.cfg
run_test config/test_multi.cfg graphs/motifs/multifile
