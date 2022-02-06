/**
 * Created by Mahmud on 2/7/2016.
 */

var capitalize_string = function(str, separator) {
    if (separator==undefined || separator==null) {
        separator = ' ';
    }
    var str_list = str.split(separator);
    var finale = '';
    str_list.each(function() {
       filane += this.charAt(0).toUpperCase() + this.slice(1) + ' ';
    });
    return finale;
}
