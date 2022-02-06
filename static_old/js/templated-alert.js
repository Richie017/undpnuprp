/**
 * Created by ActiveHigh on 5/6/14.
 */


TemplateAlert = {
    Confirm: function (title, message, ok_callback, cancel_callback, positive_button_label, negative_button_label){
        //var modal = $('<div tabindex="-1" class="modal hide fade" style="display: none;" aria-hidden="true">'+
        //'<div class="modal-header">'+
        //    '    <button data-dismiss="modal" class="close" type="button">×</button>'+
        //    '    <h4 class="blue bigger" align="center">' + title +
        //    '</h4>'+
        //    '</div>'+
        //    '   <div class="modal-body">'+
        //          message  +
        //    '   </div>'+
        //
        //    '    <div class="modal-footer">'+
        //    '       <button data-dismiss="modal" class="btn btn-small btn-cancel">'+
        //    '           <i class="icon-remove"></i>'+
        //    '       No' +
        //'       </button>'+
        //
        //'       <button data-dismiss="modal" class="btn btn-small btn-primary btn-ok">'+
        //'           <i class="icon-ok"></i>'+
        //'       Yes'+
        //'       </button>'+
        //'   </div>'+
        //'</div>');
        var positive_button = "Yes";
        if(typeof(positive_button_label) != "undefined" && positive_button_label != "") {
            positive_button = positive_button_label;
        }
        var negative_button = "No";
        if(typeof(negative_button_label) != "undefined" && negative_button_label != "") {
            negative_button = negative_button_label;
        }
        var modal = $(
            '<div tabindex="-1" class="modal fade fbx-modal" style="display: none;" aria-hidden="true">'+
            '<div class="modal-dialog modal-sm">' +
                '<div class="modal-content text-center fbx-modal-content">'+
                    '<h4>' + title + '</h4>'+
                    '<p>' + message + '</p>'+
                    '<div class="fbx-modalfooter">'+
                        '<ul class="list-inline fbx-footer-list">'+
                            '<li>'+
                                '<a data-dismiss="modal" class="btn-ok">'+
                                    '<i class="fbx-tick"></i>'+
                                    '<span>&nbsp;'+ positive_button +'</span>'+
                                '</a>'+
                            '</li>'+
                            '<li>'+
                                '<a data-dismiss="modal" class="btn-cancel">'+
                                    '<i class="fbx-cancel"></i>'+
                                    '<span>&nbsp;'+ negative_button +'</span>'+
                                '</a>'+
                            '</li>'+
                        '</ul>'+
                    '</div>'+
                '</div>'+
            '</div>');
        $(modal).find(".btn-ok").unbind('click').click(function(){
            if (typeof ok_callback == 'function')
                ok_callback();
        });
        $(modal).unbind('click').find(".btn-cancel").click(function(){
            if (typeof cancel_callback == 'function')
                cancel_callback();
        });
        $(modal).on('hidden', function(){
            $(modal).remove();
        });
        $(modal).modal('show');
    },
    Alert: function (title, message){
        $('<div tabindex="-1" class="modal hide fade" style="display: none;" aria-hidden="true">'+
            '<div class="modal-header">'+
            '    <button data-dismiss="modal" class="close" type="button">×</button>'+
            '    <h4 class="blue bigger" align="center">' + title +
            '</h4>'+
            '</div>'+
            '   <div class="modal-body">'+
            message  +
            '   </div>'+
            '    <div class="modal-footer">'+
            '       <button data-dismiss="modal" class="btn btn-small btn-primary btn-ok">'+
            '           <i class="icon-ok"></i>'+
            'Ok'+
            '       </button>'+
            '   </div>'+
            '</div>').modal('show');
    }
};