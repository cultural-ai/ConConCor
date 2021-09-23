# Instructions for creating the ConConCor dataset

All code is made available under a [Apache](http://www.apache.org/licenses/LICENSE-2.0.txt) license.

Scripts can be found in [parent folder](../build_scripts/).

## Initial sampling of approx 200 ocr articles + metadata per content/data query combination for 'contentious words', 'alternative words' and 'additional words'. (refer to datasheets)

```
cd sample_1
python3 PIPELINE.py
```

see [sample\_1/PIPELINE.py](sample_1/PIPELINE.py) for details.


## Scoring of P(sentence) based on bigram probabilities from sample\_1/PIPELINE.py


## Sample 5-sentence extracts of centred on contentious, alternative and additional target words according to the ratios 20:20:5

```
cd sample_2/
python3 PIPELINE.py
```

see [sample\_2/PIPELINE.py](sample_2/PIPELINE.py) for details.

## Build blocks (batches) of sequential 50 annotations, sampled w/o replacement from previous sample step

Requires:

* [control.csv](build_forms/control.csv), a csv of url, query word, text for each control sample

Run:

```
python3 make_blocks.py
```

## Assemble the google forms from the batches

see [here](assemble_forms/README.md) for details

## Web interface re-directing prolific users to assembled google forms

Code for generating the flask web interface can be found [here](flask_interface/)

## Retrieve the annotations

see [here](get_form_data/README.md) for details

## Build the datasets

refer to and run [create\_datasets.py](build_deliverable_datasets/create_datasets.py)
