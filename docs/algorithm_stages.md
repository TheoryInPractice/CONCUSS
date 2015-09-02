##CONCUSS: Combatting Network Complexity Using Structural Sparsity
# Stages of the current algorithmic pipeline

The algorithmic pipeline for bounded expansion graphs generally follows four stages:

* Color
* Decompose
* Compute
* Combine

The coloring and decomposition stages are independent of the problem being solved.
That is to say, for example, the subgraph isomorphism and truncated distance problems would have their own subroutines for computing and combining, but could use the same algorithms for coloring and decomposing.

## Color
A *p*-centered coloring is an assignment of colors to the vertices such that every connected subgraph:

- has a color that appears exactly once __OR__
- uses *p* or more colors.

The *p*-centered colorings are formed by transforming the graph into a DAG (directed acyclic graph) and then augmenting it with additional (directed) edges.
Using an ordering implied by the DAG, we can quickly color the vertices.
Then we check whether this coloring is a valid *p*-centered coloring.
If not we repeat the process; after at most *O*(*p*log*p*) steps, we are guaranteed to have a *p*-centered coloring.
At the end of this stage, we remove all the extra edges that were added along the way and the graph will be returned to its original structure.

## Decompose
The *p*-centered coloring shows us how to break down the graph into small, well-structured pieces.
Each piece is part of a class that sits low on the hierarchy and thus admits very efficient algorithms.
We choose an arbitrary set of *i* colors, where *i < p*, and look at the subgraph induced on the vertices of those colors.
Note that by the definition of *p*-centered coloring, each such connected subgraph must have a color that appears exactly once.
The vertex of unique color is called the **center** of that subgraph.
We can organize the vertices of each connected component into a rooted tree using a simple procedure:

1. Pull the center up to be the root of the subgraph.
2. Recursively apply step 1 to the remaining vertices.

We call the result of this procedure a **treedepth decomposition**.
It has the special property that if *u* and *v* are adjacent in *G*, either *u* is an ancestor of *v* in the decomposition or vice-versa.
In other words, all the edges in the original graph go "up" or "down" the decomposition but not "across" it.
The **depth** of the decomposition is the height of the tree, which can be at most the number of colors we chose, *i*.
Thus, we can say that any choice of *i < p* colors from a *p*-centered coloring induces a subgraph whose treedepth is at most *i*.

## Compute
Given a treedepth decomposition from the previous step, we can use an algorithm designed for classes of bounded treedepth to compute a solution to our problem on that specific subgraph.
### Pattern Matching (subgraph isomorphism)
In the subgraph isomorphism algorithm, we exploit the fact that the edges of the graph may only occur between a vertex and its ancestors or descendants.
This greatly restricts where the pattern can occur.
For each vertex in the decomposition, we examine its **root path**, the unique path in the tree from it to the root.
Some occurrences of the pattern are contained entirely in a single root path.
Others have pieces that span multiple root paths.
Using dynamic programming, we can efficiently keep track of which pieces can be mixed, matched, and "glued together" in order to make the full pattern.
This eventually gives a final count for the number of times the pattern appears.

## Combine
For each set of colors whose size is less than *p*, we can make treedepth decompositions and run the algorithms from the previous section.
This yields a set of many solutions to individual subgraphs.
The final step is to combine these small solutions to get a solution for the entire graph.
### Pattern matching (subgraph isomorphism)
Although it may appear tempting, simply summing the counts from each set of colors will not not combine to give the proper count for the whole graph.
Suppose one particular occurence of a pattern of size four had two red vertices, one blue vertex, and one green vertex in the *p*-centered coloring.
We would count that single occurence once when considering the color set (red, blue, green, yellow), a second time when considering (red, blue, green, orange), a third time in (red, blue, green, purple), and so on.
This can be resolved by counting the number of times the pattern appears with only red, blue, and green and then use the inclusion-exclusion principle to subtract and offset the overcounting.
We can also store which smaller color combinations have already been counted and only keep track of patterns in the dynamic programming that use color combinations we have not yet seen.

