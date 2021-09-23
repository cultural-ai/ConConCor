/* 
Google Apps Script routine to pull the data from forms.

Requires the tabs (to dump data into. overwrites anything in these sheets):
* 'extracts' 
* 'optionals'

handles multiple annotations of a single sheet, by appending a suffix.
E.g., subsequent (after the first) annotations of sheet 1a, would be labelled 1a_1, 1a_2, etc
*/

function dump() {

  // CASE-SPECIFIC INPUT VARIABLES
  var target_numbers = [28, 38, 32, 34, 35, 36, 37, 40, 43, 44, 45, 48, 49, 55 ]
  var folder_id = "sdfasdf_sadf"

  // dir containing forms
  var files = DriveApp.getFolderById(folder_id).getFiles();
  var data = [];
  var optional = [];

  var forms_counter = 0
  while (files.hasNext()) {

    var file_id = files.next().getId();
    var file_url = DriveApp.getFileById(file_id).getUrl()
    var file_type = DriveApp.getFileById(file_id).getMimeType();
    var file_name = DriveApp.getFileById(file_id).getName()

    // get current file 
    if (file_type == 'application/vnd.google-apps.form'){
      var file_number =  parseInt(file_name.match(/\d+/)[0], 10)
    } else {
      var file_number = -1
    }

    // only work with google forms
    if (file_type == 'application/vnd.google-apps.form' && target_numbers.includes(file_number)){

      var form_responses = FormApp.openById(file_id).getResponses();

      // form_responses.length is the number of annoation submissions for each form.
      if (form_responses.length > 0){
        console.log(form_responses.length + " responses in form " + file_name)

        var fns = ""  //file name suffix - to denote different participants

        for (r=0; r<form_responses.length; r++){
          form_response = form_responses[r]
          forms_counter++  // increment forms considered

          // handle suffix for multiple participants
          if (r>0){
            fns = "_" + r
          }

          var items_responses = form_response.getItemResponses();
          // iterate over extraxts
          for (var j = 0; j < 100; j+=2) {
            var item_response = items_responses[j].getResponse();
            var item_suggestions = items_responses[j+1].getResponse();

            // file name, form item number, extract number, item response, item title
            data.push([file_name+fns, j/2, (file_number-1)*50+j/2, item_response, item_suggestions, items_responses[j].getItem().getTitle(), file_url]);
          } 

          // form name, optional question number, question response
          for (var j = 100; j < 104; j++){
            var item_response = items_responses[j].getResponse();
            optional.push([file_name+fns, j-99, item_response, file_url]);
          }
        }
          
      // report sheets with multiple responders
      } else if (form_responses.length == 0){
        console.log('form ' + file_name + ' has 0 responders')
      }
    }
  }

  var last_line = 1 + 50*forms_counter
  SpreadsheetApp.getActive().getRange("extracts!A2:G" + last_line).setValues(data);

  last_line = 1 + 4*forms_counter
  SpreadsheetApp.getActive().getRange("optionals!A2:D" + last_line).setValues(optional);

}
