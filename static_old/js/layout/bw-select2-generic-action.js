/**
 *  * Created by Shamil on 31-Dec-15 10:16 AM
 * Organization FIS
 */

function markMatch(text, term, markup) {
    var match = text.toUpperCase().indexOf(term.toUpperCase()),
        tl = term.length;

    if (match < 0) {
        markup.push(text);
        return;
    }

    markup.push(text.substring(0, match));
    markup.push("<span class='select2-match'>");
    markup.push(text.substring(match, match + tl));
    markup.push("</span>");
    markup.push(text.substring(match + tl, text.length));
}

function ajax_call(data_url, complete_callback) {
    $.ajax(data_url,
        {
            dataType: "json"
        }).done(complete_callback);
}

var initial_value = {};
var select2_parents = [];
var select2_parents_already_loaded = {};
var select2_watcher = {}; //{ name:[select2_watcher1,select2_watcher2,select2_watcher3] } here select2_watcher1.. are names.
var select2_cached_data = {};
var formset_select2_cached_data = {};
var select2_cached_url = {};
var select2_change_method_holder = {};
var reqProcessQueue = [];
var isRequestProcessing = false;

var disableSelect2 = function (select2) {
    $(select2).select2('enable', false);
};
var enableSelect2 = function (select2) {
    $(select2).select2('enable', true);
};
var select2ItemNameFormat = function (item) {
    // Ugly hack to show company name during order creation when the client is modern trade
    try {
        if (item.code.substring(0, 3) === 'MT-') {
            return item.code + (item.code == "---------" && item.id == "" ? "" : ": ") +
                item.company_name;
        }
        if (item['select2_string'] != undefined) {
            return item['select2_string']
        }
        return item.code + (item.code == "---------" && item.id == "" ? "" : ": ") +
            item.name + (item.description == undefined ? '' : ' ' + item.description)
    } catch (e) {
        return "---------";
    }
};
var select2Load = function (select2, result, select2_cached_data) {
    var items = [];
    for (var index = 0; index < result.items.length; index++) {
        var temp = result.items[index];
        temp['text'] = select2ItemNameFormat(temp);
        items.push(temp);
    }
    $(select2).select2({
        width: $(select2).attr('width') == 'null' ? 220 : $(select2).attr('width'),
        multiple: $(select2).attr('multiple') == 'multiple',
        data: items,
        initSelection: function (element, callback) {
            if (result != null) {
                var initValue = initial_value[$(select2).attr('id')];
                var selected = 0;
                for (var i = 0; i < items.length; i++) {
                    if ($(select2).attr('multiple') != 'multiple') {
                        var value = items[i].id;
                        var name = items[i].name;
                        if (value == initValue || name == initValue) {
                            selected = i;
                            break;
                        }
                    }
                }
                callback($(select2).attr('multiple') == 'multiple' ? items : items[selected]);
            }
        },
        formatSelection: function (item, container) {
            return item ? select2ItemNameFormat(item) : undefined;
        },
        formatResult: function (item, container, query) {
            var markup = [];
            markMatch(select2ItemNameFormat(item), query.term, markup);
            return markup.join("");
        }
    });
};

var select2APIDataLoad = function (select2, result, dummyFirstItem) {
    if (dummyFirstItem === true && $(select2).attr('multiple') != 'multiple')
        result.items.unshift({"code": "---------", "name": "", "id": ""});
    var depends_on = $(select2).data('depends-on');
    if (typeof depends_on != "undefined" && depends_on != "") {
        select2_cached_data[depends_on] = result.items;
    }
    enableSelect2(select2);
    if (result.items == undefined) return;
    select2Load(select2, result, select2_cached_data[$(select2).attr('id')]);

    var init_value = initial_value[$(select2).attr('id')];
    var selected = [];
    for (var i = 0; i < result.items.length; i++) {
        if ((typeof init_value === 'undefined' || init_value === undefined || init_value === '') &&
            ($(select2).attr('multiple') == 'multiple')) {
            selected.push(result.items[i]);
        } else {
            var id = result.items[i].id;
            var name = result.items[i].name;
            if (id == init_value || name == init_value) {
                selected.push(result.items[i]);
                break;
            }
        }
    }
    if (dummyFirstItem === true && $(select2).attr('multiple') != 'multiple')
        result.items.shift();
    if ($(select2).attr('multiple') == 'multiple') {
        $(select2).select2("data", selected).change();
    } else {
        $(select2).select2("data", selected[0]).change();
    }
};

var requestProcessTimer = null;

