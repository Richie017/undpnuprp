/**
 *  * Created by Shamil on 03-Jan-16 1:56 PM
 * Organization FIS
 */

$(function () {

    $(document).on('click', '.btn-inline-search', function () {
        if ($(this).data('ajax') == '1') {
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null) {
                $.ajax({
                    url: $(container).data('url'),
                    data: $(this).closest('form').serialize(),
                    type: 'get',
                    success: function (html) {
                        $(container).html(html);
                        //updateSelect2Fields();
                        //loadBWSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        return true;
    });

    var addSearchProperty = function (tthis) {
        var values = "None";
        var names = "None";
        var api_link = $(".search_property option:selected").data('api-link');
        if ($(".search_property option:selected").data('is-range') == 'True') {
            var q1 = $(tthis).closest("form").find("#query_1").val();
            var q2 = $(tthis).closest("form").find("#query_2").val();
            if (q1 == null || q1 == "") {
                $(tthis).closest("form").find("#query_1").focus();
                return false;
            } else {
                q1 = q1 + " 00:00:00"
            }
            if (q2 == null || q2 == "") {
                $(tthis).closest("form").find("#query_2").focus();
                return false;
            } else {
                q2 = q2 + " 23:59:59"
            }
            values = q1 + "," + q2;
            names = values;
        } else if (api_link == undefined || api_link === null || api_link === '') {
            values = $(tthis).closest("form").find("#query_3").val();
            names = values;
            if (values == null || values == "") {
                $(tthis).closest("form").find("#query_3").focus();
                return false;
            }
        } else {
            values = $('#query_4').val();
            names = $("#query_4 option:selected").text();
        }
        //if (values == null || values == "") {
        //    values = "None";
        //}
        //if (names == null || names == "") {
        //    names = "None";
        //}
        $(tthis).closest("form").find(".search-input").val('');

        var searchType = $(tthis).closest("form")
            .find(".search_property option:selected")[0]
            .innerHTML.replace(/\s/g, "");
        var searchKey = $(tthis).closest("form")
            .find(".search_property option:selected")
            .val();
        var parent = document.getElementById("search-item-template");
        var childNodes = parent.getElementsByClassName('search-item-container');
        for (var index = 0; index < childNodes.length; index++) {
            try {
                var childNode = childNodes[index];
                var second = childNode.getElementsByClassName('id_template_label')[0];
                var addedItems = childNode.getElementsByClassName('search-value-item');
                for (var i = 0; i < addedItems.length; i++) {
                    var node = addedItems[i];
                    var addedValue = node.getElementsByClassName('id_template_value_strong')[0].innerHTML;
                    if (names === addedValue) {
                        return false;
                    }
                }
                if (searchType === second.innerHTML.replace(/\s/g, "")) {
                    var $template = $('#search-value-item-template').clone();
                    var node = $template[0];
                    node.getElementsByClassName('id_template_value_strong')[0].innerHTML = names;
                    node.getElementsByClassName('id_template_value_input')[0].value = names;
                    node.getElementsByClassName('id_template_value_input')[0].name = searchKey;
                    //console.log(searchType);
                    childNode.appendChild(node);
                    return false;
                }
            } catch (e) {
                console.log(e);
            }
        }
        var template = $.clone($(tthis).closest("form").find("#search-item-template").get(0));
        template = template.getElementsByClassName('search-item-container')[0];
        template.style.display = "inline-block";
        $(template).find(".id_template_label").html($(tthis).closest("form").find(".search_property option:selected").text());
        $(template).find(".id_template_value").attr({
            value: names,
            name: searchKey
        });
        $(template).find(".id_template_value_strong").html(names);
        $(tthis).closest("form").find("#search-item-template").append(template);
        return false;
    };

    var submitSearch = function (tthis) {
        var all_data = $(tthis).serializeArray();
        //if (all_data.length <= 1) {
        //    //No search will be performed.
        //    return false;
        //}
        var data = {};
        for (var i = 0; i < all_data.length; i++) {
            if (data[all_data[i].name] != undefined) {
                data[all_data[i].name] = data[all_data[i].name] + ',' + all_data[i].value;
            } else {
                data[all_data[i].name] = all_data[i].value;
            }
        }
        window.location.href = $.param.querystring(window.location.href.replace($.param.querystring(), ''), data);
        return false;
    };

    $(document).on('click', '.btn-inline-append-search', function () {
        return addSearchProperty(this);
    });

    $('.search-form').keypress(function (e) {
        if (e.which == 13) {
            addSearchProperty(this);
            return submitSearch(this);
        }
    });

    $(".search-form").on('submit', function () {
        addSearchProperty(this);
        return submitSearch(this);
    });

    $(document).on('change', '.search_property', function () {
        var searchKey = $(this).find("option:selected").val();
        if (searchKey == undefined || searchKey == null || searchKey == "all") {
            $(".search-input").prop("disabled", true);
        } else {
            $(".search-input").prop("disabled", false);
        }
    });

    $(document).on('click', '.btn-inline-remove-search', function () {
        var ttthis = this;
        $(ttthis).closest(".search-item-container").fadeOut('fast', function () {
            $(ttthis).closest(".search-item-container").remove();
        });
        return false
    });

    $(document).on('click', '.btn-inline-remove-search-item', function () {
        var ttthis = this;
        $(ttthis).closest(".search-value-item").fadeOut('fast', function () {
            var parentItem = $(this).closest(".search-item-container");
            var childCount = parentItem.children('.search-value-item').length;
            console.log(childCount);
            $(ttthis).closest(".search-value-item").remove();
            if (childCount <= 1) {
                parentItem.fadeOut('fast', function () {
                    parentItem.remove();
                });
                parentItem.remove();
            }
        });
        return false
    });

    $(".search-input").prop("disabled", true);
});