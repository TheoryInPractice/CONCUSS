##CONCUSS: Combatting Network Complexity Using Structural Sparsity
# Testing

To help developers ensure that changes do not impact the correctness of the pattern counts provided by CONCUSS, three testing scripts are included (outlined below).

## `test_pypy.sh`

### Usage
From the testing directory run:

	./test_pypy.sh [OPTIONS] graph motif [config]

### Description

The `test_pypy.sh` script is a wrapper around two calls to `concuss.py`:  one using CPython 2.7 and the other using PyPy.
A comparison of the running times is printed to the console.
The arguments to `test_pypy.sh` are the same as those to `concuss.py`, although `test_pypy.sh` will automatically add the `-p` option.
Full profiling information is available in the `/tmp/` directory after execution.

## `test_coloring.sh`

## Usage
From the testing directory run:

	./test_coloring.sh [OPTIONS] graph motif

### Description

The `test_coloring.sh` script runs the coloring portion of CONCUSS using a number of different configuration files to test program correctness, as well as to compare run times.
The arguments to `test_coloring.sh` are the same as those to `concuss.py` except there is no need to specify a configuration file.
This test automatically enables the `-p` option.
Full profiling information from all configurations is available in `/tmp/` after execution.


## `test_counters.sh`

### Usage
From the testing directory run:

	./test_counters.sh [OPTIONS] graph motif

### Description

The `test_counters.sh` script runs the decompose, compute, and combine sections of CONCUSS using a number of different configuration files to test program correctness, as well as to compare run times.
A single *p*-centered coloring is generated and subsequently used during all runs.
The arguments to `test_counters.sh` are the same as those to `concuss.py` except there is no need to specify a configuration file nor a coloring file.
This test automatically enables the `-p` option.
It also runs the `nxCount.py` script, which counts patterns using NetworkX, in order to verify the counts from CONCUSS are correct.
Full profiling information from all configurations is available in `/tmp/` after execution.


