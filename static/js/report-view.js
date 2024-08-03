/**
 * Created by Mahmud on 9/2/2014.
 */

$(function(){
    var DataDict = function(prefix, html){
        var _self = this;
        _self.prefix = prefix;
        _self.html = html;
        return _self;
    };

    var formsetDict = [];

    //build formset dictionary
    var buildFormsetDictionary = function(a){
        var prefix = $(a).data('prefix');
        var html = $('.' + prefix + '-formset-container:first').get(0).outerHTML;
        $(html).find('.select2').removeClass('select2-offscreen');
        $(html).find('.select2-container').remove();
        $(html).find('.select2').attr('tab-index', '1');
        formsetDict[formsetDict.length] = new DataDict(prefix, html);
    };

    var changeProperty = function(node, props, prefix, index){
        $.map(props, function(prop){
            var current = $(node).attr(prop);
            if (current != undefined) {
                var reg = new RegExp(prefix + '-(\\d)+');
                current = current.replace(reg, prefix + '-' + index);
                $(node).attr(prop, current);
                return node;
            }
        });
    };

    var updateInputFields = function(prefix){
        var all = $("." + prefix + "-formset-container");
        for( var i =0; i < all.length; i++){
            var $html = $(all[i]);
            $html.find('select[name^="' + prefix + '"], ' +
                'label[for^="' + prefix + '"], ' +
                'input[name^="' + prefix + '"], ' +
                'span[data-valmsg-for^="' + prefix + '"]').each(function(){
                changeProperty(this, ['name', 'for', 'id', 'data-valmsg-for'], prefix, i);
            });
        }
        $('input[name="' + prefix + '-TOTAL_FORMS"]').val(all.length);
        $(".date-selector").datepicker({format: 'dd-mm-yyyy'});
    };



    $(document)
        .off('click', '.btn-inline-remove')
        .on('click', '.btn-inline-remove', function(){
        var prefix = $(this).data('prefix');
        var tthis = $(this).closest('.' + prefix + '-formset-container');
        $(tthis).slideUp($(tthis).height() * 2, function(){
            if ($.trim($(tthis).find("." + prefix + "-id").val()) == ''){
                $(this).remove();
                updateInputFields(prefix);
            }else {
                $(tthis).find("input[type='checkbox'][name$='-DELETE']").attr('checked', 'checked');
            }
        });
        return false;
    });

    $(document)
        .off('click', '.btn-inline-addmore')
        .on('click', '.btn-inline-addmore', function(){
            var prefix = $(this).data('prefix');
            var html = '';
            for(var i =0; i < formsetDict.length; i++){
                if (prefix == formsetDict[i].prefix){
                    html = $(formsetDict[i].html).clone();
                    break;
                }
            }
            var $result = $(html).insertBefore($(this).closest("." + prefix + "-formset-addmore-container"));
            $result.hide().slideDown($result.height() * 2);
            //$result.find("select.select2").select2();
            updateSelect2Fields($result)
            updateInputFields(prefix);
            return false;
    });

    $("select.select2").select2('destroy');
    $(".btn-inline-addmore").each(function(){
        buildFormsetDictionary(this);
    });
    updateSelect2Fields();
    $(".date-selector").datepicker({format: 'dd-mm-yyyy'});
    $(".datetimepicker").datetimepicker({
        pick12HourFormat: true
    });
});