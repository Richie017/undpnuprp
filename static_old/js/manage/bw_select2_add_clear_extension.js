/**
 * Created by tareq on 12/28/16.
 */

$(function () {
    var $clear_all = $('.clear_all');
    var $add_all = $('.add_all');
    var $time_slot = $('#id_time_slot');

    $clear_all.each(function () {
        $(this).prop('checked', true);
    });

    $add_all.change(function () {
        var add_all = $(this).is(':checked');
        if (add_all == true) {
            var $clear_all_element = $(this).parent().next().children(':input');
            $clear_all_element.prop('checked', false);

            var $this_select2 = $(this).parent().parent().find('select');
            if ($this_select2.length == 0) {
                $this_select2 = $(this).parent().parent().find('input.select2-input[data-url]');
                $this_select2.select2('val', $this_select2.select2('data')).trigger('change');
            } else {
                $this_select2.find('option').each(function () {
                    $(this).prop('selected', true);
                });
                $this_select2.select2().trigger('change');
            }
        }
    });

    $clear_all.change(function () {
        var clear_all = $(this).is(':checked');
        if (clear_all == true) {
            var $add_all_element = $(this).parent().prev().children(':input');
            $add_all_element.prop('checked', false);

            var $this_select2 = $(this).parent().parent().find('select');
            if ($this_select2.length == 0) {
                $this_select2 = $(this).parent().parent().find('input.select2-input[data-url]');
                $this_select2.select2('val', '').trigger('change');
            } else {
                $this_select2.find('option').each(function () {
                    $(this).prop('selected', false);
                });
                $this_select2.select2().trigger('change');
            }
        }
    });

    $('select').change(function () {
        var total_item_length = $(this).find('option').length;
        var selected_item_length = $(this).select2("val").length;
        var $this_add_all_element = $(this).parent().parent().find('.add_all');
        var $this_clear_all_element = $(this).parent().parent().find('.clear_all');
        if (selected_item_length == 0) {
            $this_clear_all_element.prop('checked', true);
            $this_add_all_element.prop('checked', false);
        }
        else if (selected_item_length > 0 && selected_item_length < total_item_length) {
            $this_add_all_element.prop('checked', false);
            $this_clear_all_element.prop('checked', false);
        }
        else if (selected_item_length == total_item_length) {
            $this_add_all_element.prop('checked', true);
            $this_clear_all_element.prop('checked', false);
        }
    });


    $('input.select2-input[data-url]').each(function () {
        $(this).change(function (e) {
            var total_items = select2_cached_data[$(this).data('depends-on').split(',')[0]];
            var total_item_length = total_items.length;
            var selected_item_length = $(this).select2('val').length;
            var $this_add_all_element = $(this).parent().parent().find('.add_all');
            var $this_clear_all_element = $(this).parent().parent().find('.clear_all');
            if (selected_item_length == 0) {
                $this_clear_all_element.prop('checked', true);
                $this_add_all_element.prop('checked', false);
            }
            else if (selected_item_length > 0 && selected_item_length < total_item_length) {
                $this_add_all_element.prop('checked', false);
                $this_clear_all_element.prop('checked', false);
            }
            else if (selected_item_length == total_item_length) {
                $this_add_all_element.prop('checked', true);
                $this_clear_all_element.prop('checked', false);
            }
        });
    });
});