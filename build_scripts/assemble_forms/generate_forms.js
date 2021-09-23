/* 
The source spreadsheet contains 107 blocks of 50 extacts (all extracts are unique)
The script creates:
  * forms of 50 questions corresponding to a block of 50 extracts, for the specified 'start_stop' range
    E.g., start_stop = [1,5] will produce sheets 1 tot en met 5
  * We create 6 copies of each form (7 total), so that each person can be assigned a unique form. why? because:
    i) by assigning a unique person a unique link, there's no possibiity for ambiguity of the author. E.g., if we directed 7 people to the same sheet, we'd need to ask them for id a 2nd time within the form.
*/
function build() {

  //which forms to produce and where to put 
  var start_stop = [49,52]

  var save_dir = DriveApp.createFolder('CCC_forms' + start_stop[0]) 
  //var save_dir = DriveApp.createFolder('CCC_forms_' + date.getFullYear()+ date.getMonth() + date.getDay() + "_" + date.getHours() + date.getMinutes() + date.getSeconds())

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();

  // get the data
  var title = sheet.getRange('A2:A2').getValues()[0][0];
  var description = sheet.getRange('B2:B2').getValues()[0][0];
  var data = sheet.getRange('A4:G5353').getValues();  // doesn't matter how large (as long as >= data set), the later loops control

  // clear form
  /*
  for (var i = 0; i < form.getItems().length; i++) {
    form.deleteItem(0)
  }
  */

  // number of questions for each form
  var block = 50;

  // save the form urls
  var form_urls = [];

  // save compound targets (in order of input data)
  var targets = []

  // create a new folder to save generated forms
  var date = new Date
  

  //produce form
  for (f=start_stop[0]; f<start_stop[1]+1; f++){

    console.log('test form ' + f)

    // create form and move to save dir
    var form = FormApp.create('test form ' + f + 'a');
    saveItemInFolder(form, save_dir)

    // set form data (non-questions)
    form.setTitle(title);
    form.setDescription(description);
    form.hasProgressBar();
    //form.addTextItem().setTitle('Prolific User ID');

    // get form data subset
    var formData = data.slice((f-1)*block, f*block);

    // populate questions in form
    for (i=0; i<formData.length; i++){
      var row = formData[i];

      // create question item
      var item = form.addMultipleChoiceItem();

      var question = row[1];

      //get target and replacement
      var target = row[2];
      //console.log(target)
      var regex = new RegExp(`[A-Za-z']*${target}[A-Za-z']*`, 'i');
      var target = question.split("\n\n")[2].match(regex)[0];
      targets.push(target);
      var replacement = target.replace(/[A-Za-z']/g, translate);  // bolded form of actual in-context word

      // perform target/replacement exchange on the middle sentence
      regex = new RegExp(target);
      var sentences = question.split('\n\n');
      //console.log(target)
      //console.log(replacement)
      sentences[2] = sentences[2].replace(regex, replacement);
      //console.log(sentences[2])


      item.setTitle(sentences.join("\n\n"));

      // get the multiple choices from input data
      var choices = [];
      var col_index = 3;
      while (row[col_index] != "" && col_index < row.length){
        choices.push(row[col_index]);
        col_index += 1;
      }
    
      // append multiple choices to item
      if (choices.length>0){
        item.setChoiceValues(choices);
      }

      // set question answer as required
      item.setRequired(true)

      // add text box for other terms
      form.addTextItem().setTitle('Andere omstreden termen in de context (boven)');
    }

    // add supplementary (standard) questions
    form.addSectionHeaderItem().setTitle("Via deze vragen komen we graag te weten wat u van de annotatietaak vond");
    form.addParagraphTextItem().setTitle("Was er genoeg context om te bepalen of u een term omstreden vond?");
    form.addParagraphTextItem().setTitle("Vond u het moeilijk om te beoordelen of een term omstreden is?");
    form.addParagraphTextItem().setTitle("Vond u de instructies helder?");
    form.addParagraphTextItem().setTitle("Heeft u nog andere opmerkingen of suggesties?");
    // form.addTextItem().setTitle("hoe lang duurde het om dit formulier in te vullen?");
    // form.addTextItem().setTitle("Laat uw emailadres achter als u een limited edition Cultural AI mok wilt winnen");
    form.setConfirmationMessage("Prolific Confirmation Code: 4E47C15E")

    /*
    save copies of form in form_urls
    */
    copies = ['b', 'c', 'd', 'e', 'f', 'g']
    form_url = form.getPublishedUrl()
    form_urls.push(form_url)
    for (i=0; i < copies.length; i++){
      form_copy_url = DriveApp.getFileById(form.getId()).makeCopy('test form ' + f + copies[i], save_dir).getUrl()
      form_urls.push(form_copy_url)
    }
  }

  //save form urls to a text file
  var info_file = DriveApp.createFile('form_urls.txt', form_urls.join("\n"));
  saveItemInFolder(info_file, save_dir);

  // save compount target words to file
  var info_file = DriveApp.createFile('targets.txt', targets.join("\n"));
  saveItemInFolder(info_file, save_dir);
}

function saveItemInFolder(item, folder) {
  var id = item.getId();  // Will throw error if getId() not supported.
  folder.addFile(DriveApp.getFileById(id));
}

function translate (char){
    let diff;
    if (/[A-Z]/.test (char))
    {
        diff = "??".codePointAt (0) - "A".codePointAt (0);
    }
    else
    {
        diff = "??".codePointAt (0) - "a".codePointAt (0);
    }
    return String.fromCodePoint (char.codePointAt (0) + diff);
}
