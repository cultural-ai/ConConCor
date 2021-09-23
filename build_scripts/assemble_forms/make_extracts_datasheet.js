function make_datasheet2() {

/*
from form dump csv: these are the extract global ids of control questions
*/
var c1 = [229, 191, 140, 91, 25, 459, 439, 389, 307, 276, 715, 656, 631, 574, 534, 978, 940, 898, 847, 750, 1004, 1215, 1169, 1110, 1094, 1486, 1433, 1363, 1327, 1278, 1715, 1670, 1602, 1571, 1545, 1993, 1912, 1886, 1831, 1755, 2241, 2179, 2141, 2065, 2043, 2450, 2418, 2390, 2342, 2296, 2575, 2526, 2702, 2665, 2611, 2841, 2798];

var c2 = [209, 153, 126, 65, 7, 455, 447, 359, 312, 255, 719, 652, 623, 561, 536, 966, 923, 864, 812, 795, 1022, 1236, 1183, 1104, 1054, 1468, 1432, 1385, 1318, 1253, 1739, 1671, 1609, 1590, 1511, 1956, 1948, 1859, 1829, 1775, 2206, 2174, 2123, 2051, 2045, 2464, 2412, 2394, 2312, 2295, 2562, 2540, 2723, 2677, 2626, 2823, 2793];

var c3 = [200, 151, 114, 73, 20, 462, 434, 358, 349, 278, 739, 660, 609, 586, 537, 999, 939, 874, 814, 777, 1030, 1208, 1178, 1102, 1086, 1452, 1400, 1380, 1320, 1294, 1725, 1680, 1601, 1550, 1516, 1997, 1925, 1852, 1801, 1781, 2208, 2165, 2106, 2070, 2009, 2465, 2411, 2353, 2311, 2291, 2571, 2521, 2734, 2662, 2607, 2805, 2773];

var c4 = [232, 152, 100, 98, 8, 463, 442, 397, 347, 258, 704, 653, 612, 567, 502, 997, 906, 868, 849, 759, 1040, 1210, 1185, 1138, 1057, 1484, 1409, 1356, 1306, 1290, 1708, 1694, 1640, 1583, 1544, 1958, 1938, 1872, 1835, 1772, 2228, 2175, 2101, 2087, 2023, 2474, 2414, 2350, 2340, 2276, 2585, 2525, 2703, 2650, 2614, 2801, 2774];

var c5 = [207, 168, 129, 67, 32, 499, 440, 354, 311, 288, 725, 664, 620, 563, 530, 974, 900, 886, 813, 776, 1006, 1211, 1180, 1144, 1072, 1497, 1427, 1359, 1347, 1258, 1700, 1654, 1621, 1598, 1548, 1984, 1934, 1875, 1800, 1767, 2230, 2181, 2104, 2094, 2036, 2459, 2442, 2374, 2319, 2298, 2599, 2539, 2745, 2683, 2605, 2811, 2778];


  var ss = SpreadsheetApp.getActiveSpreadsheet();

  //extracts
  var extract_sheet = ss.getSheetByName('Sheet1');
  var extracts = extract_sheet.getRange('A4:C').getValues();

  //keep a record of control extracts included
  var control_added = [false, false, false, false, false]
  var control_count = 0

  out = []
  for (i=0; i<57*50; i++){ // PULL IN extracts for sheets 1-57 only, since 58-60 are unannotated
    // note: i is in effect the global id in Datasheet1
    row = extracts[i]

    //get info
    url = row[0]
    extract = row[1]
    target = row[2]

    //re-assign ids for control extracts
    id = i
    if (c1.includes(i)){
      id = 'c1'
      control_count+=1
      if (control_added[0] == true){
        continue
      } else {
        control_added[0] = true
      }
    } else if (c2.includes(i)){
      id = 'c2'
      control_count+=1
      if (control_added[1] == true){
        continue
      } else {
        control_added[1] = true
      }
    } else if (c3.includes(i)){
      id = 'c3'
      control_count+=1
      if (control_added[2] == true){
        continue
      } else {
        control_added[2] = true
      }
    } else if (c4.includes(i)){
      id = 'c4'
      control_count+=1
      if (control_added[3] == true){
        continue
      } else {
        control_added[3] = true
      }
    } else if (c5.includes(i)){
      id = 'c5'
      control_count+=1
      if (control_added[4] == true){
        continue
      } else {
        control_added[4] = true
      }
    }

    // get transformations
    transformed = get_transformed(target, extract)
    target_compound = transformed[0]
    transformed_compound = transformed[1]
    transformed_extract = transformed[2]

    out_row = [id, target, target_compound, transformed_compound, transformed_extract, url]
    out.push(out_row)
  }

  //out
  var datasheet2 = ss.getSheetByName('extracts_datasheet');
  datasheet2.getRange("A2:F" + (1+out.length)).setValues(out);

  console.log(control_count)
}

/*
  Returns [target_compound, transformed_target, transformed_extract]
  @param {string} target:
  @param {string} extract: 5 sentence extract, each sentence separated by /n/n
*/
function get_transformed(target, extract){

  var sentences = extract.split('\n\n');

  // get the compound word (which contains the target), which we are targetting
  var regex = new RegExp(`[A-Za-z']*${target}[A-Za-z']*`, 'i');
  var target_compound = sentences[2].match(regex)[0];

  //get transformed form of target_compound
  var transformed_compound = target_compound.replace(/[A-Za-z']/g, translate);  // bolded form of actual in-context word

  // get the extract which replaces the target_compound with transformed_compound
  regex = new RegExp(target_compound);
  sentences[2] = sentences[2].replace(regex, transformed_compound);
  transformed_extract = sentences.join("\n\n")

  return [target_compound, transformed_compound, transformed_extract]
}

/*
  Return Unicode bold and italic form of a char
*/
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
