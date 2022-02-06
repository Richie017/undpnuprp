/**
 *  * Created by Shamil on 08-Mar-16 1:53 PM
 * Organization FIS
 */

var select2_values = {};
var select2_childs = {};
var select2_legacy_method_holder = {};

jQuery.cachedScript = function (url, options) {
    options = $.extend(options || {}, {
        //dataType: "script",
        cache: true,
        url: url
    });
    return jQuery.ajax(options);
};
var isArray = function (what) {
    return Object.prototype.toString.call(what) === '[object Array]';
};


var selectOptionNameFormat = function (item) {
    try {
        return item.text;
    } catch (e) {
        return "---------";
    }
};

var getProductListBasedOnRelation = function (objects, val, check_prop, return_prop) {
    for (var e = 0; e < objects.length; e++) {
        if (objects[e][check_prop] == val) {
            return objects[e][return_prop]
        }
    }
};
var products = null;
var updateSelectOptions = function (select2, parent_val, depend_property, initial, relational_object) {
    if (depend_property === '' || typeof depend_property === 'undefined' || depend_property == undefined)
        depend_property = 'parent';
    var this_id = $(select2).attr('id');
    var data = select2_values[this_id];
    var select2_reloaded_data = [];
    while (select2_reloaded_data.length) {
        select2_reloaded_data.pop();
    }
    select2_reloaded_data.push({
        id: '',
        text: '---------'
    });
    if (parent_val !== undefined && parent_val !== '' && parent_val != 0 && depend_property === 'includes_in_relation') {
        var products = getProductListBasedOnRelation(relational_object, parent_val, 'client', 'products');
        depend_property = 'id';
        $.each(data, function (object, value) {
            for (var index = 0; index < products.length; index++) {
                if (value[depend_property] == products[index]['pk']) {
                    select2_reloaded_data.push({
                        id: value.id,
                        text: value.name
                    });
                    break;
                }
            }
        });
    }
    else if (parent_val !== undefined && parent_val !== '' && parent_val != 0) {
        var check_values = $.trim(parent_val).split(',');
        $.each(data, function (object, value) {
            if (check_values.indexOf(String(value[depend_property])) > -1) {
                select2_reloaded_data.push({
                    id: value.id,
                    text: value.name
                });
            }
        });
    }
    if (select2_reloaded_data != null) {
        var selected = 0;
        var selected_index = 0;
        for (var i = 0; i < select2_reloaded_data.length; i++) {
            var value = select2_reloaded_data[i].id;
            var name = select2_reloaded_data[i].text;
            if (value == initial) {
                selected = value;
                selected_index = i;
                break;
            }
            else if (name == initial) {
                selected = value;
                selected_index = i;
                break;
            }
        }
        $(select2).select2({
            width: $(select2).attr('width') == 'null' ? 220 : $(select2).attr('width'),
            multiple: $(select2).attr('multiple') == 'multiple',
            data: select2_reloaded_data,
            initSelection: function (element, callback) {
                callback($(select2).attr('multiple') == 'multiple' ?
                    select2_reloaded_data.slice(1, select2_reloaded_data.length) : select2_reloaded_data[selected_index]);
            },
            formatSelection: function (item, container) {
                return item ? selectOptionNameFormat(item) : undefined;
            },
            formatResult: function (item, container, query) {
                var markup = [];
                markMatch(selectOptionNameFormat(item), query.term, markup);
                return markup.join("");
            }
        });
        $(select2).select2("val", selected).change();
    }
};

