/**
 * Created by Mahmud on 9/2/2014.
 */

var DataDict = function (prefix, html) {
    var _self = this;
    _self.prefix = prefix;
    _self.html = html;
    return _self;
};
var formsetDict = [];

//build formset dictionary
var buildFormsetDictionary = function (a) {
    var prefix = $(a).data('prefix');
    //alert(prefix);
    var html = $('.' + prefix + '-formset-container:first').get(0).outerHTML;
    $(html).find('.select2').removeClass('select2-offscreen');
    $(html).find('.select2-container').remove();
    $(html).find('.select2').attr('tab-index', '1');

    formsetDict[formsetDict.length] = new DataDict(prefix, html);
};

var evaluationExpression = function (prefix, expression, fields) {
    var calc = expression;
    for (var i = 0; i < fields.length; i++) {
        var _c_1 = fields[i];
        var _c = fields[i].replace('[', '').replace(']', '');
        var elemId = prefix + _c;
        calc = calc.replace(_c_1, $("#id_" + elemId).val() == "" ? "0" : $("#id_" + elemId).val());
    }
    return eval(calc);
};

var updateCalculatedField = function () {
    $("[data-calculation]").each(function (e) {
        var tthis = this;
        var prefix = $(this).data('prefix');
        var re = /\[\w+\]/g;
        var calculation = $(this).data('calculation');
        var refs = calculation.match(re);
        for (var i = 0; i < refs.length; i++) {
            var _c = refs[i].replace('[', '').replace(']', '');
            var elemId = prefix + _c;
            $("#id_" + elemId).change(function () {
                $(tthis).val(evaluationExpression(prefix, calculation, refs))
            });
        }
    });
};

var highlightMandatoryFields = function (parent) {
    if (parent === undefined || parent === null) {
        $("span.mandatory-asterisk").remove();
        $('input,textarea,select').filter('[required]:visible').after("<span style=\" padding: 5px;\" class='text-danger mandatory-asterisk'>&#x2731</span>");
    } else {
        $(parent).find("span.mandatory-asterisk").remove();
        $(parent).find('input,textarea,select').filter('[required]:visible').after("<span style=\" padding: 5px;\" class='text-danger mandatory-asterisk'>&#x2731</span>");
    }
};

