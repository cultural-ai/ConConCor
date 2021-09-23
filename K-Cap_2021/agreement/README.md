IAA.ipynb – script to generate the additional files necessary for the inter-annotator agreement analysis:

1. batches_annotators.json – a list of annotators per batch (which set of samples was labelled by which annotator)
2. k_alpha_per_batch_4_options.csv – Krippendorff's alpha per batch for all 4 options
3. k_alpha_per_batch_2_options.csv – Krippendorff's alpha per batch for 2 options ('Omstreden' and 'Niet omstreden'), other responses are filtered out, so this data has missing values; the purpose of it is to check the agreement between annotators who could decide whether a term was contentious or non-contentious in a given sample (without options 'I don't know' or 'Bad OCR')
4. pairwise_agreement.csv – Krippendorff's alpha for every pair of annotators in a batch
5. mean_alpha_per_annotator.csv – mean Krippendorff's alpha per annotator (taking all the alpha values from annotator's pairs)
6. perc_agreement.csv – percentage agreement between annotators per sample 
7. k_alpha_per_batch_2_options_filtered_alpha.csv – Krippendorff's alpha per batch for 2 options without annotators whose mean K alpha lower than 0.2
8. k_alpha_per_batch_2_options_filtered_controls.csv – Krippendorff's alpha per batch for 2 options without annotators who got 3 or more control questions 'wrong' (different from experts)
