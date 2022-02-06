/**
 * Created by mahmudul on 2/20/14.
 */

$(function(){

    $(document).on('click', 'table th input:checkbox', function(){
        var that = this;
        $(this).closest('table').find('tr > td:first-child input:checkbox')
            .each(function(){
                this.checked = that.checked;
                $(this).closest('tr').toggleClass('selected');
            })
            .first().change();
    });

    $(document).on('change', 'table tr td input:checkbox', function(){
        var cbox = this;
        var total = $('table tr td input:checkbox:checked');
        if(total.length == 1){
            $("a.single-action").removeAttr('disabled');
            $("a.single-action").each(function(){
                $(this).attr('href', $(this).data('url').replace("{0}", $(cbox).val()));
            });
        }else{
            $("a.single-action").attr('disabled', 'disabled');
        }
        if(total.length > 0){
            $("a.multi-action").removeAttr('disabled');
            $("a.multi-action").each(function(){
                if($(this).data('url') != undefined) {
                    $(this).attr('href', $(this).data('url').replace("{0}", $.map($('table tr td input:checkbox:checked'), function (e, i) {
                        return $(e).val();
                    }).join(",")));
                }
            });
        }else{
            $("a.multi-action").attr('disabled', 'disabled');
        }
    });

    $("a.all-action").removeAttr('disabled');
    $("a.multi-action").attr('disabled', 'disabled');
    $("select.pageSizeSelect").select2();
    $(document).on('change', ".pageSizeSelect", function(){
        var _size = $(this).val();
        var link = window.location.href.replace(/\?page=\d{1,}&/gi,'?');
        if ($(this).data('ajax') == '1') {
            link = $(this).closest('.ajax-container').data('url').replace(/\?page=\d{1,}&/gi,'?');
        }
        link = link.replace(/\?page=\d{1,}/gi,'');
        link = link.replace(/&page=\d{1,}&/gi,'&');
        link = link.replace(/&page=\d{1,}/gi,'');
        var new_link = '';
        if(link.indexOf('paginate_by') > -1){
            new_link = link.replace(/paginate_by=(\d{1,})/gi, 'paginate_by=' + _size)
        }else if(link.indexOf('?') > -1){
            new_link = link + '&paginate_by=' + _size;
        }else {
            new_link = link + '?paginate_by=' + _size;
        }

        if ($(this).data('ajax') == '1'){
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null){
                $.ajax({
                    url : new_link,
                    type: 'get',
                    success:function(html){
                        $(container).html(html);
                        updateSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        window.location.href = new_link;
    });

    $(document).on('click', ".page-navigation", function(){
        var _page = $(this).html();
        var link = window.location.href.replace(/\?page=\d{1,}&/gi,'?');
        if ($(this).data('ajax') == '1') {
            link = $(this).closest('.ajax-container').data('url').replace(/\?page=\d{1,}&/gi,'?');
        }
//        link = link.replace(/\?page=\d{1,}/gi,'');
//        link = link.replace(/&page=\d{1,}&/gi,'&');
//        link = link.replace(/&page=\d{1,}/gi,'');
//        $(".loader").fadeIn('fast');
        var new_link = '';
        if(link.indexOf('paginate_by') > -1){
            new_link = link.replace(/page=(\d{1,})/gi, 'page=' + _page)
        }else if(link.indexOf('?') > -1){
            new_link = link + '&page=' + _page;
        }else {
            new_link = link + '?page=' + _page;
        }

        if ($(this).data('ajax') == '1'){
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null){
                $.ajax({
                    url : new_link,
                    type: 'get',
                    success:function(html){
                        $(container).html(html);
                        updateSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        return true;
    });

    $(document).on('click', "a.manage-action", function(){
        if($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
            return false;
        }
        if($(this).hasClass('all-action') && $(this).hasClass('confirm-action')) {
            var tthis = $(this).attr('href');
            TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
                function(){
                    window.location.href = tthis;
                },
                function(){

                });
            return false;
        }
        if($(this).hasClass('popup')){
            var tthis_url = $(this).attr('href');
            window.open(tthis_url,"","");
            window.focus();
            return false;
        }


        if($(this).hasClass('multi-action') && !$(this).hasClass('ignore-multi')) {
            var tthis = $(this).attr('href');
            TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
                function(){
                    window.location.href = tthis;
                },
                function(){

                });
            return false;
        }
        return true;
    });

    $(document).on('click', '.run-importer', function(){
        var tthis = $(this);
        TemplateAlert.Confirm("Confirmation", "Clicking 'Yes' will start the importer. The page will auto refresh periodically. Please be patient while the importer runs.",
            function(){
                window.location.href = $(tthis).prop('href');
            },
            function(){

            });
        return false;
    });

    $(document).on('click', '.btn-inline-search', function(){
        if ($(this).data('ajax') == '1'){
            var container = $(this).closest('.ajax-container');
            if (container != undefined || container != null){
                $.ajax({
                    url : $(container).data('url'),
                    data: $(this).closest('form').serialize(),
                    type: 'get',
                    success:function(html){
                        $(container).html(html);
                        updateSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        return true;
    });

    function append_search_query() {
        if ($(".search_property option:selected").data('is-range') == 'True') {
            var q1 = $(this).closest("form").find("#query_1").val();
            var q2 = $(this).closest("form").find("#query_2").val();
            if(q1 == null || q1 == "") {
                $(this).closest("form").find("#query_1").focus();
                return false;
            }
            if(q2 == null || q2 == "") {
                $(this).closest("form").find("#query_2").focus();
                return false;
            }
            var values = q1 + "," + q2;
        } else {
            var values = $(this).closest("form").find("#query_1").val();
            if(values == null || values == "") {
                $(this).closest("form").find("#query_1").focus();
                return false;
            }
        }
        if (values == null || values == ""){
            values = "None";
        }
        $(this).closest("form").find(".search-input").val('');

        var template = $.clone($(this).closest("form").find("#search-item-template").get(0));
        $(template).find(".id_template_label").html($(this).closest("form").find(".search_property option:selected").text());
        $(template).find(".id_template_value").attr({
            value: values,
            name: $(this).closest("form").find(".search_property option:selected").val()
        });
        $(template).find(".id_template_value_strong").html(values);
        $(this).closest("form").find(".div_filters").append($(template).html());
        return true;
    }

    $(document).on('click', '.btn-inline-append-search', function(){
        if ($(".search_property option:selected").data('is-range') == 'True') {
            var q1 = $(this).closest("form").find("#query_1").val();
            var q2 = $(this).closest("form").find("#query_2").val();
            if(q1 == null || q1 == "") {
                $(this).closest("form").find("#query_1").focus();
                return false;
            }
            if(q2 == null || q2 == "") {
                $(this).closest("form").find("#query_2").focus();
                return false;
            }
            var values = q1 + "," + q2;
        } else {
            var values = $(this).closest("form").find("#query_1").val();
            if(values == null || values == "") {
                $(this).closest("form").find("#query_1").focus();
                return false;
            }
        }
        if (values == null || values == ""){
            values = "None";
        }
        $(this).closest("form").find(".search-input").val('');

        var template = $.clone($(this).closest("form").find("#search-item-template").get(0));
        $(template).find(".id_template_label").html($(this).closest("form").find(".search_property option:selected").text());
        $(template).find(".id_template_value").attr({
            value: values,
            name: $(this).closest("form").find(".search_property option:selected").val()
        });
        $(template).find(".id_template_value_strong").html(values);
        $(this).closest("form").find(".div_filters").append($(template).html());
        return false;
    });

    $(document).on('click', '.btn-inline-remove-search', function(){
        var ttthis = this;
        $(ttthis).closest(".search-item-container").fadeOut('fast', function(){
            $(ttthis).closest(".search-item-container").remove();
        });
        return false
    });


    $(document).on('change', '.inline-edit-input', function() {
        $(this).closest('form').find("div.alert").slideDown();
    });


    $(document).on('click', '.btn-save-inline-form', function(){
        if ($(this).data('ajax') == '1'){
            var container = $(this).closest('.ajax-container');
            console.log($(container).data('url'));
            console.log($(this).closest('form').serialize());
            if (container != undefined || container != null){
                $.ajax({
                    url : $(container).data('url'),
                    data: $(this).closest('form').serialize(),
                    type: 'post',
                    success:function(html){
                        console.log(html);
                        //console.log(container);
                        $(container).html(html);
                        //$(container).html("asdasdasdasdasdasd");
                        updateSelect2Fields();
                        updateSearchFields(true);
                    }
                });
            }
            return false;
        }
        return true;
    });

    $('.search-form').keypress(function (e) {
      if (e.which == 13) {

        var append_qstring = true;
        if ($(".search_property option:selected").data('is-range') == 'True') {
            var q1 = $(this).closest("form").find("#query_1").val();
            var q2 = $(this).closest("form").find("#query_2").val();
            if(q1 == null || q1 == "") {
                $(this).closest("form").find("#query_1").focus();
                append_qstring = false;
            }
            if(q2 == null || q2 == "") {
                $(this).closest("form").find("#query_2").focus();
                append_qstring = false;
            }
            var values = q1 + "," + q2;
        } else {
            var values = $(this).closest("form").find("#query_1").val();
            if(values == null || values == "") {
                $(this).closest("form").find("#query_1").focus();
                append_qstring = false;
            }
        }
        if(append_qstring) {
            $(this).closest("form").find(".search-input").val('');

            var template = $.clone($(this).closest("form").find("#search-item-template").get(0));
            $(template).find(".id_template_label").html($(this).closest("form").find(".search_property option:selected").text());
            $(template).find(".id_template_value").attr({
                value: values,
                name: $(this).closest("form").find(".search_property option:selected").val()
            });
            $(template).find(".id_template_value_strong").html(values);
            $(this).closest("form").find(".div_filters").append($(template).html());
        }

        var all_data = $(this).serializeArray();
        if(all_data.length <= 1) {
            //No search will be performed.
            return false;
        }
        var data = {};
        for(var i = 0; i < all_data.length; i++){
            if(data[all_data[i].name] != undefined){
                data[all_data[i].name] = data[all_data[i].name] + ',' + all_data[i].value;
            }else {
                data[all_data[i].name] = all_data[i].value;
            }
        }
        window.location.href = $.param.querystring(window.location.href.replace($.param.querystring(), ''), data);
        e.preventDefault();
        return false;
      }
    });

    $(".search-form").on('submit', function(){
        var all_data = $(this).serializeArray();
        var data = {};
        for(var i = 0; i < all_data.length; i++){
            if(data[all_data[i].name] != undefined){
                data[all_data[i].name] = data[all_data[i].name] + ',' + all_data[i].value;
            }else {
                data[all_data[i].name] = all_data[i].value;
            }
        }
        window.location.href = $.param.querystring(window.location.href.replace($.param.querystring(), ''), data);
        return false;
    });
});
