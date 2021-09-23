# K-CAP\_2021

Documentation and data for the paper

Note: All code is made available under a [Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.txt)

## Investigating Annotator Agreement

[the script used to calculate the annotators agreement; and additional files used for the results analysis](agreement/)

## Investigating Context

Run the following in order to re-create the analysis and data used in section 4.3:

1. Assembly of the CCC corpus dataset:

    see [folder](0_build_ccc_data/)

    Produce data.csv, a csv of CCC corpus data merged by sample, with text-analysis of the sample contexts.

    see [more information](0_build_ccc_data/readme_build_data.md) for details.

2. Assess significant associations at token level:

    see [folder](1A_assocations_by_context_term/)

    Produce p_response_given_context.csv, a csv of statistics wrt., token and majority vote contentious/ nono-contentious co-occurrences. 

    see [more information](1A_assocations_by_context_term//README.md) for details.

3. Build an embeddings set, a reduced set of 2d embeddings via UMAP and a hierarchical clustering matrix via umap:

    see [folder](2A_KB_embeddings/)
    see [more information](2A_KB_embeddings/PIPELINE.py) for further details

    Run:
    ```
    python3 PIPELINE.py
    ```

4. View selected tokens (significantly association with contentious or non-contentious samples) on a t-SNE reduced embedding space:

    see [folder](2B_cluster_significant_contexts/)
    see [tsne_cluster.py](2B_cluster_significant_contexts/tsne_cluster.py) for details

    Run:
    ```
    python3 tsne_cluster.py
    ```

5. Assess significant associations with selected hierarchical clusters with contentious and non-contentious majority vote samples

    see [folder](2C_associations_by_cluster/)
    see [PIPELINE.py](2C_associations_by_cluster//PIPELINE.py) for details

    Run:
    ```
    python3 PIPELINE.py
    ```

    refer to [investigated clusters](2C_associations_by_cluster/investigated_clusters/) for scripts used to asses statistical association of 'cleaned' token groups
