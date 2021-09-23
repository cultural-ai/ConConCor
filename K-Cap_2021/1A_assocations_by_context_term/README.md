## Can we identify common context tokens (between extracts) that are significantly associated with contentious or non-contentious majority vote sample? 

Run:

```
python3 PIPELINE.py
```

Requires:
* data.csv from [folder](../0_build_ccc_data/)


Output:
* majority\_vote/majority\_vote.csv: a csv of majority vote outcomes by sample;
    - possible options: 1 (contentious), 0 (non-contentious), 0.5 (no overall
      majority);
* stats/p\_response\_given\_context.csv: a csv of statistics by context word in regards to the strength of its association with contentious or non-contentious majority vote labelled samples;

## For Table xx of section 4.3 of the paper: extract a list of those significant context terms with the greatest association with contentious and non-contentious majority vote samples (examining a range of t=min count(unique target terms, context term)) 

Run:
```
python3 examine_significant_contentious.py
python3 examine_significant_non_contentious.py
```


Output:
* contentious\_terms\_various\_t.csv, non\_contentious\_terms\_various\_t.csv

