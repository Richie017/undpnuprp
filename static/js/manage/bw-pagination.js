/**
 *  * Created by Shamil on 03-Jan-16 1:35 PM
 * Organization FIS
 */

$(function() {

    $("a.all-action").removeAttr('disabled');
    $("a.multi-action").attr('disabled', 'disabled');
    $("select.pageSizeSelect").select2();
    $(document).on('change', ".pageSizeSelect", function () {
        var _size = $(this).val();
        var link = window.location.href.replace(/\?page=\d{1,}&/gi, '?');
        if ($(this).data('ajax') == '1') {
            link = $(this).closest('.ajax-container').data('url').replace(/\?page=\d{1,}&/gi, '?');
        }
        link = link.replace(/\?page=\d{1,}/gi, '');
        link = link.replace(/&page=\d{1,}&/gi, '&');
        link = link.replace(/&page=\d{1,}/gi, '');
        var new_link = '';
        if (link.indexOf('paginate_by') > -1) {
            new_link = link.replace(/paginate_by=(\d{1,})/gi, 'paginate_by=' + _size)
        } else if (link.indexOf('?') > -1) {
            new_link = link + '&paginate_by=' + _size;
        } else {
            new_link = link + '?paginate_by=' + _size;
        }

        if ($(this).data('ajax') == '1') {
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null) {
                $.ajax({
                    url: new_link,
                    type: 'get',
                    success: function (html) {
                        $(container).html(html);
                        //updateSelect2Fields();
                        loadBWSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        window.location.href = new_link;
    });

    $(document).on('click', ".page-navigation", function () {
        var _page = $(this).html();
        var link = window.location.href.replace(/\?page=\d{1,}&/gi, '?');
        if ($(this).data('ajax') == '1') {
            link = $(this).closest('.ajax-container').data('url').replace(/\?page=\d{1,}&/gi, '?');
        }
        var new_link = '';
        if (link.indexOf('paginate_by') > -1) {
            new_link = link.replace(/page=(\d{1,})/gi, 'page=' + _page)
        } else if (link.indexOf('?') > -1) {
            new_link = link + '&page=' + _page;
        } else {
            new_link = link + '?page=' + _page;
        }
        if ($(this).data('ajax') == '1') {
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null) {
                $.ajax({
                    url: new_link,
                    type: 'get',
                    success: function (html) {
                        $(container).html(html);
                        //updateSelect2Fields();
                        loadBWSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        return true;
    });

    function removeParam(sourceURL) {
        var rtn = sourceURL.split("?")[0];
        return rtn;
    }

    $(document).on('click', '.fis-paginate', function () {
        var is_ajax = $(this).data('ajax');
        var loading_url = $(this).data('url');
        if (is_ajax > 0) {
            var tab_url = $(this).closest(".ajax-container").data('url');
            var baseUrl = window.location.origin;
            var tthis = this;
            $.ajax({
                url: baseUrl + tab_url + loading_url,
                type: 'get',
                success: function (html) {
                    var tab_container = $(tthis).closest(".ajax-container");
                    var tab = $(tthis).closest(".tab-ajax");
                    $(tab_container).html(html);
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
                    //updateSelect2Fields($(tab));
                    loadBWSelect2Fields($(tab));
                    $(tab_container).attr('data-url', $(tab).attr('url'));
                    if ($(tab).data('print') == '1') {
                        $(tab).find('.pagination').remove();
                        $(tab).find(".search-filter").remove();
                    }
                    updateSearchFields(true);
                }
            });
        } else {
            console.log($(location).attr('href') + loading_url);
            window.open(removeParam($(location).attr('href')) + loading_url, '_self');
        }
    });
});