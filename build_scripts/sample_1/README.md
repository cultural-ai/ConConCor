A pipeline for sampling the Europeana newspaper articles between 1890-01-01 and 1941-12-31; results in blocks.csv: a 

```
cd get_extracts
```

# 1. Catalogue Europeana newspaper issue identifiers

I.e., get a complete list of pairs of Europeana identifiers and Delpher links from the api.europeana.eu for the Europeana dataset subset corresponding to the query, query=DATA\_PROVIDER:\"National Library of the Netherlands\"&theme=newspaper

See [folder](catalogue.py)

Note: The Delpher links seem to be non-functional, but they contain the KB newspaper issue identifiers within them - this is the useful bit matching KB api query results with the Europeana set.

## Documentation 
```
python3 catalogue.py -h
```

## Run
```
python3 catalogue.py
```

## Output
europeana\_catalogue.csv


# 2. Queries

The content word sets for each of the Contentious, Alternative and Additional words can be found [here](queries/). See [Datasheet.pdf](https://github.com/cultural-ai/ConConCor/Datasheet.pdf) for more info.

Note: refer to [Datasheet.pdf](https://github.com/cultural-ai/ConConCor/Datasheet.pdf), Appendix A, for more information.


# 3. Catalogue the available KB APIs in metadata.json files.

    Specifically, update (or create) separate records of KB ocr urls that match each of the [query sets](queries/) via the jsru.kb.nl . For each query combination, sample a random selection of 200 articles for which to retrieve metadata via kb.nl/mdo/oai API.

## Documentation
```
python3 query_kb.py -h
```

###Run:
```
python3 query_kb.py -c queries/Contentious.txt queries/dates_artikel.txt -m 200 -save_dir contentious_words  
# output = contentious_words/metadata.json, contentious_words/kb_count.csv, contentious_words/eu_count.csv

python3 query_kb.py -c queries/Alternative.txt queries/dates_artikel.txt -m 200 -save_dir alternative_words  
# output = alternative_words/metadata.json, contentious_words/kb_count.csv, contentious_words/eu_count.csv

python3 query_kb.py -c queries/Additional.txt queries/dates_artikel.txt -m 200 -save_dir  
# output = additional_words/metadata.json, contentious_words/kb_count.csv, contentious_words/eu_count.csv
```

# 4. Distill those sampled records in metadata.json to a new file. 

## Documentation
```
python3 get_ocr.py -h
```

### Run
```
python3 get_ocr.py -f contentious_words/metadata.json -all -sav_dir contentious_words
python3 get_ocr.py -f alternative_words/metadata.json -all -sav_dir alternative_words
python3 get_ocr.py -f additional_words/metadata.json -all -sav_dir addtional_words
```

### output
* contentious\_words/ocr.json
* alternative\_words/ocr.json
* additional\_words/ocr.json

# 4) P(sentence) scoring

### Output: 
    * contentious\_words/scored.json
    * additional\_words/scored.json
    * alternative\_words/scored.json

# 5) Final stratified sample of extracts

I.e., collect 3000 samples, in the proportion 20:20:5:5 (contentious words: non-contentious words: Alternative words: Control samples)

Note: stratified sampling occurs over each combination target (root) word and spatial distribution (of 6).  In performing stratified sampling, number of cycles = range(1,n), a 

Thus: 
* 20/50 x 3000 = 1200 samples with a contentious word as a target word.
* 20/50 x 3000 = 1200 samples with a non-contentious word as a target word;
* 5/50 x 3000 = 300 samples with a non-contentious word as a target word;
* plus the 5 control samples.

## Documentation
```
python3 sample.py -h
```

## Run
E.g., cyclically sample 2 extracts per query + sample\_spatial.txt entry combination, where an extract has 'a' sentences either side of a sentence containing the context word, a total of 'n' examples 

```
python3 sample.py -data contentious_words/scored.json -q queries/Contentious.txt -s queries/sample_spatial.txt -a 2 -n 2 -N 1200 -sav_dir contentious_words
```

i.e., 
- identify all extracts matching sampling criteria
- 2088 extracts initially sampled for each content/time/distribution combination, extracted from possible extract pool as weighted by P(extract)
- 320 content/time query variations, shuffled and cyclically iterated to retrieve 1200 extracts, ensuring maximum spread of content/time variations. (note: 320 content/time variations since reasonable as profile\_ocr.py yields 383 prior to removal of queries)

## Run for n\_samples
Note: 19x6x6 yields 684 combinations, from which we need 1200 extracts
```
python3 sample.py -data n_samples/scored.json -q n_samples/sample_queries.txt -s n_samples/sample_spatial.txt -a 2 -n 12 N 1200 -sav_dir n_samples
```
- 1267 extracts initial sampled based on -n 1
- 63 content/ time variations within pool
- retrieved 1200 extracts, ensuring maximum spread of content/time variations

## Run for additional\_samples
Note: 18x6x6 = 648 combinations, from which we need 300
```
python3 sample.py -data additional_samples/scored.json -q additional_samples/sample_queries.txt -s additional_samples/sample_spatial.txt -a 2 -n 1 -N 300 -sav_dir additional_samples
```
- 326 extracts initial sampled based on -n 1
- 96 content/ time variations within pool
- retrieved 300 extracts, ensuring maximum spread of content/time variations

# checks

- see sampled.csv for each of p\_samples, n\_samples, additional\_samples
- also, the following, demonstrating
```
python3 profile_sampled.py -f n_samples/sampled.json -sav_dir n_samples/profile_sampled
```

# 6) Retrieve blocks 60No. of 50 samples

## go to folder
```
cd conconcor_data/form_data_prep
```
## ensure following files are in-place
- populate control.csv with 5No., samples to be present in all forms
- huc\_study.csv is all samples present in earlier huc study. We ensure no overlap with this list.
- p\_samples/sampled.csv. We take a consecutive blocks of 20 for each form (since they are in random order inherently)
- n\_samples/sampled.csv. We take a consecutive blocks of 20 for each form (since they are in random order inherently)
- additional\_samples/sampled.csv. We take consecutive blocks of 5 (since they are in random order inherently)

## pull 1200 negative, 1200 positive, 300 additional and 5 control (repeated) into blocks of 50

```
python3 make_blocks.py
```
output: blocks.csv

## check the output

- profile the numbers of p,n,a,c in each block in block.csv
- get count of query terms sampled for n and p
```
python3 profile_blocks.py
```
results:
- correct division between p,n,a,c per block
- 12 negative query words present, 62 positive query words present