var proccessBWSelect2APIResponseSyncronously = function () {
    if (isRequestProcessing == false) {
        isRequestProcessing = true;
        var responseObject = reqProcessQueue.shift();
        var select2 = responseObject['select2'], result = responseObject['result'],
            dummyFirstItem = responseObject['dummyFirstItem'], isWatcher = responseObject['isWatcher'];
        enableSelect2(select2);
        if (isWatcher === true) {
            formset_select2_cached_data[$(select2).prop('name')] = result;
            var watcher_select2s = JSON.parse(JSON.stringify(select2_watcher[$(select2).prop("name")]));
            for (var j = 0; j < watcher_select2s.length; j++) {
                var child_select2 = "#id_" + watcher_select2s[j];
                enableSelect2(child_select2);
                select2APIDataLoad(child_select2, result, dummyFirstItem);
            }
        } else {
            select2APIDataLoad(select2, result, dummyFirstItem);
        }
        isRequestProcessing = false;
    }
    if (reqProcessQueue.length > 0) {
        if (requestProcessTimer != null) clearTimeout(requestProcessTimer);
        requestProcessTimer = setTimeout(function () {
            proccessBWSelect2APIResponseSyncronously();
        }, 100);
    }
};

var loadSelect2FromAPICall = function (select2, url, parameters, dummyFirstItem, isWatcher) {
    var check_url = url;
    for (var name in parameters) {
        if (parameters.hasOwnProperty(name)) {
            if (parameters[name] === '' || parameters[name] == undefined) parameters[name] = 0;
            check_url += "&" + name + "=" + parameters[name];
        }
    }
    //console.log("blocked: " + check_url);
    if (select2_cached_url.hasOwnProperty($(select2).attr('id'))) {
        if (select2_cached_url[$(select2).attr('id')] === check_url) return;
    }
    select2_cached_url[$(select2).attr('id')] = check_url;
    disableSelect2(select2);
    if (isWatcher === true) {
        for (var i = 0; i < select2_watcher[$(select2).prop("name")].length; i++) {
            disableSelect2("#id_" + select2_watcher[$(select2).prop("name")][i]);
        }
    }
    $.ajax({
        url: url,
        dataType: 'json',
        quietMillis: 250,
        data: parameters,
        success: function (result) {
            reqProcessQueue.push({
                result: result,
                select2: select2,
                dummyFirstItem: dummyFirstItem,
                isWatcher: isWatcher
            });
            proccessBWSelect2APIResponseSyncronously();
        },
        cache: true
    });
};


var select2ChangeMethod = function (child) {
    var t = {};
    var named = [];
    var data_url = $(child).data('url');
    var parent_prefix =
        $(child).data('prefix') == null ||
        $(child).data('prefix') == '-' ? '' : $(child).data('prefix');
    var depends_on = $(child).data('depends-on');
    var dependencies = depends_on.split(',');
    var properties = $(child).data('depends-property').split(",");
    if ($(child).data('named-parameters') != null) {
        named = $(child).data('named-parameters').split(",");
    }

    var no_parameter_found = true;
    for (var _dd = 0; _dd < properties.length; _dd++) {
        var child_id = "#id_" + parent_prefix + dependencies[_dd];
        if (!$(child_id).length) {
            child_id = "#id_" + dependencies[_dd];
        }
        var val = $(child_id).val();
        if (val === '') {
            val = -1;
            no_parameter_found = false;
        } else {
            no_parameter_found = false;
        }
        if (!t.hasOwnProperty(properties[_dd])) {
            t[properties[_dd]] = val;
        } else {
            if (val > 0)
                t[properties[_dd]] = val;
        }
    }
    //console.log(no_parameter_found);
    if (no_parameter_found) {
        select2Load(child, null, []);
    } else {
        for (var dd = 0; dd < named.length; dd++) {
            var nd = named[dd].split(':');
            var value = $("#id_" + parent_prefix + nd[0]).val();
            if (value == '') {
                value = -1;
            }
            data_url = data_url.replace(nd[1], value)
        }
        loadSelect2FromAPICall(child, data_url, t, true, false);
    }
};

