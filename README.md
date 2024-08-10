# Phrase and Proximity Query Search System

## Overview

This project implements a search system for phrase and proximity queries using the positional inverted indexing scheme. The Reuters-21578 dataset is used as the source of documents for indexing and querying. It contains 21,578 news stories from the Reuters newswire.

## Preprocessing the Dataset

A tokenizer is implemented to extract tokens from the news texts, and normalization operations are performed, including case-folding and removal of punctuation and numbers.

## Inverted Index

Each news article is treated as an individual document, and an inverted index is constructed. This index is composed of a dictionary of terms and their corresponding postings lists, which track the occurrences of each term across the documents. The inverted index is stored as a file, which will be used during query processing to retrieve relevant documents efficiently, eliminating the need to access the original dataset.



## Query Processing

A query processor is implemented for handling two types of queries:

- **Phrase Query:** A query where a specific sequence of words must appear in the same order within the text. For example, a phrase query is expressed as `w1 w2 ... wn` where `w1, w2, ..., wn` are single-word keywords.  

- **Proximity Query:** A query where two words must appear within a certain number of words of each other, regardless of order. For example, a proximity query is expressed as `w1 k w2`, where `k` is the maximum number of words allowed between `w1` and `w2`.  

The query processor searches the inverted index to identify and return the IDs of documents that match the query criteria, presenting the results in ascending order.

## Usage

- Python version: 3.9.13

To preprocess the dataset and build the inverted index, run the following command:

```
python preprocess.py data_path
```

- `data_path` is the path to the dataset containing SGML files.  
- `preprocess.py` processes the dataset and saves the inverted index dictionary `term_dict.pkl`.

You can make phrase and proximity queries using the following command:

```
- python query.py dict_path query
```

- `dict_path` is the path of the dictionary.  
- `query` can be phrase or proximity query.

For phrase queries, enter your text with double quotation marks. For example:
```
python query.py dict_path "old crop cocoa"
```
For proximity queries, enter your text in the following order: term1 int term2. For example:
```
python query.py dict_path old 1 cocoa
```

`query.py` prints the document IDs containing your query (if any).
