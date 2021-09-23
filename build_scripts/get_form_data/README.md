# Pulling data from participant-completed google forms

Steps:

* import example\_spreadsheet to google forms
* paste javascript routines into google sheets script editor scripts:

# Pull the responses from the google forms

* form\_dump.js:
    * place all google forms to extract into a folder
    * amend line 16, var folder\_id to the folder id of the folder containing the goole forms
    * amend line 15, target\_numbers to contain the google forms numbers to be extracted in this run (this can be useful, given google's max run time)

# Identify control extracts

* identify\_controls.js:
    * Place control questions url, target\_word and extract into columns A-C of tab 'controls';
    * Run script to scan 'extracts' tab for controls and populate column D+ with extract global ids;


# Produce a un-anonymised version of Annotations.csv

* ensure tab 'form\_name-participant\_id' is complete;
* copy/rename extracts\_tab to 'extracts\_ALL'
* run script 'populate\_unanonymised\_annotations.js'
