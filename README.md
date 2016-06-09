<img align="right" src="concuss_logo.png">
# CONCUSS: Combatting Network Complexity Using Structural Sparsity

CONCUSS is a software tool for large scale graph analytics.  The efficiency and scalability of CONCUSS come from exploiting the underlying [structure and sparsity](/docs/background.md) of the data.  It allows users to count the number of occurrences of a specific pattern within a graph (i.e. subgraph isomorphism counting).  These counts are a building block for more complicated scientific analysis, such as motif counting and graphlet degree signature creation.

## Command line usage

    ./concuss.py [OPTIONS] graph pattern [config]

Count the number of subgraphs of `graph` which are isomorphic to `pattern`.

Positional arguments:

* `graph` - filename of the host graph
* `pattern` - filename, basic pattern or `multi`. See [basic patterns](#basic-patterns) and [multiple-patterns](#counting-multiple-patterns-in-a-single-concuss-run) sections below.
* `config` - filename of the configuration settings (defaults to `config/default.cfg`)

Optional arguments:

* `-h, --help` - show help message and exit
* `-o [OUTPUT], --output [OUTPUT]` - filename of the result
* `-v, --verbose` - verbose output
* `-p, --profile` - profile function calls
* `-c [COLORING], --coloring [COLORING]` - filename of existing *p*-centered
  coloring.  When this option is not selected, CONCUSS will find a coloring itself
* `-C, --coloring-no-verify` - same as -c but do not verify correctness of existing coloring
* `-m [MULTI_PAT_FILE], --multi_pat_file [MULTI_PAT_FILE]` - file containing multiple pattern descriptions (as file paths and/or basic patterns)
* `-e [EXECUTION_DATA], --execution-data [EXECUTION_DATA]` - create ZIP archive `EXECUTION_DATA` for visualization with BEAVr


Example command:

Using pattern file:

	./concuss.py testing/graphs/karate.txt testing/graphs/motifs/K3.txt

Example output:

	Number of occurrences of H in G: 270

This means that there are 270 isomorphisms of K3 (a triangle) in the karate network.  Since the triangle has 3 automorphisms, the karate network has 90 distinct triangles.


### Basic patterns:

CONCUSS can be run by providing a basic pattern instead of a pattern file for the `pattern` argument in the execution command. All other positional and optional arguments remain unchanged.

Basic patterns provide a faster and simpler way of specifying patterns to search for in the graph.

We provide the following commonly used basic patterns:

**1-partite basic patterns:**

`clique wheel cycle path star`

Usage:

	.concuss.py {path_to_graph}/graph basicpattern|int
	
`|` represents concatenation. The `int` specifies the number of vertices in pattern.

Example command:

	./concuss.py testing/graphs/karate.txt star4
	
Example output:

	Number of occurrences of H in G: 6588

**Bi-partite basic patterns:**

`biclique`

Usage:

	./concuss.py {path_to_graph}/graph basicpattern|int,int
	
`|` represents concatenation. The `ints` specify the number of vertices in the first and second sets of the bi-partite pattern.

Example command:

	./concuss.py testing/graphs/karate.txt biclique2,2
	
Example output:

	Number of occurrences of H in G: 288
	
## Counting multiple patterns in a single CONCUSS run

CONCUSS supports counting multiple patterns in a single pipeline run. In order to use the multiple pattern pipeline, CONCUSS needs to be run using the command line argument `-m [FILENAME]` where `[FILENAME]` is a file containing descriptions of patterns either as file paths or [basic patterns](#basic-patterns).
For the positional argument `pattern`, the keyword `multi` must be used to specify that we are counting multiple patterns.

The format for the multiple pattern file is as follows. Specify each pattern as a basic pattern or a filename on a separate line.

    basic_pattern_1
    basic_pattern_2
    path/to/pattern/file3
    ...
    basic_pattern_n
    
Example file: [multi_size3.txt](testing/graphs/motifs/multi_size3.txt)

    star3
    path3
    testing/graphs/motifs/K3.txt

Example command:
    
    ./concuss.py testing/graphs/karate.txt multi -m testing/graphs/motifs/multi_size3.txt
    
Example output:

    Number of occurrences of star3 in G: 786
    Number of occurrences of path3 in G: 786
    Number of occurrences of testing/graphs/motifs/K3.txt in G: 270

## Install and Software Requirements

CONCUSS requires a 64-bit operating system and Python 2.7.x interpreter (e.g. CPython or PyPy).
Running the pipeline with PyPy typically decreases runtimes due to native function inlining.

### Extra Dependencies

The main computations in CONCUSS do not require any additional libraries.

To import graph data in GraphML or GEXF format, the Beautiful Soup package is required.

	pip install beautifulsoup

For developers wishing to contribute to CONCUSS, the testing suite (see below) uses the NetworkX python package to verify the correctness of the counts.

	pip install networkx

## File Format Compatibilities

### Graphs

CONCUSS supports reading data files for the host and pattern graphs in the following formats:

* Edgelist (.txt)
* GML (.gml)
* LEDA (.leda)
* GraphML (.graphml) (requires Beautiful Soup package)
* GEXF (.gexf) (requires Beautiful Soup package)

### Colorings

[*p*-centered colorings](/docs/algorithm_stages.md) are stored in a file that lists the number of colors used on the first line and each subsequent line is of the form

	[VERTEX ID]: [COLOR]

where `[VERTEX ID]` and `[COLOR]` are integers ranging from 0 to the number of vertices minus one and the number of colors minus one, respectively.

### BEAVr

As of version 2.0, CONCUSS supports visualization with
[BEAVr](https://github.com/TheoryInPractice/BEAVr).  By passing the `-e` option
to CONCUSS, a ZIP archive is created containing:

* The graph and pattern given to CONCUSS
* All graph colorings computed by the Color stage of CONCUSS
* The largest treedepth decomposition found in the Decompose stage of CONCUSS
* The dynamic programming tables computed for that treedepth decomposition
* The number of isomorphisms found in each color set

This ZIP archive can be loaded into BEAVr to create an interactive
visualization of the execution of CONCUSS.  See the BEAVr documentation for
more information.

CONCUSS can currently only create visualization output with certain
configuration options for the Compute and Combine stages.  The Compute stage
must use the KPattern class, and must be set to not reuse dynamic programming
table entries.  The Combine stage must use the InclusionExclusion method of
correcting overcounting.  For convenience, a configuration file containing the
required options is provided as `config/beavr.cfg`.

## Configuration

The algorithmic workflow in this tool is highly modular, which allows users to swap out subroutines throughout the stages of the pipeline.  A default configuration file is provided in `config/default.cfg`; this is recommended as the "best practice" for efficiency.  Users who want to experiment with algorithmic variations can find details on how to create custom config files in the [documentation](/docs/config_options.md).

## Contribution and Testing (for Developers)

We welcome contributions to CONCUSS, in the form of [Pull Requests](https://help.github.com/articles/using-pull-requests/), where you "fork" our repository and then request that we "pull" your changes into the main branch. You must have a Github account to make a contribution.

Whenever possible, please follow these guidelines for contributions:

- Keep each pull request small and focused on a single feature or bug fix.
- Familiarize yourself with the code base, and follow the formatting principles adhered to in the surrounding code (e.g. we are PEP8 compliant).
- Wherever possible, provide unit tests for your contributions. In fact, feel free to contribute a better unit testing framework :)

A series of tests are included for developers to ensure their changes do not introduce new bugs.
See the [testing documentation](/docs/testing.md) for additional instructions.

## Citation and License

**Important**: CONCUSS is *research software*, so you should cite us when you use it in scientific publications! Please see the CITATION file for citation information.
[![DOI](https://zenodo.org/badge/18042/TheoryInPractice/CONCUSS.svg)](https://zenodo.org/badge/latestdoi/18042/TheoryInPractice/CONCUSS)

CONCUSS is released under the BSD license; see the LICENSE file. Distribution, modification and redistribution, and incorporation into other software is allowed.


## Getting Help, Feature Requests, and Bug Reports

We are using [Github Issues](/issues/) for communication related to CONCUSS. Feel free to submit feature requests, ask for help (after reading the [documentation](/docs/)), or notify us of a potential bug. "Watch" our repository to keep abreast of progress and new releases.

## Acknowledgements

Development of the CONCUSS software package was funded in part by:

- the [DARPA GRAPHS](http://www.darpa.mil/program/graphs) program, through SPAWAR Grant
N66001-14-1-4063 (PI: [Blair D. Sullivan](http://www.csc.ncsu.edu/faculty/bdsullivan))
- the [Gordon & Betty Moore Foundation Data-Driven Discovery Initiative](https://www.moore.org/programs/science/data-driven-discovery), through a [DDD Investigator Award](https://www.moore.org/programs/science/data-driven-discovery/investigators) to Blair D. Sullivan ([grant GBMF4560](https://www.moore.org/grants/list/GBMF4560)).