var filterCacheDataBasedOnDependsProperty = function (id, parent_name, depends_property) {
    try {
        var $parent = $('#id_' + parent_name);
        var parent_id_list = [];
        if (!select2_values.hasOwnProperty('id_' + parent_name)) {
            $parent.find('option').each(function () {
                parent_id_list.push(parseInt($(this).attr('value')));
            });
        } else {
            for (var i = 0; i < select2_values['id_' + parent_name].length; i++) {
                var item = select2_values['id_' + parent_name][i];
                parent_id_list.push(item['id']);
            }
        }
        var new_cache_data = [];
        for (var i = 0; i < select2_values[id].length; i++) {
            var item = select2_values[id][i];
            if (item.hasOwnProperty(depends_property) &&
                parent_id_list.indexOf(item[depends_property]) > -1) {
                new_cache_data.push(item);
            } else if (!item.hasOwnProperty(depends_property)) {
                new_cache_data.push(item);
            }
        }
        select2_values[id] = new_cache_data;
    } catch (e) {
    }
};

var loadSelect2Legacy = function (parent) {
    var bw_select2s = null;
    var version = 0;
    try {
        version = cache_config.version;
    } catch (e) {

    }
    if (parent == undefined || parent == null) {
        bw_select2s = $("input.bw-select2, select.bw-select2");
    } else {
        bw_select2s = $(parent).find("input.bw-select2, select.bw-select2");
    }
    if (bw_select2s != null) {
        bw_select2s.each(function () {
            var js_url = $(this).data('js-url');
            var relational_js_urls = $(this).data('relational-js-urls');
            var data_includes_property = $(this).data('includes-property');
            var this_select2 = this;
            var initial_val = $(this_select2).val();
            if (js_url !== undefined && js_url !== '') {
                $.cachedScript(js_url + '?' + version)
                    .done(function (script, statusText) {
                        if (statusText === 'success') {
                            //$(this_select2).select2({width: '220px'});
                            var this_id = $(this_select2).attr('id');
                            select2_values[this_id] = JSON.parse(script);

                            var depends_on = $(this_select2).data('depends-on').split(',');
                            var data_depends_property = [];
                            try {
                                data_depends_property = $(this_select2).data('depends-property').split(',');
                            } catch (e) {
                            }
                            var loadOnFirstParent = false;
                            for (var ind = 0; ind < depends_on.length; ind++) {
                                var depends_property = data_depends_property[ind];
                                var parent_name = depends_on[ind];
                                filterCacheDataBasedOnDependsProperty(this_id, parent_name, depends_property);
                                var parent_prefix =
                                    $(this_select2).data('prefix') == null ||
                                    $(this_select2).data('prefix') == '-' ? '' : $(this_select2).data('prefix');

                                var parent_id = "#id_" + parent_prefix + parent_name;
                                if (!$(parent_id).length) {
                                    parent_id = "#id_" + parent_name;
                                }

                                var parent_val = $(parent_id).val();

                                if (!select2_childs.hasOwnProperty(parent_id)) {
                                    select2_childs[parent_id] = [];
                                }
                                select2_childs[parent_id].push(this_select2);

                                if (parent_val !== '' && loadOnFirstParent === false) {
                                    loadOnFirstParent = true;
                                    updateSelectOptions(this_select2, parent_val, depends_property, initial_val);
                                }
                                if (isArray(select2_values[this_id])) {
                                    var select2ChangeMethod = function (select2) {
                                        var parent_prefix =
                                            $(select2).data('prefix') == null ||
                                            $(select2).data('prefix') == '-' ? '' : $(select2).data('prefix');
                                        var parent_val = '';
                                        var depends_on = $(select2).data('depends-on').split(',');
                                        var data_depends_property = [];
                                        var index = 0;
                                        try {
                                            for (; index < depends_on.length; index++) {
                                                if (parent_val === '') {
                                                    var parent_id = "#id_" + parent_prefix + depends_on[index];
                                                    if (!$(parent_id).length) {
                                                        parent_id = "#id_" + depends_on[index];
                                                    }
                                                    parent_val = $(parent_id).val();
                                                    if (parent_val !== '') break;
                                                }
                                            }
                                            data_depends_property = $(select2).data('depends-property').split(',');
                                        } catch (e) {
                                        }
                                        updateSelectOptions(select2, parent_val, data_depends_property[index], null);
                                    };

                                    if (data_includes_property == undefined || data_includes_property == '') {
                                        if (!select2_legacy_method_holder.hasOwnProperty(parent_id)) {
                                            select2_legacy_method_holder[parent_id] = [];
                                        }
                                        select2_legacy_method_holder[parent_id].push({
                                            method: select2ChangeMethod,
                                            param: this_select2
                                        });
                                        $(parent_id).on("change", function () {
                                            var this_id = '#' + $(this).attr('id');
                                            if (select2_legacy_method_holder.hasOwnProperty(this_id)) {
                                                for (var index = 0; index < select2_legacy_method_holder[this_id].length; index++) {
                                                    select2_legacy_method_holder[this_id][index]['method']
                                                    (select2_legacy_method_holder[this_id][index]['param']);
                                                }
                                            }
                                        });
                                    } else {
                                        var parent_value = $(parent_id).val();
                                        var relational_names = $(parent_id).data('relational-names');
                                        var relational_objects = select2_values[relational_names];
                                        if (select2_childs.hasOwnProperty(parent_id)) {
                                            if (isArray(select2_childs[parent_id])) {
                                                updateSelectOptions(this_select2,
                                                    parent_value, 'includes_in_relation', initial_val, relational_objects);
                                            }
                                        }
                                        $(this_select2).on("change", function () {
                                            var parent_id = null;
                                            var parent_prefix =
                                                $(this).data('prefix') == null ||
                                                $(this).data('prefix') == '-' ? '' : $(this).data('prefix');
                                            var parent_val = '';
                                            var depends_on = $(this).data('depends-on').split(',');
                                            var index = 0;
                                            try {
                                                for (; index < depends_on.length; index++) {
                                                    if (parent_val === '') {
                                                        parent_id = "#id_" + parent_prefix + depends_on[index];
                                                        if (!$(parent_id).length) {
                                                            parent_id = "#id_" + depends_on[index];
                                                        }
                                                        parent_val = $(parent_id).val();
                                                        if (parent_val !== '') break;
                                                    }
                                                }
                                                var relational_names = $(parent_id).data('relational-names');
                                                var relational_objects = select2_values[relational_names];
                                                if ($(this).hasClass("require-price")) {
                                                    updatePriceInput(parent_val, relational_objects, $(this));
                                                }
                                            } catch (e) {
                                            }
                                        });
                                    }
                                }
                            }
                            if (loadOnFirstParent == false) {
                                updateSelectOptions(this_select2, '', '', null);
                            }
                            var data_detail_url = $(this_select2).data('detail-url');
                            if (data_detail_url != null && data_detail_url != undefined) {
                                var this_select2_index = '#' + $(this_select2).attr('id');
                                if (!select2_legacy_method_holder.hasOwnProperty(this_select2_index)) {
                                    select2_legacy_method_holder[this_select2_index] = [];
                                }
                                select2_legacy_method_holder[this_select2_index].push({
                                    method: updateDetailSpans,
                                    param: this_select2
                                });
                                updateDetailSpans($(this_select2_index));
                            }
                        }
                    })
                    .fail(function (jqxhr, settings, exception) {
                    });
            } else {
                $(this).select2({width: '220px'});
                $(this).select2("val", $(this).val()).change();
            }
            if (relational_js_urls !== undefined && relational_js_urls !== '') {
                $.cachedScript(relational_js_urls + '?' + version).done(
                    function (script, statusText) {
                        if (statusText === 'success') {
                            var this_id = '#' + $(this_select2).attr('id');
                            var relational_names = $(this_select2).data('relational-names');
                            select2_values[relational_names] = JSON.parse(script);
                            if (relational_names === 'client_product_config') {
                                var select2RelationalMethod = function (select2) {
                                    var this_id = '#' + $(select2).attr('id');
                                    var this_value = $(select2).val();
                                    var relational_names = $(select2).data('relational-names');
                                    var relational_objects = select2_values[relational_names];
                                    if (select2_childs.hasOwnProperty(this_id)) {
                                        if (isArray(select2_childs[this_id])) {
                                            for (var index = 0; index < select2_childs[this_id].length; index++) {
                                                updateSelectOptions(select2_childs[this_id][index],
                                                    this_value, 'includes_in_relation', null, relational_objects);
                                            }
                                        }
                                    }
                                };
                                select2_legacy_method_holder[this_id].push({
                                    method: select2RelationalMethod,
                                    param: this_select2
                                });
                                $(this_select2).on("change", function () {
                                    var this_id = '#' + $(this).attr('id');
                                    if (select2_legacy_method_holder.hasOwnProperty(this_id)) {
                                        for (var index = 0; index < select2_legacy_method_holder[this_id].length; index++) {
                                            select2_legacy_method_holder[this_id][index]['method']
                                            (select2_legacy_method_holder[this_id][index]['param']);
                                        }
                                    }
                                });
                            }
                        }
                    }
                ).fail(function (jqxhr, settings, exception) {
                    console.log(exception);
                });
            }
        });
    }
};


