/**
 * Created by Ziaul Haque on 5/16/2016.
 */

$(function () {
    'use strict';
    var _count_add = 0;
    var _count_done = 0;

    // Initialize the JQuery File Upload widget:
    var $upload_selector = $('#fileupload');
    var _upload_url = $upload_selector.attr('action');
    $upload_selector.fileupload({
        url: _upload_url,
        //The regular expression for allowed file types. For example: /(\.|\/)(gif|jpe?g|png)$/i
        acceptFileTypes: undefined,
        //The maximum allowed file size in bytes. For example: 10000000 // 10 MB
        maxFileSize: undefined,
        //By default, files are appended to the files container.Set this option to true, to prepend files instead.
        prependFiles: true,
        //By default, files added to the widget are uploaded as soon as the user clicks on the start buttons.
        // To enable automatic uploads, set this option to true.
        autoUpload: false,
        //By default, each file of a selection is uploaded using an individual request for XHR type uploads.
        //    Set this option to false to upload file selections in one request each.
        singleFileUploads: true,
        //To limit the number of files uploaded with one XHR request,
        // set the following option to an integer greater than 0. For example: 3
        limitMultiFileUploads: undefined,
        //The following option limits the number of files uploaded with one XHR request
        // to keep the request size under or equal to the defined limit in bytes. For example: 1000000
        limitMultiFileUploadSize: undefined,
        //Set this option to true to issue all file upload requests in a sequential order instead of simultaneous requests.
        sequentialUploads: false,
        //To limit the number of concurrent uploads, set this option to an integer value greater than 0. For example:3
        limitConcurrentUploads: undefined,
        //To upload large files in smaller chunks, set this option to a preferred maximum chunk size
        maxChunkSize: undefined,
        //The minimum time interval in milliseconds to calculate and trigger progress events.Default: 100
        progressInterval: 100

    });

    $upload_selector.bind('fileuploadadd', function (e, data) {
        _count_add += 1;
        //alert("added: " + _count_add);
        if (_count_add > 0) {
            _showButton(e, data);
        }
    });

    $upload_selector.bind('fileuploadfail', function (e, data) {
        _count_add -= 1;
        //alert("added: " + _count_add);
        if (_count_add < 1) {
            _hideButton(e, data);
        }
        if (_count_add === _count_done) {
            //window.location.href = window.location.href
        }
    });

    $upload_selector.bind('fileuploaddone', function (e, data) {
        _count_add -= 1;
        _count_done += 1;
        //alert("uploaded: " + _count_done);
        _updateFileTableRow(e, data);
        if (_count_add < 1) {
            _hideButton(e, data);
        }
        if (_count_add === _count_done) {
            //window.location.href = window.location.href
        }
    });

    $upload_selector.bind('fileuploadstarted', function (e, data) {
        var cancel_buttons = $(e.currentTarget).find('button.cancel');
        $(cancel_buttons).each(function (index, element) {
            $(element).attr("disabled", true);
        });
        $upload_selector.addClass('fileupload-processing');

        $(window).on('beforeunload', function () {
            return "You have unsubmitted changes.";
        });
    });

    $upload_selector.bind('fileuploadstopped', function (e, data) {
        var cancel_buttons = $(e.currentTarget).find('button.cancel');
        $(cancel_buttons).each(function (index, element) {
            $(element).attr("disabled", false);
        });
        $upload_selector.removeClass('fileupload-processing');
        $(window).off('beforeunload');
    });

    $upload_selector.bind('fileuploadsent', function (e, data) {
        var extra_field_anchor = $(data.context).find('a.load_extra_field');
        $(extra_field_anchor).addClass('disable_anchor');
    });

    $upload_selector.bind('fileuploadadded', function (e, data) {
        var $upload_fields = $('#template-upload-form');
        if ($upload_fields !== undefined && $upload_fields.length > 0) {
            $upload_fields.find('.select2-container.select2-container-multi.select2').remove();
            $upload_fields.find('.select2-container.select2').remove();
            var fields = '<td class="fade-in-1">' + $upload_fields.html() + '</td>';
            var upload_template = $(data.context).closest('.template-upload');
            upload_template.find('td:first').before(fields);
            loadBWSelect2Fields($(upload_template));
            loadTagSuggestionSelector($(upload_template)); // enable tag suggestion

            // date time picker initialization
            $(".datetimepicker").datetimepicker({
                pick12HourFormat: true
            });
        }
    });

    $upload_selector.bind('fileupload', function (e, data) {
        console.log('In fileupload');
        var inputs = data.context.find(':input');
        if (inputs.filter(function () {
                if (!this.value && $(this).prop('required')) {
                    $(this).parent().parent().find('p').removeClass('fade');
                } else if (this.value && $(this).prop('required')) {
                    $(this).parent().parent().find('p').addClass('fade');
                }
                return !this.value && $(this).prop('required')
            }).first().focus().length) {
            data.context.find('button').prop('disabled', false);
            return false;
        }
        data.formData = inputs.serializeArray();
    });
});

var _hideButton = function _hideButton(e, data) {
    $(data.form).find('button[type="submit"]').fadeOut('fast');
    $(data.form).find('button[type="reset"]').fadeOut('fast');
};

var _showButton = function _hideButton(e, data) {
    $(data.form).find('button[type="submit"]').fadeIn('fast');
    $(data.form).find('button[type="reset"]').fadeIn('fast');
};

var _updateFileTableRow = function _updateFileTableRow(e, data) {
    var result = data.result["table_row"];
    if (result !== undefined && result.length > 0) {
        $('.fileTable').dataTable().api().destroy();
        $('.fileTable tbody').prepend(result);
        _loadFileTable();
    }
};

var _loadFileTable = function loadFileTable() {
    $('.fileTable').dataTable({
        "bSort": false,
        "bFilter": true,
        "bInfo": true,
        "bJQueryUI": false,
        "bPaginate": true
    });
    InitializeDataTableCss();
    jQuery('.fileTable').wrap('<div class="dataTables_scroll" style="position:relative;"/>');
};

function InitializeDataTableCss() {
    var _dataTableSearchBox = $('.dataTables_filter label');
    var _dataTableSearchField = $('.dataTables_filter input');
    var _dataTableLengthBox = $('.dataTables_length select');
    _dataTableSearchBox.contents().get(0).remove();
    _dataTableSearchField.attr({
        'placeholder': 'Search',
        'class': 'form-control input-sm'
    });
    _dataTableSearchField.css({
        'margin-left': '-2px',
        'border-radius': '2px'

    });
    _dataTableLengthBox.css({
        'background-color': '#fff',
        'padding': '3px 10px',
        'border': '1px solid #ccc',
        'display': 'inline-block',
        'border-radius': '2px'
    });
}