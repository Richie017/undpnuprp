/**
 *  * Created by Shamil on 31-Dec-15 1:45 PM
 * Organization FIS
 */

function collect_extra_data(cond) {
    var data_str = "";
    $('[id^=delivery_transaction_breakdown_]').each(function (i) {
        var id = $(this).prop("id").replace("delivery_transaction_breakdown_", "");
        var value = $(this).val();
        data_str += id + "=" + value + "&";
    });
    $('[id^=delivery_transaction_breakdown_reject_]').each(function (i) {
        var id = $(this).prop("id").replace("delivery_transaction_breakdown_", "");
        var value = $(this).val();
        data_str += id + "=" + value + "&";
    });
    $('[id^=delivery_transaction_breakdown_reason_]').each(function (i) {
        var id = $(this).prop("id").replace("delivery_transaction_breakdown_", "");
        var value = $(this).val();
        data_str += id + "=" + value + "&";
    });
    return data_str;
}

$(function () {
    $(document).ajaxSend(function (event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    //updateSelect2Fields();
    loadBWSelect2Fields();
    loadSelect2Legacy();

    $(".confirm-action").click(function () {
        var tthis = this;
        if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
            return false;
        }
        var request_method = "get";
        if ($(this).hasClass("require-post-method")) {
            request_method = "post";
        }
        var data = {}
        if ($(this).hasClass("require-extra-param")) {
            data["extra"] = collect_extra_data()
        }
        TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
            function () {
                $(".loader").fadeIn();
                $.ajax({
                    url: $(tthis).attr('href'),
                    type: request_method,
                    data: data,
                    success: function (data) {
                        //console.log(data);
                        if (data.success) {
                            if (data.success_url) {
                                window.location.href = data.success_url;
                            }
                            else {
                                window.location.href = window.location.href;
                            }
                        }
                        else {
                            window.location.href = $(tthis).attr('href');

                        }
                    }
                });
            },
            function () {
            });
        return false;
    });

    $(".map-update-request").click(function () {
        var tthis = this;
        if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
            return false;
        }

        TemplateAlert.Alert("Message", 'Please check device location after 30 minutes.');

        var request_method = "get";
        if ($(this).hasClass("require-post-method")) {
            request_method = "post";
        }
        var data = {}
        if ($(this).hasClass("require-extra-param")) {
            data["extra"] = collect_extra_data()
        }

        $.ajax({
            url: $(tthis).attr('href'),
            type: request_method,
            data: data,
            success: function (data) {
                if (data.success) {
                    if (data.success_url) {
                        window.location.href = data.success_url;
                    }
                    else {
                        window.location.href = window.location.href;
                    }
                }
                else {
                    window.location.href = $(tthis).attr('href');
                }
            }
        });

        return false;
    });

    //if ($.trim($(".flash_message").html()) != '') {
    //    $(".flash_message").slideDown();
    //    setTimeout(function () {
    //        $(".flash_message").slideUp();
    //    }, 5000);
    //}
    //;

    $(".search_property").change(function () {
        updateSearchFields(false);
    });

    updateSearchFields(true);

    $("body").unload(function () {
    });
});

$(function () {
    tinymce.init({
        selector: ".richtexteditor"
    });


    var message = $('#flash_message').html();
    if ($.trim(message).length > 0) {
        $('#flash_message').html('');
        var time = 5000;
        if (message.contains('btn')) time = 3600000;
        setTimeout(function () {
            // create the notification
            var notification = new NotificationFx({
                message: message,
                layout: 'growl',
                effect: 'slide',
                type: 'notice', // notice, warning or error
                ttl: time,
                onClose: function () {
                }
            });
            // show the notification
            notification.show();
        }, 100);
    }
    var current_lang = $('#language-select').val();
    $('#language-select').change(function () {
        $.ajax({
            url: '/language/setlang/',
            type: 'POST',
            data: {
                language: $(this).val(),
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (data) {
                console.log('Language Setting Successful');
                window.location = window.location.pathname.replace(
                    '/' + current_lang + '/',
                    '/' + $('#language-select').val() + '/'
                );
            },
            error: function () {
                console.log('Language Setting Failed');
            }
        });
    });
});

String.prototype.contains = function (it) {
    return this.indexOf(it) != -1;
};