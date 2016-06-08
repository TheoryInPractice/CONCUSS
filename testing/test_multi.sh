#!/bin/bash

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

. $(dirname $(which $0))/test_common.sh

"${path}/multi.sh" testing/graphs/karate.txt 3
"${path}/multi.sh" testing/graphs/karate.txt 4
#"${path}/multi.sh" testing/graphs/netscience.gml 3
#"${path}/multi.sh" testing/graphs/netscience.gml 4
