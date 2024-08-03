/**
 *  * Created by Shamil on 31-Dec-15 2:10 PM
 * Organization FIS
 */
var export_running = false;
var initial_export_btn_label = "Export";

$(document).on('click', ".load-export-modal", function () {
    var $export_button = $(this);
    initial_export_btn_label = $(this).find("span").text();
    $(this).find("span").text("Processing...");
    if (export_running == true) {
        return false;
    }
    export_running = true;
    $('#export-modal-form').find(".modal-footer").find(".btn-ok").prop('disabled', true);
    $('#export-modal-form').find('.modal-body').html('').addClass('loading');

    if ($(this).data('wide') == '1') {
        $('#export-modal-form').addClass('wide-modal')
    } else {
        $('#export-modal-form').removeClass('wide-modal')
    }

    var tthis = this;
    $('#export-modal-form')
        .find(".modal-footer")
        .find(".btn-cancel")
        .unbind('click').on('click', function () {
        $('#export-modal-form').modal('hide');
        export_running = false;
        $export_button.find("span").text(initial_export_btn_label);
    });

    $("#export-modal-form").find('button.close').unbind('click').on('click', function () {
        export_running = false;
        $(".load-export-modal").find("span").text(initial_export_btn_label);
    });

    var export_timer;
    var interval = 1000; //1 second.
    var t = 1;
    var check_download_file_ready_ajax_progress = false;

    function prepare_download_url(file_name) {
        var msg = "Data has been successfully exported. Please click <a style='color: blue;' href='/export-files/download/1/?names=" + file_name + "'>here</a> or the button bellow to download the file.<br><a class='btn btn-sm btn-danger' href='/export-files/download/1/?names=" + file_name + "'>Download file</a>";
        return msg
    }

    function search(nameKey, myArray) {
        for (var i = 0; i < myArray.length; i++) {
            if (myArray[i].name === nameKey) {
                return myArray[i];
            }
        }
    }

    function check_export_file_ready(file_name) {
        if (!check_download_file_ready_ajax_progress) {
            $.ajax({
                url: "/export-files/?name=" + file_name + "&search=1&format=json",
                type: 'get',
                success: function (data) {
                    //console.log(data);
                    if (data.total_items > 0) {
                        var array = data.items;
                        var resultObject = search(file_name.toString(), array);
                        if (resultObject !== undefined) {
                            $export_button.find("span").text(initial_export_btn_label);
                            export_running = false;
                            window.location.href = "/export-files/download/1/?names=" + file_name;
                            stop_export_timer();
                        }
                    }
                    check_download_file_ready_ajax_progress = false;
                }
            });
            check_download_file_ready_ajax_progress = true;
        }
    }

    function start_export_timer(file_name) {
        export_timer = setInterval(function () {
            check_export_file_ready(file_name);
        }, interval);
    }

    function stop_export_timer() {
        if (export_timer) {
            clearInterval(export_timer);
        }
    }

    function export_execute_handler(success_callback) {
        var data = $("#id_advanced_export_form").serialize();
        if (data == "") {
            data = {};
        }
        var form_data = $("#id_advanced_export_form").serialize();
        var search_terms = location.search.replace("?", "");

        var parsed_data = form_data;
        if (parsed_data.length > 0) {
            if (search_terms.length > 0) {
                parsed_data += "&" + search_terms;
            }
        } else {
            parsed_data = search_terms;
        }

        if ($(".kpi-filter").length) {
            $(".kpi-filter").each(function () {
                var select = $(this).parent().find('select');
                if (select.length == 0) {
                    select = this;
                }
                var key = $(select).data('kpi-filter-role');
                var value = $(select).val();
                if (Array.isArray(value)) {
                    value = value.join(',');
                }
                data[key] = value;
            });
        }
        $.ajax({
            url: "advanced-export/",
            data: parsed_data,
            type: 'get',
            success: function (data) {
                if (typeof success_callback != "undefined" && typeof success_callback == "function") {
                    success_callback(data);
                }
            }
        });
    }

    $('#export-modal-form')
        .find(".modal-footer")
        .find(".btn-ok")
        .unbind('click')
        .on('click', function (e) {
            $("#export-modal-form").modal('hide');
            $('.btn-ok').prop('disabled', true);
            $("#export-modal-form").find(".progress_status_msg").html("<h4 style='padding: 17px;'>Please wait for a while. We are generating export...</h4>");
            $("#export-modal-form").find(".progress_status_msg").show();
            var _this_object = $(this);

            export_execute_handler(function (data) {
                $("#export-modal-form").find(".modal-body").show();
                //console.log(data);
                if (data.success == true) {
                    start_export_timer(data.message);
                } else {
                    alert(data.message);
                    $export_button.find("span").text(button_label);
                    export_running = false;
                }
            });
        });

    $('#export-modal-form').unbind('shown').on('shown', function () {
        $("#export-modal-form").find(".progress_status_msg").hide();
        $('.btn-ok').removeAttr('disabled');
        $('#export-modal-form').find('.modal-body').removeClass('loading');
        $('#export-modal-form').find(".modal-body").html(export_form);
        loadBWSelect2Fields();
        //updateSelect2Fields();
        // $(".date-time-picker").datetimepicker();
        $(".datetimepicker").datetimepicker({
            pick12HourFormat: true
        });
        $('#export-modal-form').find('div.ajax-container').attr('data-url', $(tthis).attr('href'));
    });

    var export_form = "";
    var form_required = false;
    $.ajax({
        url: "advanced-export/?get_form=1",// + "/" + $(tthis).data('id'),
        dataType: "json",
        type: 'get',
        success: function (data) {

            if (data.status == "SUCCESS") {
                console.log(data);
                if (data.data.form != 0) {
                    export_form = data.data.form;
                    $("#export-modal-form").modal('show');
                } else {
                    export_execute_handler(function (data) {
                        if (data.success == true) {
                            start_export_timer(data.message);
                        } else {
                            alert(data.message);
                            $export_button.find("span").text(button_label);
                            export_running = false;
                        }
                    });
                }
            } else {

            }
        }
    });
    return false;
});