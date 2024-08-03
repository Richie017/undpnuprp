/**
 *  * Created by Shamil on 31-Dec-15 2:09 PM
 * Organization FIS
 */

var loadTabs = function (tab_to_load, sort_param) {
    var totalTabs = $(".tab-ajax").length;
    $(".tab-ajax").each(function () {
        var tabTitle = $("a[href='#" + $(this).attr('id') + "']")
        var tab = this;
        if (tab_to_load != undefined && tab_to_load != $(tab).attr('id')) {
            return;
        }
        url = $(this).attr('url');
        if (typeof(sort_param) != 'undefined') {
            url = url + sort_param
        } else {
            sort_param = ''
        }

        $(tabTitle).addClass('loading');
        $.ajax({
            url: url,
            type: 'get',
            success: function (html) {
                $(tab).find('div.ajax-container').html(html);
                $(tabTitle).removeClass('loading');
                $('table th input:checkbox').unbind('click');
                $('table th input:checkbox').on('click', function () {
                    var that = this;
                    $(this).closest('table').find('tr > td:first-child input:checkbox')
                        .each(function () {
                            this.checked = that.checked;
                            $(this).closest('tr').toggleClass('selected');
                        })
                        .first().change();
                });
                totalTabs -= 1;
                //$(tab).find('select.select2').select2();
                //updateSelect2Fields($(tab));
                loadBWSelect2Fields($(tab));
                $(tab).find('div.ajax-container').attr('data-url', $(tab).attr('url'));
                if ($(tab).data('print') == '1') {
                    $(tab).find('.pagination').remove();
                    $(tab).find(".search-filter").remove();

                    if (totalTabs == 0) {
                        window.print();
                    }
                }
                updateSearchFields(true);
                initialize_popup_images($(tab));
            }
        });
    });
};

$(document).on('click', ".tab-ajax .ajax-container table th.sortable", function () {
    loadTabs($(this).closest('.tab-ajax').attr('id'), $(this).find('a').attr('href'));
    return false;
});

$(document).on('click', ".reload-tab", function () {
    loadTabs($(this).closest('.tab-ajax').attr('id'));
    return false;
});

$('.ajax-container').on('click', ".btn.btn-inline-search", function () {
    if ($(this).data('ajax') == '1') {
        var container = $(this).closest('.ajax-container');
        if (container != undefined || container != null) {
            $.ajax({
                url: container.data('url'),
                data: $(this).closest('form').serialize(),
                type: 'get',
                success: function (html) {
                    $(container).html(html);
                    updateSearchFields(true);
                    loadBWSelect2Fields();

                }
            });
        }
        return false;
    }
    return true;
});