var loadBWSelect2Fields = function (parent) {
        var all_select2s = null;
        if (parent == undefined || parent == null) {
            all_select2s = $("select.select2, input[data-url].select2-input");
        } else {
            all_select2s = $(parent).find("select.select2, input[data-url].select2-input");
        }
        if (all_select2s != null) {
            all_select2s.each(function () {
                    var this_select2 = this;
                    var data_url = $(this_select2).data('url');
                    var data_detail_url = $(this_select2).data('detail-url');
                    // Check if data-url property of select2 field is given or not
                    if ($(this_select2).hasClass("wi-filter-warehouse")) {
                        $(this_select2).change(function (e) {
                            $(".btn-inline-search").click();
                        });
                    }

                    if (data_url != null && data_url != undefined) {
                        var depends_on = $(this_select2).data('depends-on');
                        var value = $(this_select2).val();
                        if (typeof value != 'undefined' && value != '') {
                            initial_value[$(this_select2).attr('id')] = value;
                        }
                        // Check if this select2 is dependent on others value or not
                        if (depends_on == null || depends_on == "") {
                            loadSelect2FromAPICall(this_select2, data_url, {all: ''}, false, false);
                        } else {
                            var parent_prefix =
                                $(this_select2).data('prefix') == null ||
                                $(this_select2).data('prefix') == '-' ? '' : $(this_select2).data('prefix');
                            var dependencies = depends_on.split(',');
                            var properties = $(this_select2).data('depends-property').split(",");

                            for (var _d = 0; _d < dependencies.length; _d++) {
                                var d = dependencies[_d];
                                var suffix = $(this_select2).data('suffix');
                                if (suffix != false && $(this_select2).prop("name").startsWith("suffix")) {
                                    var has_parent_prefix = $(this_select2).data('parent-prefix');
                                    if (typeof has_parent_prefix !== 'undefined' && has_parent_prefix == 1) {
                                        d = $(this_select2).data('prefix') + d;
                                    }
                                    var parent = '#id_' + d;
                                    var parent_value = $(parent).val();
                                    if (!select2_watcher.hasOwnProperty(d)) {
                                        select2_watcher[d] = [];
                                        select2_watcher[d + '_value'] = parent_value;
                                        $(parent).val(parent_value - 1);
                                        $(parent).on("change", function (e) {
                                            var this_select = this;
                                            if (select2_watcher[$(this_select).prop("name")] != undefined &&
                                                select2_watcher[$(this_select).prop("name")].length >= 1) {

                                                var _dependentFirst = $("#id_" + select2_watcher[$(this_select).prop("name")][0]);
                                                var data_url = _dependentFirst.data("url");

                                                var properties = _dependentFirst.data('depends-property').split(",");
                                                var t = {};
                                                var named = [];
                                                if (_dependentFirst.data('named-parameters') != null) {
                                                    named = _dependentFirst.data('named-parameters').split(",");
                                                }
                                                for (var dd = 0; dd < properties.length; dd++) {
                                                    var value = -1;
                                                    if ($(this_select).prop("name").indexOf(named[dd]) > -1) {
                                                        value = $(this_select).val();
                                                    } else {
                                                        value = $("#id_" + named[dd]).val();
                                                    }
                                                    if (value === '') value = -1;
                                                    t[properties[dd]] = value;
                                                }
                                                loadSelect2FromAPICall(this_select, data_url, t, true, true);
                                            }
                                        });
                                    }
                                    if (select2_watcher[d].indexOf($(this_select2).prop("name")) <= -1) {
                                        select2_watcher[d].push($(this_select2).prop("name"));
                                    }
                                    if (formset_select2_cached_data[d] != undefined) {
                                        select2APIDataLoad(this_select2, formset_select2_cached_data[d], false);
                                    }
                                } else {
                                    var parent_id = "#id_" + parent_prefix + d;
                                    if (!$(parent_id).length) {
                                        parent_id = "#id_" + d;
                                    }
                                    if ($(parent_id).data('depends-on') == null || $(parent_id).data('depends-on') == "") {
                                        if (select2_parents_already_loaded[parent_id] != true)
                                            select2_parents.push(parent_id);
                                    }
                                    if (!select2_change_method_holder.hasOwnProperty(parent_id)) {
                                        select2_change_method_holder[parent_id] = [];
                                    }
                                    select2_change_method_holder[parent_id].push({
                                        method: select2ChangeMethod,
                                        child: this_select2
                                    });
                                    $(document).on('change', parent_id, function () {
                                        if (select2_change_method_holder.hasOwnProperty(parent_id)) {
                                            for (var index = 0; index < select2_change_method_holder[parent_id].length; index++) {
                                                select2_change_method_holder[parent_id][index]['method']
                                                (select2_change_method_holder[parent_id][index]['child']);
                                            }
                                        }
                                    });
                                }

                            }
                        }
                    } else {
                        if ($(this).hasClass("order-select2")) {
                            $(".select2.order-select2").css("width", "220px");
                            $(this).select2({width: '220px'});
                        } else {
                            $(this).css("width", "220px");
                            $(this).select2({width: '220px'});
                            //$(this).select2();
                        }
                    }

                    // bind assignment update field change event to show warning message
                    if ($(this_select2).hasClass('has-helptext')) {
                        var _message = $(this_select2).data("message");

                        if ($(this_select2).parent().parent().is('tr')) {
                            $(this_select2).closest('table').attr('style', 'width: 70% !important');
                            let _message_html = "<td><span style='width: 90%;float: right;" +
                                "border: 1px solid green; background-color: lightgrey; padding: 15px; " +
                                "color: grey' id='message_" + $(this_select2).attr("id") + "'>Important Note!<br>"
                                + _message + "</span></td>";
                            $(this_select2).parent().parent().append(_message_html);
                        } else {
                            let _message_html = "<span style='width: 50%;float: right;" +
                                "border: 1px solid green; background-color: lightgrey; padding: 15px; " +
                                "color: #401e1e' id='message_" + $(this_select2).attr("id") + "'>Important Note!<br>"
                                + _message + "</span>";
                            $(this_select2).parent().append(_message_html);
                        }
                    }
                }
            );
            for (var i = 0; i < select2_parents.length; i++) {
                $(select2_parents[i]).val($(select2_parents[i]).find(":selected").val()).change();
                select2_parents_already_loaded[select2_parents[i]] = true;
            }
            select2_parents = [];

            for (var key in select2_watcher) {
                if (select2_watcher.hasOwnProperty(key) && key.indexOf("_value") < 0) {
                    var select2_watcher_item = "#id_" + key;
                    if (select2_watcher[key + "_value"] != -100) {
                        $(select2_watcher_item).val(select2_watcher[key + "_value"]).trigger("change");
                        select2_watcher[key + "_value"] = -100;
                    }
                    if (typeof select2_watcher[$(select2_watcher_item).prop("name")] !== 'undefined') {
                        for (var index = 0; index < select2_watcher[$(select2_watcher_item).prop("name")].length; index++) {
                            var $dependantThis = "#id_" + select2_watcher[$(select2_watcher_item).prop("name")][index];
                            $($dependantThis).on("change", function (e) {
                                if ($(this).hasClass("require-price")) {
                                    var _this_object = $(this);
                                    _this_object.prop("disabled", true);
                                    var id = $(this).val();
                                    if (id === '') id = 0;
                                    var data_url = "/products/?format=json&search=1&id=" + id;
                                    ajax_call(data_url, function (data) {
                                        _this_object.prop("disabled", false);
                                        try {
                                            var price_type = 'price_' + _this_object.data('price-type');
                                            var price_val = data.items[0][price_type];
                                            _this_object.parent().parent().parent().parent()
                                                .find("input[id$=unit_price]").val(price_val).change();
                                        } catch (e) {

                                        }
                                    });
                                }
                            });
                        }
                    }
                }
            }
        }

        var price_required_select2 = $('.require-unit-price');
        $(price_required_select2).on('change', function (e) {
            var _this_object = $(this);
            _this_object.prop("disabled", true);
            var id = $(this).val();
            if (id === '') id = 0;
            var data_url = "/products/?format=json&search=1&id=" + id;
            ajax_call(data_url, function (data) {
                _this_object.prop("disabled", false);
                try {
                    var price_type = 'price_' + _this_object.data('price-type');
                    var price_val = data.items[0][price_type];
                    _this_object.parent().parent().parent().parent()
                        .find("input[id$=unit_price]").val(price_val).change();
                } catch (e) {

                }
            });
        });
    }
