/**
 *  * Created by Shamil on 31-Dec-15 2:11 PM
 * Organization FIS
 */
window.import_started = false;
$(document).on('click', ".load-import-modal", function () {
    if(window.import_started == true) {
        return false;
    }
    else {
        $("#id_import_file").click();
    }
    return false;
});

$(document).on("click", "#id_button_import", function (e) {
    e.preventDefault();
    $("#id_import_file").click();
});

$(document).on("change", "#id_import_file", function (e) {
    var file_name = $("#id_import_file").val();
    if(file_name.length > 0) {
        if (file_name != "") {
            window.import_started = true;
            $("#id_partial_import_form").submit();
        }
        else {
            window.import_started = false;
        }
    }
    else {
        window.import_started = false;
    }
});