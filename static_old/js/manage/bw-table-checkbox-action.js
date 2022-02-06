/**
 *  * Created by Shamil on 03-Jan-16 10:09 AM
 * Organization FIS
 */

$(function () {

    $(document).on('click', 'table th input:checkbox', function () {
        var that = this;
        $(this).closest('table').parent().parent().find('table:last').find('tr > td:first-child input:checkbox')
            .each(function () {
                this.checked = that.checked;
                if (that.checked) {
                    $(this).closest('tr').addClass('selected');
                } else {
                    $(this).closest('tr').removeClass('selected');
                }
            })
            .first().change();
    });

    $(document).on('click', 'table tr > td:first-child input:checkbox', function () {
        if (this.checked) {
            $(this).closest('tr').addClass('selected');
        } else {
            $(this).closest('tr').removeClass('selected');
        }
    });

    $(document).on('change', 'table tr td input:checkbox', function () {
        var total = $('table tr td input:checkbox');
        var selected = $('table tr td input:checkbox:checked');
        var $checkalltoggle = $('input.checkalltoggle');
        if (selected.length < total.length) {
            if ($checkalltoggle[0].checked) {
                $checkalltoggle[0].checked = false;
                $checkalltoggle
                    .next('span')
                    .find('button .icon.cb-icon-check')
                    .css('display', 'none');
                $checkalltoggle
                    .next('span')
                    .find('button .icon.cb-icon-check-empty')
                    .css('display', 'inline-block');
            }
        }
        else if (selected.length == total.length && total.length > 0) {
            if (!$checkalltoggle[0].checked) {
                $checkalltoggle[0].checked = true;
                $checkalltoggle
                    .next('span')
                    .find('button .icon.cb-icon-check')
                    .css('display', 'inline-block');
                $checkalltoggle
                    .next('span')
                    .find('button .icon.cb-icon-check-empty')
                    .css('display', 'none');
            }
        }
    });

    $(document).on('change', 'table tr td input:checkbox', function () {
        var total = $('table tr td input:checkbox:checked');
        var $partial_edit_action = $("a.partial-edit-action");
        if (total.length == 1) {
            $partial_edit_action.removeAttr('disabled');
            $partial_edit_action.each(function () {
                var cbox = $("input[name='selection']:checked");
                var data_url = $(this).attr('href').split('//')[0];
                var link = data_url + "//" + $(cbox).val();
                $(this).attr('href', link);
            });
        } else {
            $partial_edit_action.attr('disabled', 'disabled');
        }
    });


    $(document).on('change', 'table tr td input:checkbox', function () {
        var total = $('table tr td input:checkbox:checked');
        if (total.length > 0) {
            $("a.delete-item").removeAttr('disabled');
        } else {
            $("a.delete-item").attr('disabled', 'disabled');
        }
    });

    $(document).on('change', 'table tr td input:checkbox', function () {
        var cbox = this;
        var total = $('table tr td input:checkbox:checked');
        var $single_action = $("a.single-action");
        var $multi_action = $("a.multi-action");
        if (total.length == 1) {
            $single_action.removeAttr('disabled');
            $single_action.each(function () {
                $(this).attr('href', $(this).data('url').replace("{0}", $(cbox).val()));
            });
        } else {
            $single_action.attr('disabled', 'disabled');
        }
        if (total.length > 0) {
            $multi_action.removeAttr('disabled');
            $multi_action.each(function () {
                if ($(this).data('url') != undefined) {
                    $(this).attr('href', $(this).data('url').replace("{0}", $.map($('table tr td input:checkbox:checked'), function (e, i) {
                        return $(e).val();
                    }).join(",")));
                }
            });
        } else {
            $multi_action.attr('disabled', 'disabled');
        }
    });
});