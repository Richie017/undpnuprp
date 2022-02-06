/**
 *  * Created by Shamil on 31-Dec-15 2:14 PM
 * Organization FIS
 */

$(document).on("click", "#id_button_import", function (e) {
    e.preventDefault();
    $("#id_import_file").click();
});

$(document).on("change", "#id_import_file", function (e) {
    $("#id_import_file_selected").text("File selected: " + e.target.files[0].name);
});

$(document).on('click', ".load-advanced-edit-form", function (e) {
    e.preventDefault();
    var action_url = $(this).prop("href");
    var object_id = $(this).data("object-id");
    $('#advanced_edit_modal_form').find(".modal-footer").find(".btn-ok").prop('disabled', true);
    $('#advanced_edit_modal_form').find('.modal-body').html('').addClass('loading');

    if ($(this).data('wide') == '1') {
        $('#advanced_edit_modal_form').addClass('wide-modal')
    } else {
        $('#advanced_edit_modal_form').removeClass('wide-modal')
    }

    var tthis = this;
    $('#advanced_edit_modal_form')
        .find(".modal-footer")
        .find(".btn-cancel")
        .unbind('click').on('click', function () {
            $('#advanced_edit_modal_form').modal('hide');
        });

    $('#advanced_edit_modal_form')
        .find(".modal-footer")
        .find(".btn-ok")
        .unbind('click')
        .on('click', function (e) {
            $(this).prop('disabled', true);
            $('#id_advanced_edit_form').prop("action", action_url);
            $('#id_advanced_edit_form').submit();
            $(this).prop('disabled', false);
        });

    $('#advanced_edit_modal_form').unbind('shown').on('shown', function () {
//            $("#advanced_edit_modal_form").find(".progress_status_msg").html("");
        $("#advanced_edit_modal_form").find(".progress_status_msg").hide();
        $.ajax({
            url: action_url + "?object_id=" + object_id,
            type: 'get',
            success: function (data) {
                $('.btn-ok').removeAttr('disabled');
//                    $('#advanced_edit_modal_form').find('.modal-body').removeClass('loading');
                $('#advanced_edit_modal_form').find(".modal-body").html(data);
                loadBWSelect2Fields();
                //updateSelect2Fields();
                $(".date-time-picker").datetimepicker();
                $('#advanced_edit_modal_form').find('div.ajax-container').attr('data-url', $(tthis).attr('href'));
            }
        });
    });
    $("#advanced_edit_modal_form").modal('show');
    return false;
});