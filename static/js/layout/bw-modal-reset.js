/**
 *  * Created by Shamil on 31-Dec-15 2:08 PM
 * Organization FIS
 */
$(document).on('click', ".load-reset-modal", function () {
    $('#reset-modal-form').find('.modal-body').html('').addClass('loading');
    if ($(this).data('wide') == '1') {
        $('#reset-modal-form').addClass('wide-modal');
    } else {
        $('#reset-modal-form').removeClass('wide-modal');
    }
    var tthis = this;
    $('#reset-modal-form')
        .find(".modal-footer")
        .find(".btn-cancel")
        .unbind('click').on('click', function () {
            if ($(tthis).data('wizard') == '1') {
                $('#reset-modal-form').modal('hide');
            } else {
                $('#reset-modal-form').modal('hide');
            }
        });

    if ($(tthis).data('wizard') == '1') {
        $('#reset-modal-form')
            .find(".modal-footer")
            .find(".btn-cancel").html('Back');
        $('#reset-modal-form')
            .find(".modal-footer")
            .find(".btn-ok").html('Continue');
    }
    else {
        $('#reset-modal-form')
            .find(".modal-footer")
            .find(".btn-cancel").html('Cancel');
        $('#reset-modal-form')
            .find(".modal-footer")
            .find(".btn-ok").html('Update');
    }

    var bindModalPrimaryAction = function (tthis) {
        $('#reset-modal-form')
            .find(".modal-footer")
            .find(".btn-ok")
            .unbind('click').on('click', function () {

                if ($(tthis).data('ajax') == '0') {
                    if ($(tthis).data('callback') != null) {
                        eval($(tthis).data('callback') + '(JSON.parse(\'' + JSON.stringify($('#reset-modal-form').find('form').serializeArray()) + '\'))');
                        $(".loader").fadeOut();
                    }
                } else {
                    if ($('#reset-modal-form').find('form').valid()) {
                        $(this).attr('disabled', 'disabled');
                        $(".loader").fadeIn();
                        var data = {};
                        if ($(tthis).data('file') == '1') {
                            data = new FormData($('#reset-modal-form').find('form').get(0));
                        } else {
                            data = $('#reset-modal-form')
                                .find('form')
                                .serialize() + '&ids=' +
                            $.map($('#reset-modal-form')
                                .find('.ajax-container')
                                .find('input[type="checkbox"][name="selection"]:checked'), function (e) {
                                return $(e).attr('value');
                            }).join(",");
                        }
                        var d_url = $(tthis).attr('href');
                        var d_id = $(tthis).data('id');
                        if ($("#id_step").val() !== undefined) {
                            var _d_url = d_url.substring(0, d_url.indexOf('?') != -1 ? d_url.indexOf('?') : d_url.length) + '/' + $("#id_step").val();
                            if (d_url.indexOf("?") > -1) {
                                _d_url += "/?" + d_url.split("?").pop();
                            }
                            d_url = _d_url;
                        }
                        d_url = d_id != undefined ? d_url + "/" + d_id : d_url;
                        $.ajax({
                            url: d_url,
                            data: data,
                            type: 'post',
                            success: function (html, a, b) {

                                $('.btn-ok').removeAttr('disabled');
                                if ($('#reset-modal-form').find("#id_step").val() != undefined && parseInt($('#reset-modal-form').find("#id_total_steps").val()) >= parseInt($('#reset-modal-form').find("#id_step").val())) {
                                    $(".loader").fadeOut();
                                    $('#reset-modal-form').find('.modal-body').removeClass('loading');
                                    $('#reset-modal-form').find(".modal-header>h4").html($(tthis).data('title') == null ? "Change Password" : $(tthis).data('title'));
                                    $('#reset-modal-form').find(".modal-body").html(html);
                                    //updateSelect2Fields();
                                    loadBWSelect2Fields();
                                    $(".date-time-picker").datetimepicker({
                                        pick12HourFormat: true
                                    });
                                    return;
                                }
                                if (html.success) {
                                    $('.btn-ok').removeAttr('disabled');
                                    $('#reset-modal-form').modal('hide');
                                    if ($(tthis).data('reload') != '0') {
                                        if (html.load != undefined && html.load == 'ajax') {
                                            $(".loader").fadeOut();
                                            if (html.load_tabs == true) {
                                                loadTabs();
                                            } else {
                                                var tab = $(tthis).closest('.tab-ajax');
                                                var tabTitle = $("a[href='#" + $(tab).attr('id') + "']");
                                                $(tabTitle).addClass('loading');
                                                tab.find('div.content').load(tab.attr('url'), function () {
                                                    $(tabTitle).removeClass('loading');
                                                });
                                            }
                                        }
                                    } else {
                                        $('.btn-ok').removeAttr('disabled');
                                        window.location.href = window.location.href;
                                    }
                                    if ($(tthis).data('callback') != null) {
                                        eval($(tthis).data('callback') + '(JSON.parse(\'' + JSON.stringify(html) + '\'))');
                                        $(".loader").fadeOut();
                                    }
                                }
                                else {
                                    $('.btn-ok').removeAttr('disabled');
                                    TemplateAlert.Alert("Notification", '<div class="alert alert-error">' + html.message + "</div>");
                                }


                                $(".loader").fadeOut();
                                window.location.href = window.location.href;
                            }
                        });
                    }
                }
            });
    };
    $('#reset-modal-form').unbind('shown').on('shown', function () {
        //console.log("Trying");
        $.ajax({
            url: $(tthis).attr('href'),// + "/" + $(tthis).data('id'),
            type: 'get',
            success: function (data) {
                //console.log(data);
                $('.btn-ok').removeAttr('disabled');
                $('#reset-modal-form').find('.modal-body').removeClass('loading');
                $('#reset-modal-form').find(".modal-header>h4").html($(tthis).data('title') == null ? "Change Password" : $(tthis).data('title'));
                $('#reset-modal-form').find(".modal-body").html(data);
                //updateSelect2Fields();
                loadBWSelect2Fields();
                $(".date-time-picker").datetimepicker();
                bindModalPrimaryAction(tthis);
                $('#reset-modal-form').find('div.ajax-container').attr('data-url', $(tthis).attr('href'));
            }
        });
    });
    $("#reset-modal-form").modal('show');
    return false;
});