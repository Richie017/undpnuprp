/**
 *  * Created by Shamil on 03-Jan-16 1:37 PM
 * Organization FIS
 */

$(function () {

    $(document).on('change', '.inline-edit-input', function () {
        $(this).closest('form').find("div.alert").slideDown();
    });


    $(document).on('click', '.btn-save-inline-form', function () {
        if ($(this).data('ajax') == '1') {
            var container = $(this).closest('.ajax-container');
            var tab = $(this).closest('.tab-ajax');
            console.log($(container).data('url'));
            console.log($(this).closest('form').serialize());
            if (container != undefined || container != null) {
                $.ajax({
                    url: $(container).data('url'),
                    data: $(this).closest('form').serialize(),
                    type: 'post',
                    success: function (html) {
                        $(container).html(html);
                        $(container).html(html);
                        loadTabs($(tab).attr('id'));
                        var child_names = $(tab).data('child-tabs')
                        var child_tabs = child_names.split(',');
                        for (var index = 0; index < child_tabs.length; index++) {
                            loadTabs(child_tabs[index]);
                        }
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

});