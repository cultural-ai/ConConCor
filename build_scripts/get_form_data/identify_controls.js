/*
create tab 'control', columns A, B, C = url, target word, extract
paste the url, target word, extract of the control examples here

Columns D onwards are filled in by this script: i.e., the corresponding global IDs (from the extract_ALL) of the control examples
*/

function get_control_globals() {

  var ss = SpreadsheetApp.getActiveSpreadsheet();

  var control_sheet = ss.getSheetByName('controls');
  var controls = control_sheet.getRange('C2:C6').getValues();

  var extracts_sheet = ss.getSheetByName('extracts_ALL');
  var extracts = extracts_sheet.getRange('A2:G').getValues();

  for (c=0; c<controls.length; c++){

    var matching_globals = [];
    var control_extract = controls[c];

    //console.log(control_extract)

    for (e=0; e<extracts.length; e++){
      var extracts_extract = extracts[e][5];
      var extract_global = extracts[e][2];

      if (control_extract == extracts_extract){
        matching_globals.push(extract_global)
        matching_globals = Array.from(new Set(matching_globals))
      }

    }
    //console.log(matching_globals)
    for (m=0; m<matching_globals.length;m++){
      control_sheet.getRange(c+2, 4+m).setValue(matching_globals[m])
    }
  }
}
