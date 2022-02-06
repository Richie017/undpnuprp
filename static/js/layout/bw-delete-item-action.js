/**
 *  * Created by Shamil on 31-Dec-15 2:15 PM
 * Organization FIS
 */

$(document).on('click', ".delete-item", function () {
    if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
        return false;
    }
    var tthis = this;
    TemplateAlert.Confirm("Confirmation", "Are you sure you want to remove this item?",
        function () {
            $(".loader").fadeIn();
            $.ajax({
                url: $(tthis).attr('href'),
                type: 'get',
                data: {
                    'ids': $.map($("input[name='selection']:checked"), function (e) {
                        return $(e).attr('value');
                    }).join(",")
                },
                success: function (data) {
                    if (data.success) {
                        if (data.load != undefined && data.load == 'ajax') {
                            $(".loader").fadeOut();
                            if (data.load_tabs == true) {
                                loadTabs();
                            } else {
                                var tab = $(tthis).closest('.tab-ajax');
                                var tabTitle = $("a[href='#" + $(tab).attr('id') + "']");
                                $(tabTitle).addClass('loading');
                                tab.find('div.content').load(tab.attr('url'), function () {
                                    $(tabTitle).removeClass('loading');
                                });
                                loadTabs($(tab).attr('id'));
                                var child_names = $(tab).data('child-tabs')
                                var child_tabs = child_names.split(',');
                                for (var index = 0; index < child_tabs.length; index++) {
                                    loadTabs(child_tabs[index]);
                                }
                            }
                        } else {
                            window.location.href = window.location.href;
                        }
                    }
                    else {
                        TemplateAlert.Alert("Notification", data.message);
                        $(".loader").fadeOut();
                    }
                }
            });
        },
        function () {

        });
    return false;
});