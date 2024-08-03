/**
 * Created by Mahmud on 3/1/2016.
 */

var query_url_cache = '';
var value_url_cache = '';

$(document).on('keyup', $('.model_field_text'), function () {
    var value = $('.model_field_text').val();
    if (value == '' || value.match(/__$/)) {
        var app_label = $($($('.app_label_select').children()[0]).children()[0]).html();
        var model = $($($('.model_select').children()[0]).children()[0]).html();
        var url = '/role-filters/?format=json&app_label=' + app_label + '&model=' + model + '&query=' + value;
        if (url != query_url_cache) {
            query_url_cache = url;
            $.ajax({
                    method: 'get',
                    url: url,
                    success: function (data) {
                        $('.model_field_text').autocomplete({source: data['options']});
                        $('.ui-autocomplete').show();
                    }
                }
            )
            ;
        }
    }
})
;

$(document).on('keyup', $('.value_field_text'), function () {
    var value = $('.value_field_text').val();
    if (value == '' || value.endsWith('.')) {
        path_split = window.location.pathname.split('/');
        var role = path_split[path_split.indexOf('details') + 1];
        var url = '/role-filters/?format=json&role=' + role + '&query=' + value;
        if (url != value_url_cache) {
            value_url_cache = url;
            $.ajax({
                    method: 'get',
                    url: url,
                    success: function (data) {
                        $('.value_field_text').autocomplete({source: data['options']});
                        $('.ui-autocomplete').show();
                    }
                }
            )
            ;
        }
    }
})
;