;

var updateSearchSelectField = function (id, data_url) {
    var ttthis = id;
    $(ttthis).empty().select2('enable', false);
    $.ajax({
        url: data_url,
        type: 'get',
        success: function (result) {
            select2_cached_data[$(ttthis).attr('id')] = result.items;
            $(ttthis).select2('enable', true);
            var data = result.items;
            $.each(data, function (index, value) {
                $(ttthis).append('<option value="' + data[index].code + '">' + data[index].name + '</option>');
            });
            $(ttthis).val(data[0].code).change();
        }
    });
};

var updateSearchFields = function (clear) {
    var api_link = $(".search_property option:selected").data('api-link');
    if ($(".search_property option:selected").data('is-range') == 'True') {
        $("form.search-form").find(".datetimepicker").datetimepicker({
            pick12HourFormat: true
        });
        $(".search-form").find('span.add-on').show();
        $("div.query_1").attr('placeholder', 'From').show();
        $("div.query_2").attr('placeholder', 'To').show();
        $("div.query_3").hide();
        $("div.query_4").hide();
    } else if (api_link === null || api_link === '' || typeof api_link === 'undefined') {
        $("div.query_3").attr('placeholder', 'Search Term').show();
        $("div.query_1").hide();
        $("div.query_2").hide();
        $("div.query_4").hide();
        $(".search-form").find('span.add-on').hide();
    } else {
        $("div.query_4").attr('placeholder', 'Search Term').show();
        $("div.query_1").hide();
        $("div.query_2").hide();
        $("div.query_3").hide();
        $(".search-form").find('span.add-on').hide();
        updateSearchSelectField("#query_4", api_link);
    }
    if (clear == true) {
        $(".search-input").val('');
    }
};
