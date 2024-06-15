# About this repository
This repository provides Automatic Generation Multiple-Choice Questions System (AGQ System).  AQG System is a program source to generate panoramic questions using Knowledge Graphs based on inference rules. A panoramic question is defined as a question that includes panoramic knowledge and requires understanding the overall content when solving it. Knowledge graphs consist of entities (words) and relations (links) between the entities, and this method generate questions by extracting small subgraphs from the knowledge graphs and hiding target words (correct answer words). 

* Example of generated questions
![MCQexample](https://github.com/oku-ch/AG-MCQ-pub/assets/87764149/5fbca56b-2407-4ac6-8f87-2a5227155bd6)

# Requirement
* Python: 3.9.15
* GraphDB: 10.1.3 (https://graphdb.ontotext.com/)
* wikipedia2Vec (https://wikipedia2vec.github.io/wikipedia2vec/)
* The correct answer words to used in the questions (Please use words existing in the knowledge graphs DBpedia Japanese and Wikidata, and in pretrained embeddings of Wikipedia2Vec.)

Environments under [Anaconda for Mac](https://www.anaconda.com/download) is tested.

# Usage
Clone github directory and install requiremental libraries.

```bash
git clone git@github.com:oku-ch/AG-MCQ-pub.git
cd AG-MCQ-pub
```

Specify the path in "config.py" according to your environment.

```bash
local='** Specify the path of the files: list of correct answer words, list of prefixesand used knowledge graphs, pretrained embeddings of Wikipedia2Vec **'
local_graphs='** Specify the path of the files: the generated question graphs **'
```

Generate questions by running "main.py".

```bash
python main.py
```
Draw the graph using a graph visualization tool based on the generated CSV file of the question graph.
 
# Example of the execution result
\*\*image or gif\*\*

