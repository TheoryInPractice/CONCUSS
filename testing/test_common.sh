#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

# test_common.sh - Common functions for test scripts

args="$@"
newargs=("$@")
path=$(dirname $(which $0))
export PYTHONPATH=$PYTHONPATH:${path}/..

test_pipeline() {
	echo "test_pipeline must be overridden!" > /dev/stderr
	exit 1
}

log_bold() {
	printf "\033[1m[`date '+%F %T'`] $@\033[0m\n"
}

total_time() {
	# Add up all the "(number) seconds", then print the result as
	# "(total) seconds".  This is done by:
	# Get all occurrences of "(number) seconds", one per line |
	#     replace newlines with spaces |
	#     replace the final " seconds " with "$", replace every "seconds"
	#         with "+" |
	#     replace "$" with a newline |
	#     run the addition |
	#     append " seconds"
	grep -o "[[:digit:].]* seconds" $1 | tr '\n' ' ' | sed "s/ seconds $/$/;s/seconds/+/g" | tr '$' '\n' | bc
}

remove_grep_separator() {
	sed '/^--$/d'
}

run_test() {
	test_pipeline $1
	replaced_config=`echo "${1}" | sed 's/\//\-/' `
	time=$(total_time "/tmp/concuss_test_${replaced_config}.txt")
	echo "Total time: ${time} seconds"
	echo
}

test_nxcount() {
	log_bold "Running nxCount test..."
	filename="/tmp/nxcount_out.txt"
	# Run nxCount.py, keeping only the "Stats from" lines and the one line
	# after them
	${path}/nxCount.py $1 $2 > "${filename}"
	grep -A1 "Stats from" "${filename}" | remove_grep_separator | tee "/tmp/nxcount_test.txt"
	grep "Number of occurrences" "${filename}"
}

run_nx_test() {
	test_nxcount $args
	time=$(total_time /tmp/nxcount_test.txt)
	echo "Total time: ${time} seconds"
	echo
}

color_graph() {
	log_bold "Creating graph coloring..."
	size=$(${path}/graph_size.py $2)

	re='^[0-9]+$'
	if ! [[ $size =~ $re ]] ; then
   		${path}/graph_size.py $2; exit 1
	fi

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
