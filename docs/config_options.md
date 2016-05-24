##CONCUSS: Combatting Network Complexity Using Structural Sparsity
# Configuration options

As stated in the README, the default configuration file is generally considered "best practice".
It is also possible to make a custom configuration file by adhering to the following format:

	[color]
	low_degree_orientation  = <low degree orientation module>
	step = <step-by-step addition of edges module>
	coloring  = <coloring heuristic module>
	check_tree_depth = <tree depth checking module>
	optimization  = <optimization module, optional>
	preprocess = <preprocessing module, optional>

	[decompose]
	sweep = <decomposition generator module>

	[compute]
	k_pattern = <k-pattern module>
	table_forward = <True or False>
	table_reuse = <True or False>

	[combine]
	count = <count combiner module>

where the entries in angular brackets are replaced with the appropriate choices.

## Description of module choices
Below are options for each of the entries in the configuration files.
"Best practice" choices are **bolded**.

### `low_degree_orientation`
These modules transform an undirected graph to a directed acyclic one in a way that minimizes the maximum indegree.

- **`basic.low_degree_orientation`**

	Minimize the indegrees as the edges are being oriented.

- `basic.sandpile_orientation`

	Find one orientation of the edges and then use sandpiling to reduce the indegrees.

### `step`
These modules augment directed edges to the graph that in turn place restrictions on the subsequent coloring.
They may be executed multiple times as "steps", and thus the criteria for adding edges depends on the state of the graph at the start of the step.
In the following descriptions we write *ab* to denote a directed edge from *a* to *b*.

- `basic.trans_frater_augmentation`

	Add edges between all vertex pairs that were fraternal or transitive at the beginning of this 	step.
	Vertices *a* and *b* are fraternal if there is some vertex *c* such that *ac* and *bc* are both edges in the graph.
	Vertices *a* and *b* are transitive if there is a vertex *c* such that *ac* and *cb* are both edges in the graph.

- **`basic.truncated_tf_augmentation`**

	Add edges between some vertices that were transitive and fraternal at the beginning of this step.
	If *ac* was added during step *i* and *cb* was added at step *j*, we do not need to add *ab* until step *i+j*.

### `coloring`
These modules give heuristics about how to order the vertices of a graph to color them greedily.

- `coloring.min_deg`

	Prioritize coloring vertices with small degree.

- `coloring.max_deg`

	Prioritize coloring vertices of large degree.

- **`coloring.dsatur`**

	Use the DSATUR heuristic, which prioritizes coloring vertices that already have many colors represented among its neighbors.

### `check_tree_depth`
These modules check to see whether each subgraph containing fewer than *p* colors has a center (a color appearing exactly once).

- **`basic.check_tree_depth`**

	Currently the only checker, which uses union-find data structures.

### `optimization`
These modules take an existing *p*-centered coloring and attempt to reduce the number of colors.

- **`basic.optimization_interval`**

	Add random transitive and fraternal edges to the graph and re-run the greedy coloring.

### `preprocess`
These modules preprocess the graph in order to give a better coloring.

- `basic.trim_high_degree`

	Remove vertices whose degrees are above some threshold (default to 4 times the 4th root of *n*).
	After performing the desired coloring on the remainder of the graph, replace the removed vertices and give them each a unique color.

- **`basic.trim_low_and_high_degree`**
	Same as `basic.trim_high_degree`, but also removes vertices of degree 1 and gives them all the same (unique) color when added back.

### `sweep`
These modules determine the order in which the sets of colors are analyzed.

- `CombinationsSweep`

	Use the Python built-in `itertools.combinations` method.

- **`DFSSweep`**

	Traverse the color space in a DFS-like manner.
	For example, in a 4-centered coloring with 9 colors this would look like: {1}, {1,2}, {1,2,3}, {1,2,3,4}, {1,2,3,5}, ... {1,2,3,9}, {1,2,4}, {1,2,4,5}, {1,2,4,6}, etc.
	Store partial vertex sets in order to reduce redundant computation i.e. retain vertices with colors {1,2,3} when computing {1,2,3,4} because they will all appear in {1,2,3,5}.

### `k_pattern`
These modules represent the pieces of the pattern that can be found along root paths of the treedepth decomposition.

- `KPattern`

	Basic representation using Python built-in set data structures.

- `BVKPattern`

	Replace Python built-in sets with bitvectors as to do set operations as integer operations.

- `MemoizedKPattern`

	Memoize (store and remember) the set of all valid k-patterns for fast repeated iterations.

- **`MemoizedBVKPattern`**

	Use bitvectors for set operations and memoize the set of all valid k-patterns, join operations, forget operation, and boundary iterators.

### `table_forward`
This option controls the order in which the dynamic programming table is filled.
The value of a particular entry in the table is affected by various contributions from other entries in the table

- `True`

	For each entry, add its contributions to all other entries later in the table that it affects.

- **`False`**

	For each entry, add all the entries that contribute to it from earlier in the table.

### `table_reuse`
This option decides where to store the dynamic programming table of a particular treedepth decomposition.

- **`True`**

	Overwrite the entries of the table from the previous treedepth decomposition.

- `False`

	Allocate a new table for each treedepth decomposition

### `count`
These modules determine how double counting of patterns is resolved.

- `InclusionExclusion`

	Counts occurences of pattern that use fewer colors than the its number of vertices, and then apply the inclusion-exclusion principle to correct the overcounting.

- `ColorCounts`

	Store the number of pattern occurences for each set of colors and do not count a color set that has already been seen.

- `HybridCount`

	Store the number of pattern occurences for a small, select set of colors.

- `BVColorCounts`

	Same as `ColorCounts` but use bitvectors instead of Python sets.

- **`BVHybridCount`**

	Same as `HybridCounts` but use bitvectors instead of Python sets.

