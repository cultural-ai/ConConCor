# ConConCor

The Contentious Contexts Corpus dataset. This project was carried out in the context of the EuropeanaTech Challenge for Europeana Artificial Intelligence and Machine Learning datasets.

The dataset is made available through the [CC-BY license](https://creativecommons.org/licenses/by/2.0/legalcode)

The dataset is supported with the [Project Documentation](Dataset/Project Documentation.pdf) and the [Datasheet](Dataset/Datasheet.pdf).

The dataset is split into 4 sub-sets to reduce repetition in the data (and therefore stored size), and improve clarity of the data for inspection.

1. Extracts.csv: 2720 Dutch newspaper articles extracts obtained from OCR'd versions of the Europeana Newspaper collection, as provided by KB National Library of the Netherlands
  * extract\_id: H – expert annotators, c – control samples
  * target: a target word that was used in a query
  * target\_compound: a target word found in an extract
  * target\_compound\_bolded: a bolded target word found in an extract (mathematical sans-serif bold italic small unicode charachters are used)
  * text: extract text of 5 sentences, centred around a bolded target word
  * url: a url to Delpher to view the newspaper scan and the OCR'd text 

2. Annotations.csv: Anonymised participant multi-choice responses; in being asked to define whether the target word in the given textual context is contentious (to even the slightest degree), according to present-day sensibilities
  * anonymised\_participant\_id: 'unknown\_' prefix – expert annotators, 0–398 – Prolific annotators
  * extract\_id
  * response: the multiple-choice options for each extract “Omstreden naar huidige maatstaven” (“Contentious according to current standards”), “Niet omstreden" (“Not contentious”), “Weet ik niet” (“I don’t know”), “Onleesbare OCR” ("Illegible OCR”)
  * suggestion: a suggested word that an annotator found contentios in the given extract (can be empty)
  * is\_control: boolean, True if an extract was used as a control one

3. Demographics.csv: Anonymised Prolific annotators demographic data, no demographic data was collected from the expert annotators
  * anonymised\_participant\_id
  * time\_taken: sec
  * age
  * Country of Birth
  * Current Country of Residence
  * Employment Status
  * First Language
  * Fluent languages
  * Nationality
  * Sex
  * Student Status

4. Metadata.csv: metadata corresponding to the extracts in Extracts.csv. This metadata is extracted from the KB via the provided OAI-PMH protocol
  * url: same as in Extracts.csv
  * europeana\_issue\_id
  * datestamp
  * date
  * publisher
  * spatial\_distribution
  * spatial\_origin
  * spatial\_origin


## Building the dataset

See [here](build_scripts/README.md) for instructions for recreating the dataset components: i.e., sampling extracts, auto-assembly of Google Forms, creation of the datasets files.

## K-cap 2021 paper analyses

See [here](K-Cap_2021/README.md) for instructions for performing the analyses/ creating the figures presented in K-Cap 2021 paper.
