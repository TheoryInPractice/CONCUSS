#!/bin/bash

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

. $(dirname $(which $0))/test_common.sh

test_pipeline() {
	log_bold "Running $1 test..."
	replaced_config=`echo "${1}" | sed 's/\//\-/' `
	filename="/tmp/concuss_out_${replaced_config}.txt"
	# Run concuss.py with profiling, keeping only the "Stats from" lines
	# and the one line after them
	${path}/../concuss.py ${newargs[0]} $1 "${path}/config/test_multi.cfg" -c "${coloring_file}" -C -p > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/concuss_test_${replaced_config}.txt"
	grep "Number of occurrences" "${filename}"
	common $1
}

test_multi() {
	log_bold "Running $1 test..."
	replaced_config=`echo "config/test_multi.cfg" | sed 's/\//\-/' `
	filename="/tmp/concuss_out_${replaced_config}.txt"
	# Run concuss.py with profiling, keeping only the "Stats from" lines
	# and the one line after them
	${path}/../concuss.py ${newargs[0]} multi "${path}/config/test_multi.cfg" -c "${coloring_file}" -C -m "${1}" -p > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/concuss_test_${replaced_config}.txt"
	grep "Number of occurrences" "${filename}"
	common "config/test_multi.cfg"
}

common(){
    replaced_config=`echo "${1}" | sed 's/\//\-/' `
	time=$(total_time "/tmp/concuss_test_${replaced_config}.txt")
	echo "Total time: ${time} seconds"
	echo
}

color_graph_given_size() {
	log_bold "Creating graph coloring..."
	size=$2

	filename=$(basename "$1")
	coloring_file="${path}/colorings/${filename%.*}${size}"
	if [ "$#" -lt 3 ]; then
		conf="../config/default.cfg"
	else
		conf="$3"
	fi
	config_file="${path}/${conf}"
	${path}/../lib/coloring/generate_coloring.py $1 $size ${config_file} -o ${coloring_file}
	echo
}

color_graph_given_size ${newargs[0]} ${newargs[1]} config/test_multi.cfg
test_pipeline "path${newargs[1]}"
test_pipeline "star${newargs[1]}"
test_pipeline "clique${newargs[1]}"

touch "${path}/graphs/motifs/mfile"
echo -e "path${newargs[1]}\nstar${newargs[1]}\nclique${newargs[1]}" > "${path}/graphs/motifs/mfile"
test_multi "${path}/graphs/motifs/mfile"

rm "${path}/graphs/motifs/mfile"
