/**
 * Created by ruddra on 11/3/14.
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
    $("select.pageSizeSelect").select2()
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
                    }
                });
            }
            return false;
        }
        return true;
    });

    $(document).on('click', "a.manage-action", function(){
        if($(this).attr('disabled') == 'disabled') {
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

    $('.btn-inline-search').unbind();
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
                    }
                });
            }
            return false;
        }
        return true;
    });
});
