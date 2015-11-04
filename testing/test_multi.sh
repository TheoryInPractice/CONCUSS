#!/bin/sh
. $(dirname $(which $0))/test_common.sh

#"${path}/multi.sh" testing/graphs/karate.txt 3
#"${path}/multi.sh" testing/graphs/karate.txt 4
"${path}/multi.sh" testing/graphs/netscience.gml 3
#"${path}/multi.sh" testing/graphs/netscience.gml 4