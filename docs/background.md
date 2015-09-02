##CONCUSS: Combatting Network Complexity Using Structural Sparsity
# Background

CONCUSS implements an algorithmic pipeline for structually sparse graphs, currently focusing on properties guaranteed in graph classes of bounded expansion.
A great deal of information about bounded expansion graphs and structural sparsity can be found in [this textbook](http://dl.acm.org/citation.cfm?id=2230458) as well as in these [two](http://www.sciencedirect.com/science/article/pii/S019566980700056X) [papers](http://www.sciencedirect.com/science/article/pii/S0195669807000571).

## Why Structural Sparsity?
Many "real-world" graph data sets are sparse, meaning they have relatively few edges compared to the number of possible edges.
More importantly, these data sets are often sparse in a specific manner.
For example, a small number of proteins in an organism have many interactions with other proteins, while most proteins only participate in a few interactions.
In the domain of Internet routing, it would highly inefficient to connect a core router in New York directly to one in Los Angeles without any intermediate routers along the way.

The underlying structure of these graphs is important to know because some hard algorithms become much easier to solve when we know something about the structure of the input.
For example, finding the size of the maximum clique, which is known to be NP-hard, can be solved in constant time on trees -- the answer is always 2!
Structural graph theory is a branch of mathematics that quantifies the structure of graphs and provides a hierarchy of classes to describe varying levels of structural sparsity.
Each class of graphs has associated algorithms that exploit the structural properies of the graph to become more efficient.
For classes that are low in the hierarchy, there is more specific structure for the algorithms to leverage, which leads to highly efficient algorithms.
On the other hand, classes that are high in the hierarchy have more relaxed structural requirements and thus include more graphs.
[Recent research](http://arxiv.org/abs/1406.2587) suggests that the class of graphs with bounded expansion lies in that "sweet spot":  low enough to be algorithmically useful but high enough to encompass a broad number of scientific data sets.

## Bounded Expansion
### Characterization
At a high level, graphs of bounded expansion must be globally sparse, but are allowed to have smaller dense pockets.
At a slightly less high level, we can identify bounded expansion classes by first grouping our graph into (arbitrary) "balls" of small radius, meaning that the distance between any two vertices in the ball is small.
Then we contract ("squish") the balls into new "super vertices".
If the graph has bounded expansion, the "super vertex graph" should not be too dense.
Alternatively, the only way to get a dense super vertex graph from a graph of bounded expansion is to squish balls of large radius.

The algorithms that exploit the bounded expansion property rely on an equivalent, though non-obviously related, tool called a *p*-centered coloring.
A *p*-centered coloring is an assignment of colors to the vertices such that every connected subgraph:

* has a color that appears exactly once __OR__
* uses *p* or more colors.

A graph has bounded expansion if, for all values of *p*, there is a *p*-centered coloring of it with a small number of colors.

### Does my graph have bounded expansion?
That is a somewhat tricky question to answer.
In the previous section, we mentioned that contracting small balls should not make the graph too dense, and that we can use a small number of colors.
But what do "small" and "too dense" mean?
Unfortunately, from a mathematical perspective, these sizes are only defined over an infinite set of graphs and it is not clear how to directly translate them to individual graphs.


In a given run of CONCUSS, we will generate one *p*-centered coloring, where the value of *p* is unrelated to the graph.
For example, in pattern counting, *p* will be one more than the number of vertices in the pattern.
The running times of the algorithms are dominated by *p* and the number of colors used, so the if the graph uses a small number of colors, these tools are appropriate.
The best way to find out for yourself is to try running the pipeline and seeing how many colors you use!
Beyond that, though, it has [been proven](http://arxiv.org/abs/1406.2587) that some random graph generators, such as Chung-Lu, the configuration model, and a generalization of Erdos-Renyi, produce graphs of bounded expansion.
If your data is well modelled by one of these generators, it is possible that this tool will be especially applicable to you.
