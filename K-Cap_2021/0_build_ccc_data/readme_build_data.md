# build\_ccc\_data pipeline 

Assemble the ConConCor dataset into a single data.csv

Specifically:

* combine Annotations.csv & Extracts.csv by common extract\_id values
* remove the control examples
* attach info from Metadata.csv
* create column 'text\_analysed': i.e., the extract context only, after text-analysis:
    - remove tokens with len(tokens) < 3;
    - remove punctuation;
    - remove stop words;
    - lemmatize;
    - convert anything containing 0-9 to <NUMERIC> token.

Note: the text analysis pipeline is indentical to the text-analysis applied to the larget KB pool of embeddings prior to producing word2vec embeddings

## Run
```
python3 build_data.py
```

## Requires
Annotations.csv, Extracts.csv, Metadata.csv in folder.
