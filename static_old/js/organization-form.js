///**
//* Created by ruddra on 2/24/14.
//// */
//
//
//$(function () {
//    $('.btn-add-more').click(function () {
//        var type = $(this).data('type');
//        var parent = $("." + type+ "-form:first").parent('div');
//        var addDiv = $("." + type+ "-form:first").clone();
//        parent.append(addDiv);
//        var index = 0;
//        parent.children("." + type+ "-form").each(function(){
//            var elements = ['label', '*', 'span'];
//            var props = [['for'], ['id','name'], ['data-valmsg-for']];
//            var prefix = [[''], ['id_', ''], ['']];
//            for(var i = 0; i < props.length; i++){
//                for(var j = 0; j < elements.length; j++){
//                    $(this).find("*["+props[j][i]+"^='"+prefix[j][i] + type + "']").each(function(){
//                        var prop = $(this).attr(props[j][i]);
//                        var regex = /(id_)*\w{1,}-\d{1,}-\w{1,}/gi;
//                        var match = prop.match(regex);
//                        if(match.length > 0){
//                            var m = match[0];
//                            var d = /-\d{1,}-/gi;
//                            m = m.replace(d,"-"+index+"-");
//                            $(this).attr(props[j][i], m);
//                        }
//                    });
//                }
//            }
//            index++;
//        });
//        $("#id_" + type +  "-TOTAL_FORMS").val(parent.children("." + type+ "-form").length);
//    })
//})