var updatePriceInput = function (parent_val, relational_objects, $this_select2) {
    var products = getProductListBasedOnRelation(relational_objects, parent_val, 'client', 'products');
    try {
        var price = 0.0;
        for (var index = 0; index < products.length; index++) {
            if ($this_select2.val() == products[index]['pk']) {
                price = products[index]['price']
                break;
            }
        }
        $this_select2.parent().parent().parent().parent()
            .find("input[id$=unit_price]").val(price).change();
    } catch (e) {

    }
};


var updateDetailSpans = function (this_select2) {
    var detail_depend_property = $(this_select2).data('detail-depends-property');
    var detail_url = $(this_select2).data('detail-url');
    var detail_span = '#detail-span';
    var action_url = detail_url + '&' + detail_depend_property.split(',')[0] + '=' + $(this_select2).val() + '&' +
        detail_depend_property.split(',')[1] + '=' + $(this_select2).val();
    if (select2_cached_url.hasOwnProperty(this_select2.id + '_detail')) {
        if (select2_cached_url[this_select2.id + '_detail'] == action_url) {
            return;
        }
    }
    select2_cached_url[this_select2.id + '_detail'] = action_url;
    $(detail_span).remove();
    if (detail_depend_property != undefined && detail_depend_property != '') {
        var control_group = this_select2.closest('.control-group');
        $.ajax({
            'method': 'get',
            'url': action_url,
            'success': function (data) {
                var detail_span = '#detail-span';
                $(detail_span).remove();
                var items = data['items'];
                if (items.length > 0) {
                    var span = document.createElement('DIV');
                    span.setAttribute('id', 'detail-span');
                    span.setAttribute('style', 'overflow-x: auto; padding: 20px;');

                    var table = document.createElement('TABLE');
                    table.border = "1";
                    table.id = "detail-table";
                    table.setAttribute('class', 'table table-striped table-bordered table-condensed dataTable no-footer');

                    var obj = items[0];
                    var thead = document.createElement('THEAD');
                    for (var key in obj) {
                        var headerCell = document.createElement('TH');
                        var str_list = key.split('_');
                        var tag = '';
                        for (var i = 0; i < str_list.length; i++) {
                            tag += str_list[i].charAt(0).toUpperCase() + str_list[i].slice(1) + ' ';
                        }
                        $(headerCell).html(tag);
                        thead.appendChild(headerCell);
                    }
                    table.appendChild(thead);
                    var tbody = document.createElement('TBODY');

                    for (var i in items) {
                        var tr = document.createElement('TR');
                        var item = items[i];
                        for (var key in item) {
                            var td = document.createElement('TD');
                            $(td).html(item[key]);
                            tr.appendChild(td);
                        }
                        tbody.appendChild(tr);
                    }
                    table.appendChild(tbody);
                    span.appendChild(table);
                    $(control_group).append(span);
                }
            }
        });
    }
}