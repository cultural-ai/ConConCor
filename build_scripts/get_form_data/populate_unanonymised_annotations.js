/*
a script to populate the unanonymised_annotations tab (a pre-anonymised version of the Annotations.csv deliverable)

Requires:
  * tab 'unanonyised_annotations', with headers in row 1, A-E of 'participant_id', 'extract_id', 'response', 'suggestion', 'is_control'
  * tab 'form_name:participant_id', column A containing form_names as per 'extract_ALL' tab, and column B, the corresponding participant id's 
*/

function make_datasheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // var forms_to_ignore = []; // list of form ids to ignore

  //extracts
  var extract_sheet = ss.getSheetByName('extracts_ALL');
  var extracts = extract_sheet.getRange('A2:L').getValues();

  //form numbers to participant ids
  var id_sheet = ss.getSheetByName('form_name-participant_id');
  var ids = id_sheet.getRange('A2:B15').getValues();
  // console.log(ids.length)

  /*
  create a dictionary of form_id:participant_id conversions
  */
  ftp = {}  // dict holding form_name: participant pairs
  for (i=0; i<ids.length ; i++){
    var row = ids[i];

    var form_id = row[0];
    var participant_id = row[1];

    //skip blank form_id entries
    if (form_id == ""){
      continue
    }

    ftp[form_id] = participant_id
  }

  /*
  Get useful info from extracts_ALL
  */
  out = []
  for (i=0; i<extracts.length; i++){
    var extract_row = extracts[i];

    // var form_id = extract_row[0].replace("test form ", "")
    var form_id = extract_row[0]

    // // skip extract if belongs to a form we don't care about
    // if (forms_to_ignore.includes(form_id)){
    //   continue
    // }

    var participant_id = ftp[form_id];
    var extract_global = extract_row[2];
    var extract_response = extract_row[3];
    var extract_suggestion = extract_row[4];
    // var extract_text = extract_row[5];

    // identify as control extract or not
    var extract_is_control = false;
    for (j=0; j<5; j++){
      if (extract_row[7+j] == true){
        extract_is_control = true;
        extract_global = "c" + j
      }
    }

    out_row = [participant_id, extract_global, extract_response, extract_suggestion, extract_is_control]
    // console.log(out_row)
    out.push(out_row)
  }

  //out
  var datasheet1 = ss.getSheetByName('unanonymised_annotations');
  // console.log(out.length)
  datasheet1.getRange(2,1,out.length, 5).setValues(out)
}