$(function () {

    var changeProperty = function (node, props, prefix, index) {
        $.map(props, function (prop) {
            var current = $(node).attr(prop);
            if (current != undefined) {
                var reg = new RegExp(prefix + '-(\\d)+');
                current = current.replace(reg, prefix + '-' + index);
                $(node).attr(prop, current);
                return node;
            }
        });
    };

    var updateInputFields = function (prefix) {
        var all = $("." + prefix + "-formset-container");
        for (var i = 0; i < all.length; i++) {
            var $html = $(all[i]);
            $html.find('select[name^="' + prefix + '"], ' +
                'label[for^="' + prefix + '"], ' +
                'input[name^="' + prefix + '"], ' +
                'textarea[name^="' + prefix + '"], ' +
                'span[data-valmsg-for^="' + prefix + '"]').each(function () {
                changeProperty(this, ['name', 'for', 'id', 'data-valmsg-for', 'data-prefix'], prefix, i);
            });
        }
        $('input[name="' + prefix + '-TOTAL_FORMS"]').val(all.length);
        $(".date-selector").datepicker({format: 'dd-mm-yyyy'});
        $(".icon-calendar").datepicker({format: 'dd-mm-yyyy'});
    };


    $(document)
        .off('click', '.btn-inline-remove')
        .on('click', '.btn-inline-remove', function () {
            var prefix = $(this).data('prefix');
            var tthis = $(this).closest('.' + prefix + '-formset-container');
            $(tthis).slideUp($(tthis).height() * 2, function () {
                if ($.trim($(tthis).find("." + prefix + "-id").val()) == '') {
                    $(this).remove();
                    updateInputFields(prefix);
                } else {
                    $(tthis).find("input[type='checkbox'][name$='-DELETE']").attr('checked', 'checked');
                }

                /*This section is for approval process roles*/
                /* startsection */
                if ($(".approval_process_level").length) {
                    initial_approval_level = 1;
                    $("#create_form").find(".approval_process_level").each(function (i) {
                        $(this).val(initial_approval_level);
                        initial_approval_level += 1;
                    });
                }

                /* endsection */

            });

            return false;
        });

    var initial_approval_level = 1;


// Handle tabs in create view
    var renderErrorToTabHeaders = function () {
        $(".form-tab-links").removeClass(".contains-error");
        var tabHeaders = $(".form-tab-links");
        var firstErrorTab = null;
        for (var i = 0; i < tabHeaders.length; i++) {
            var tabId = $(tabHeaders[i]).data("anchor");
            var tabContent = $("#" + tabId);
            var errors = $(tabContent).find(".input-validation-error");
            if (errors.length > 0) {
                $(tabHeaders[i]).addClass("contains-error");
                if (firstErrorTab == null) {
                    firstErrorTab = tabId;
                }
            }
        }
        if (firstErrorTab != null) {
            navigateToFormTab(firstErrorTab);
        }
    };

    var navigateToFormTab = function (tabId) {
        $(".form-tab-content").css("display", "none");
        $(".form-tab-links").removeClass("active");
        var selected_tab_name = tabId;
        $("#" + selected_tab_name).css("display", "block");
        $("#" + selected_tab_name).find(".fbx-content-shop").css({'padding-top': 0});
        var tabHeaders = $(".form-tab-links");
        var tabIndex = -1;
        for (var i = 0; i < tabHeaders.length; i++) {
            console.log(tabHeaders[i]);
            if ($(tabHeaders[i]).data("anchor") == tabId) {
                tabIndex = i;
                $(tabHeaders[i]).addClass("active");
            }
        }
        if ((tabIndex + 1) == tabHeaders.length) {
            $('.tabbed-form-next').css("display", "none");
            $('.tabbed-form-previous').css({"display": "inline-block", "float": "none"});
            $('.fbx-actionbtn button.fbx-previous i').css({"background-size": "100%"});
            $('.fbx-save').css('display', 'inline-block');
            $('.fbx-cancel').css('display', 'inline-block');
        }
        else {
            $('.fbx-save').css('display', 'none');
            $('.fbx-cancel').css('display', 'none');
            $('.tabbed-form-next').css('display', 'block');
            $('.fbx-actionbtn button.fbx-previous i').css({"background-size": "80%"});
            if (tabIndex === 0) {
                $('.tabbed-form-previous').css("display", "none");
            }
            else {
                $('.tabbed-form-previous').css({"display": "inline-block", "float": "right"});
            }
        }

        $('html,body').animate({
            scrollTop: $("#create_form").offset().top
        }, 'slow');
        // highlightMandatoryFields();
    };

    var navigateToNextTab = function () {
        var tabHeaders = $(".form-tab-links");
        var currentTabHeader = $(".active.form-tab-links");
        var currentTabName = $(currentTabHeader).data("anchor");
        var tabIndex = -1;
        for (var i = 0; i < tabHeaders.length; i++) {
            if ($(tabHeaders[i]).data("anchor") == currentTabName) {
                tabIndex = i;
            }
        }
        tabIndex++;
        if (tabHeaders.length > (tabIndex)) {
            navigateToFormTab($(tabHeaders[tabIndex]).data("anchor"));
        }
    };

    var navigateToPreviousTab = function () {
        var tabHeaders = $(".form-tab-links");
        var currentTabHeader = $(".active.form-tab-links");
        var currentTabName = $(currentTabHeader).data("anchor");
        var tabIndex = -1;
        for (var i = 0; i < tabHeaders.length; i++) {
            if ($(tabHeaders[i]).data("anchor") == currentTabName) {
                tabIndex = i;
            }
        }
        tabIndex -= 1;
        if (tabIndex > -1) {
            navigateToFormTab($(tabHeaders[tabIndex]).data("anchor"));
        }
    };

    $(document)
        .off("click", ".tabbed-form-next")
        .on("click", ".tabbed-form-next", function () {
            navigateToNextTab();
        });

    $(document)
        .off("click", ".tabbed-form-previous")
        .on("click", ".tabbed-form-previous", function () {
            navigateToPreviousTab();
        });

    $(document)
        .off("click", ".form-tab-links")
        .on("click", ".form-tab-links", function () {
            var selected_tab_name = $(this).data("anchor");
            navigateToFormTab(selected_tab_name);
        });

    if ($(".form-tab-links").length > 0) {
        $(".form-tab-links").first().trigger("click");
        renderErrorToTabHeaders();
    }

    $(document)
        .off('click', '.btn-inline-addmore')
        .on('click', '.btn-inline-addmore', function () {
            var prefix = $(this).data('prefix');
            var html = '';
            for (var i = 0; i < formsetDict.length; i++) {
                if (prefix == formsetDict[i].prefix) {
                    html = $(formsetDict[i].html).clone();
                    var visible_inputs = $(html).find('input[type != hidden], select');
                    for (var j = 0; j < visible_inputs.length; j++) {
                        $(visible_inputs[j]).val('');
                    }
                    visible_inputs = $(html).find('textarea');
                    for (var j = 0; j < visible_inputs.length; j++) {
                        $(visible_inputs[j]).html('');
                    }
                    break;
                }
            }
            var $result = $(html).insertBefore($(this).closest("." + prefix + "-formset-addmore-container"));
            $result.hide().slideDown($result.height());

            $result.find("i").each(function (i) {
                var date_icon = !!$(this).data('date-icon');
                if (date_icon) {
                    if ($(this).data("date-icon") == "icon-calendar") {
                        $(this).removeAttr("id").addClass("icon-calendar");
                        $(".datetimepicker").datetimepicker({
                            format: 'dd/MM/yyyy'
                        });
                    }
                }
            });

            /*This section is for approval process roles*/
            /* startsection */
            if ($(html).find(".approval_process_level").length) {
                initial_approval_level = 1;
                $("#create_form").find(".approval_process_level").each(function (i) {
                    $(this).val(initial_approval_level);
                    initial_approval_level += 1;
                });
            }

            /* endsection */

            updateInputFields(prefix);
            loadBWSelect2Fields($result);
            ;
            loadSelect2Legacy($result);
            ;

            $result.find(".control-label").each(function (i) {
                var __this = $(this);
                if (__this.parent().find(".order-breakdown").length || __this.parent().find(".require-unitprice").length) {
                    __this.css("visibility", "hidden");
                }
            });
            $result.find(".btn-inline-remove").show();

            if ($result.find(".select2").length) {
                $result.find(".select2")
            }

            // all_select2s = $result.find("select.select2, input[data-url].select2-input");
            // if (all_select2s != null)
            // {
            // all_select2s.each(function ()
            // {
            // var this_select2 = this;
            // var depends_on = $(this_select2).data('depends-on');
            // var cached_items = select2_cached_data[depends_on];
            // select2APIDataLoad(this_select2, { items: cached_items }, false);

            // $(this_select2).on("change", function (e) {
            //
            //     var child = $(this_select2).parent().parent().parent().parent().find("input.product-expiry-date");
            //     select2ChangeMethod(child);
            // });

            // });
            // }


            if ($(html).find("select[id$=product]").length > 0) {
                if ($(html).find("select[id$=product]").hasClass("require-unitprice")) {
                    UpdateUnitPriceOnProductSelect($(html).find("select[id$=product]"));
                }
            }

            if ($(html).find("select[id$=product]").length > 0) {
                if ($(html).find("select[id$=product]").hasClass("transaction-select2")) {
                    $(html).find("select[id$=product]").select2();
                }
            }

            //This part is to show the remove icon in the right side. Each time the product is added trash icon is visible to that
            //particular product so that he can drop it. The first default product is not deletable.

            $(".btn-inline-remove:first").hide();

            $(".btn-inline-remove:not(:first)").css({
                "float": "right",
                "display": "block",
                "margin-right": "67px"
            });
            return false;
        });


    function UpdateTotalItems(this_obj) {
//        var number_of_packet = parseInt(this_obj.parent().parent().parent().find("input[id$=number_of_packet]").val());
//        var items_per_packet = parseInt(this_obj.parent().parent().parent().find("input[id$=items_per_packet]").val());
//        var loose_items = parseInt(this_obj.parent().parent().parent().find("input[id$=loose_items]").val());
//        if(number_of_packet < 0 || items_per_packet < 0 || loose_items < 0){
//            return;
//            //this_obj.parent().parent().parent().find("input[id$=number_of_packet]").val(0);
//        }
        var total_items = parseInt(this_obj.parent().parent().parent().parent().find("input[id$=quantity]").val()); //number_of_packet * items_per_packet + loose_items;
        //this_obj.parent().parent().parent().find("input[id$=total_items]").val(total_items);
        var unit_price = parseFloat(this_obj.parent().parent().parent().parent().find("input[id$=unit_price]").val());
        if (unit_price < 0) {
            return;
        }
        var subtotal = total_items * unit_price;
        //this_obj.parent().parent().parent().parent().find("input[id$=sub_total]").val(subtotal.toFixed(1));
//        var discount = parseFloat(this_obj.parent().parent().parent().find("input[id$=discount]").val());
//        if(parseFloat(discount) < 0 || parseFloat(discount) > 100){
//            return;
//        }
//        var total = subtotal - ((discount/100) * subtotal);
        this_obj.parent().parent().parent().parent().find("input[id$=-total]").val(subtotal.toFixed(1));
    }

    function CheckPositiveInteger(this_obj) {
        var number_of_packet = parseInt(this_obj.parent().parent().parent().find("input[id$=number_of_packet]").val());
        var items_per_packet = parseInt(this_obj.parent().parent().parent().find("input[id$=items_per_packet]").val());
        var loose_items = parseInt(this_obj.parent().parent().parent().find("input[id$=loose_items]").val());
        if (number_of_packet < 0) {
            this_obj.parent().parent().parent().find("input[id$=number_of_packet]").val(0);
        }
    }

    //$("input[id$=total_items]").prop("readonly","true");
    $("input[id$=sub_total]").prop("readonly", "true");
    $("input[id$=-total]").prop("readonly", "true");
    //$("input[id$=unit_price]").prop("readonly","true");

    $(document).on("change", "input[id$=number_of_packet]", function (e) {
        UpdateTotalItems($(this));
        //CheckPositiveInteger($(this));
    });

    $(document).on("change", "input[id$=items_per_packet]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("change", "input[id$=loose_items]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("keyup", "input[id$=unit_price]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("change", "input[id$=unit_price]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("change", "input[id$=discount]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("change", "input[id$=quantity]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("change", "input[id$=total_items]", function (e) {
        UpdateTotalItems($(this));
    });

    $(document).on("submit", "#create_form", function (e) {
        if (!$('#create_form').valid()) {
            return false;
        }
        else {
            $(this).submit(function () {
                return false;
            });
        }
        return true;

    });

    // Price config form

    // Net customer price

    function updateNetCustomerPrice(this_obj) {
        var ref_price = parseFloat(this_obj.val());
        var ref_net_cust_markup = $("input[id$=id_ref_net_cust_markup]").val();
        var net_customer_price = parseFloat(this_obj.val());

        if (this_obj.val() != '') {
            if (ref_net_cust_markup != '' && ref_net_cust_markup != 'undefined') {
                var value = ref_net_cust_markup.split('%');
                var ref_net_cust_markup_value = parseFloat(value.shift());
                if (ref_net_cust_markup_value > 0) {
                    net_customer_price = (ref_price + (ref_price * ref_net_cust_markup_value) / 100).toFixed(2);
                } else {
                    net_customer_price = (ref_price + (ref_price * ref_net_cust_markup_value) / 100).toFixed(2);
                }
            } else {
                net_customer_price = net_customer_price;
            }
        } else {
            net_customer_price = '';
        }
        $("input[id$=id_net_cust_price]").val(net_customer_price);
    }

    function updateNetCustomerPriceFromMarkup(this_obj) {
        var ref_price_raw = $("input[id$=id_ref_price]").val();
        var ref_net_cust_markup = this_obj.val();
        if (ref_price_raw != '') {
            ref_price = parseFloat(ref_price_raw)
            if (ref_net_cust_markup != '' && ref_net_cust_markup != 'undefined') {
                var value = ref_net_cust_markup.split('%');
                var ref_net_cust_markup_value = parseFloat(value.shift());
                net_customer_price = (ref_price + (ref_price * ref_net_cust_markup_value) / 100).toFixed(2);
            } else {
                net_customer_price = ref_price;
            }
        } else {
            net_customer_price = '';
        }
        $("input[id$=id_net_cust_price]").val(net_customer_price);
    }

    // Update net customer markup from  Net customer price field

    function updateNetCustomerMarkup(this_obj) {
        var ref_price = $("input[id$=id_ref_price]").val();
        var ref_net_cust_markup = $("input[id$=id_ref_net_cust_markup]").val();
        var net_customer_price = parseFloat(this_obj.val());
        var ref_net_cust_markup_value = ''
        if (this_obj.val() != '') {
            if ((ref_price != '' && ref_price != 'undefined')) {
                var ref_price_value = parseFloat(ref_price);
                var subtracted_value = net_customer_price - ref_price_value
                var ref_net_cust_markup = (subtracted_value * 100) / net_customer_price
                ref_net_cust_markup_value = ref_net_cust_markup.toFixed(2) + '%'
            }
        }

        $("input[id$=id_ref_net_cust_markup]").val(ref_net_cust_markup_value);

    }

    $(document).on("keyup change", "input[id$=id_ref_price]", function (e) {
        updateNetCustomerPrice($(this))
    });

    $(document).on("keyup change", "input[id$=id_ref_net_cust_markup]", function (e) {
        updateNetCustomerPriceFromMarkup($(this))
    });

    $(document).on("keyup change", "input[id$=id_net_cust_price]", function (e) {
        updateNetCustomerMarkup($(this))
    });

    // Gross Customer Price

    function updateGrossCustomerPriceFromVAT(this_obj) {
        var net_customer_price_raw = $("input[id$=id_net_cust_price]").val()
        var gross_cust_price = ''
        if (this_obj.val() != '' && net_customer_price_raw != '') {
            var net_customer_price = parseFloat(net_customer_price_raw)
            var value = this_obj.val().split('%');
            var vat_amount = parseFloat(value.shift());
            if (isNaN(vat_amount)) {
                gross_cust_price = net_customer_price_raw
            } else {
                gross_cust_price = (net_customer_price + (vat_amount * net_customer_price) / 100).toFixed(2);
            }
        } else {
            gross_cust_price = net_customer_price_raw
        }
        $("input[id$=id_gross_cust_price]").val(gross_cust_price);
    }

    // Update Distributor price from gross customer distributor markup field

    function updateDistPriceFromCDistMarkup(this_obj) {
        var gross_customer_price_raw = $("input[id$=id_gross_cust_price]").val();
        var distributor_price = '';
        if (this_obj.val() != '' && gross_customer_price_raw != '') {
            var gross_customer_price = parseFloat(gross_customer_price_raw);
            var value = this_obj.val().split('%');
            var markup_amount = parseFloat(value.shift());
            if (isNaN(markup_amount)) {
                distributor_price = gross_customer_price_raw;
            } else {
                distributor_price = (gross_customer_price + (markup_amount * gross_customer_price) / 100).toFixed(2);
            }
        } else {
            distributor_price = gross_customer_price_raw;
        }
        $("input[id$=id_dist_price]").val(distributor_price);
    }

    // Update Gross customer markup from Distributor price

    function updateGrossCustomerMarkup(this_obj) {
        var gross_customer_price_raw = $("input[id$=id_gross_cust_price]").val();
        var gross_cust_markup = $("input[id$=id_gross_cust_distributor_markup]").val();
        var distributor_price = parseFloat(this_obj.val());
        var gross_cust_markup_value = ''
        if (this_obj.val() != '') {
            if ((gross_customer_price_raw != '' && gross_customer_price_raw != 'undefined')) {
                var gross_customer_price = parseFloat(gross_customer_price_raw);
                var subtracted_value = distributor_price - gross_customer_price
                var gross_cust_markup = (subtracted_value * 100) / distributor_price
                gross_cust_markup_value = gross_cust_markup.toFixed(2) + '%'
            }
        }
        $("input[id$=id_gross_cust_distributor_markup]").val(gross_cust_markup_value);

    }

    $(document).on("keyup change", "input[id$=id_vat_rate]", function (e) {
        updateGrossCustomerPriceFromVAT($(this))
    });

    // On change Gross customer distributor markup field update distributor price

    $(document).on("keyup change", "input[id$=id_gross_cust_distributor_markup]", function (e) {
        updateDistPriceFromCDistMarkup($(this))
    });

    // On change Distributor price field update Gross customer distributor markup

    $(document).on("keyup change", "input[id$=id_dist_price]", function (e) {
        updateGrossCustomerMarkup($(this))
    });


    // Retailer Price

    // Update Retailer price from Distributor Retailer markup field

    function updateRetPriceFromDistRetMarkup(this_obj) {
        var distributor_price_raw = $("input[id$=id_dist_price]").val();
        var retailer_price = '';
        if (this_obj.val() != '' && distributor_price_raw != '') {
            var distributor_price = parseFloat(distributor_price_raw);
            var value = this_obj.val().split('%');
            var markup_amount = parseFloat(value.shift());
            if (isNaN(markup_amount)) {
                retailer_price = distributor_price_raw;
            } else {
                retailer_price = (distributor_price + (markup_amount * distributor_price) / 100).toFixed(2);
            }
        } else {
            retailer_price = distributor_price_raw;
        }
        $("input[id$=id_retail_price]").val(retailer_price);
    }

    // Update distributor retailer markup on change retailer price field

    function updateRetailerMarkup(this_obj) {
        var dist_price_raw = $("input[id$=id_dist_price]").val();
        var retailer_price = parseFloat(this_obj.val());
        var dist_retailer_markup_value = ''
        if (this_obj.val() != '') {
            if ((dist_price_raw != '' && dist_price_raw != 'undefined')) {
                var dist_price = parseFloat(dist_price_raw);
                //console.log(dist_price);
                //console.log(retailer_price);
                var subtracted_value = retailer_price - dist_price
                var dist_retailer_markup = (subtracted_value * 100) / retailer_price
                dist_retailer_markup_value = dist_retailer_markup.toFixed(2) + '%'
            }
        }
        $("input[id$=id_dist_retailer_markup]").val(dist_retailer_markup_value);

    }

    // On change retailer markup field update Retailer price

    $(document).on("keyup change", "input[id$=id_dist_retailer_markup]", function (e) {
        updateRetPriceFromDistRetMarkup($(this))
    });

    // On change Retailer price field update distributor retailer markup

    $(document).on("keyup change", "input[id$=id_retail_price]", function (e) {
        updateRetailerMarkup($(this))
    });


    function ajax_call(data_url, complete_callback) {
        $.ajax(data_url,
            {
                dataType: "json"
            }).done(complete_callback);
    }

    if ($("input[id$=invoice]").length > 0) {
        if ($("input[id$=invoice]").hasClass("require-invoice")) {
            UpdateInvoiceAmountOnInvoiceSelect($("input[id$=invoice]"));
        }
    }

    function UpdateInvoiceAmountOnInvoiceSelect(element) {
        element.on("change", function (e) {
            var _this_object = $(this);

            if (_this_object.val() != '') {
                $("input[id$=total_amount]").prop("readonly", true);
                $("input[id$=due_amount]").prop("readonly", true);

                _this_object.prop("disabled", true);

                var id = $(this).val();
                var data_url = "/open-invoices/?format=json&id=" + id + "&search=1";

                ajax_call(data_url, function (data) {
                    var price_total = data.items[0].price_total;
                    var paid_total = data.items[0].actual_amount_paid;
                    var due_total = price_total - paid_total;

                    _this_object.parent().parent().parent().find("input[id$=total_amount]").val(price_total.toFixed(1));
                    _this_object.parent().parent().parent().find("input[id$=due_amount]").val(due_total.toFixed(1));

                    _this_object.prop("disabled", false);

                });
            }

            if (_this_object.val() == '') {
                $("input[id$=total_amount]").prop("readonly", false);
                $("input[id$=due_amount]").prop("readonly", false);
                _this_object.prop("disabled", false);

                _this_object.parent().parent().parent().find("input[id$=total_amount]").val(0.0);
                _this_object.parent().parent().parent().find("input[id$=due_amount]").val(0.0);
            }
        });
    };


    updateCalculatedField();
    //updateRefFields();
    //loadBWSelect2Fields();

    $("select.select2").select2('destroy');
    $(".btn-inline-addmore").each(function () {
        buildFormsetDictionary(this);
    });
    //console.log("Update select2 fields called.");
    $(".date-selector").datepicker({format: 'dd-mm-yyyy'});
    $(".datetimepicker").datetimepicker({
        pick12HourFormat: true
    });

    $(document).ready(function () {
    });


    // On change Custom Field field_type hide/show choice fields

    $('select.select2').select2()
        .on("change", function (e) {
            var tthis = this;
            if ($(tthis).hasClass("toggle_choices")) {
                if ($(tthis).val() == 'choice_list') {
                    $("#id_list_values").removeClass("hidden");
                    $("#id_list_values").parent().parent().removeClass("hidden");
                }
                else {
                    $("#id_list_values").addClass("hidden");
                    $("#id_list_values").parent().parent().addClass("hidden");
                }
            }
        });


});



// $(document).ready(function () {
//     highlightMandatoryFields(); // highlight mandatory fields of given form
// });