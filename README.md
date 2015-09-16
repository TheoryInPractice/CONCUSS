#CONCUSS: Combatting Network Complexity Using Structural Sparsity

CONCUSS is a software tool for large scale graph analytics.  The efficiency and scalability of CONCUSS come from exploiting the underlying [structure and sparsity](/docs/background.md) of the data.  It allows users to count the number of occurences of a specific pattern within a graph (i.e. subgraph isomorphism counting).  These counts are a building block for more complicated scientific analysis, such as motif counting and graphlet degree signature creation.  

## Command line usage

    ./concuss.py [OPTIONS] graph pattern [config]

Count the number of subgraphs of "graph" which are isomorphic to "pattern".

Positional arguments:

* `graph` - filename of the host graph
* `pattern` - filename or basic pattern. Basic pattern specified as: `pattern_nameint` or `pattern_nameint,int`. The ints specify number of vertices. See example below.
* `config` - filename of the configuration settings (defaults to `config/default.cfg`)

Optional arguments:

* `-h, --help` - show help message and exit
* `-o [OUTPUT], --output [OUTPUT]` - filename of the result
* `-v, --verbose` - verbose output
* `-p, --profile` - profile function calls
* `-c [COLORING], --coloring [COLORING]` - filename of existing *p*-centered
  coloring.  When this option is not selected, CONCUSS will find a coloring itself
* `-C, --coloring-no-verify` - same as -c but do not verify correctness of existing coloring


Example command:

Using pattern file:
	
	./concuss.py testing/graphs/karate.txt testing/graphs/motifs/K3.txt

Using basic pattern:
	
	./concuss.py testing/graphs/karate.txt clique3
	
Example output:

	Number of occurrences of H in G: 270

This means that there are 270 isomorphisms of K3 (a triangle) in the karate network.  Since the triangle has 3 automorphisms, the karate network has 90 distinct triangles.

Using bipartite basic pattern:
	
	./concuss.py testing/graphs/karate.txt biclique2,2
	
Example output:
	
	Number of occurrences of H in G: 288
	
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

CONCUSS supports reading data files for the host and pattern graphs in the following formats:

* Edgelist (.txt)
* GML (.gml)
* LEDA (.leda)
* GraphML (.graphml) (requires Beautiful Soup package)
* GEXF (.gexf) (requires Beautiful Soup package)

[*p*-centered colorings](/docs/algorithm_stages.md) are stored in a file that lists the number of colors used on the first line and each subsequent line is of the form

	[VERTEX ID]: [COLOR]

where `[VERTEX ID]` and `[COLOR]` are integers ranging from 0 to the number of vertices minus one and the number of colors minus one, respectively.

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



