// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeline', 'timelineEnd', 'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());
// Place any jQuery/helper plugins in here.

/*FBX CUSTOM SCRIPT START FROM HERE*/

jQuery(document).ready(function($){

    // *************** Left Sidebar  *********************

    $( ".parentmenuboxtrig" ).click(function() {
        //$( this ).toggleClass( "parentmenubox_open" );
        $(this).parent().toggleClass('parentmenubox_open','fast');
   });

    $( ".sidebar-label" ).click(function() {
        $( this ).parent().toggleClass( "sidebar-label-open" );
    });

    //by default hide the sidebar
    //$('#fbx-sidebar-area').addClass('sidebar-hide col-xs-12 col-sm-3 col-lg-2');
    //$('#fbx-maincontent').removeClass('col-sm-9 col-lg-10').addClass('col-xs-12');
    $('#fbx-sidebar-area').addClass('col-xs-12 col-sm-3 col-lg-2');
    //$('#fbx-maincontent').addClass('col-sm-9 col-lg-10').removeClass('col-xs-12')


    $( ".sidebar-toggle").click(function() {
        if($('#fbx-sidebar-area').hasClass('sidebar-hide')) {
            //door is now off and need to open
            $('#fbx-sidebar-area').removeClass('sidebar-hide').addClass('col-xs-12 col-sm-3 col-lg-2');
            $('#fbx-maincontent').addClass('col-xs-12 col-sm-9 col-lg-10');
        }else {
            //door is now off, please open
            $('#fbx-sidebar-area').addClass('sidebar-hide');
            $('#fbx-maincontent').removeClass('col-sm-9 col-lg-10').addClass('col-xs-12');
        }
   });

  /* //closest()
    $(".parentmenuboxtrig").click(function() {
        if($(this).hasClass('active'){
            $(this).parent().parent().addClass("toggle-active");
            //or $(this).parents().eq(2).addClass("toggle-active"); //for find() or closest()

        }
        else{
            $(this).parent().parent().removeClass("toggle-active");
        }
    });
*/
    // ***************  End Left Sidebar  *********************


    //adding datapicker
    $('.fbdatepicker').datetimepicker({
        format: 'DD/MM/YYYY'   // please change format as need http://eonasdan.github.io/bootstrap-datetimepicker/Options/#format
    });

    //adding datapicker
    $('.fbdatetimepicker').datetimepicker({
        /*format: 'DD.MM.YYYY'*/   // please change format as need http://eonasdan.github.io/bootstrap-datetimepicker/Options/#format
    });

    //adding chosen
    $('.chosen-select').chosen();
    $('.chosen-select-deselect').chosen({ allow_single_deselect: true });

    /*FOR CHECK BOX */
    $('.checkbox').checkbox();
    //$('input[type="checkbox"]').checkbox();



    //check toggler
    //on click of checkbox having class "checkalltoggle"  will get the class name from it's data-checktoggler  for the
    // checkbox it will toggle and  data-checktogglercontainer  will be the id of the container which contains the checkboxes that needs to
    $('.checkalltoggle').on('click', function(e){
        var $checktoggler            = $(this).data('checktoggler'); //class name that is used for the checkbox
        var $checktogglercontainer   = $(this).data('checktogglercontainer');  //id of the checkbox container
        var current_val = $(this).is(":checked"); //true or false
        var lastItem = this;
        $('.'+$checktogglercontainer).find('.'+$checktoggler).each(function( index, item ) {
            //if pure html checkbox is used without any style
            //$(item).prop('checked', current_val);

            //else
            if($(item).prop('type') == 'checkbox') {
                /*
                 $(item).checkbox({
                 checked: current_val
                 }, 'click');
                 */
                //console.log($(item).data('checkbox'));
                $(item).checkbox('setChecked', current_val);
                lastItem = item;
                //if(current_val == true){
                //    $("a.multi-action").removeAttr('disabled');
                //    $("a.multi-action").each(function(){
                //        if($(this).data('url') != undefined) {
                //            $(this).attr('href', $(this).data('url').replace("{0}",
                //                $.map($('table tr td input:checkbox:checked'), function (e, i) {
                //                return $(e).val();
                //            }).join(",")));
                //        }
                //    });
                //}else{
                //    $("a.multi-action").attr('disabled', 'disabled');
                //}
            }
            //end
        });
        $(lastItem).trigger("change");
    });

    //add new product
    $('.fbx-itemadd ').on('click', function(e){
        e.preventDefault();
        //add new product from single row template addproducttpl.html

        //addproducttpl.html should be the skeleton tpl , for complex example regular expression can be used
        $.get( "addproducttpl.html", function( data ) {
            //console.log(data);
           // console.log('adding new item');
            $('#fbx-product-area').append(data);
            //adding chosen
            $('.chosen-select').chosen();
            $('.chosen-select-deselect').chosen({ allow_single_deselect: true });
        });
    });

    //remove single product col
    $('#fbx-product-area').on('click','.fbx-itemremove', function(e){
        e.preventDefault();
        //console.log('removing item');
        $(this).parents('.fbx-productitem').remove();
    });


    //*****************add new product TWO ***********


    $('.fbx-itemadd ').on('click', function(e){
        e.preventDefault();
        //add new product from single row template addproducttpl.html

        //addproducttpl.html should be the skeleton tpl , for complex example regular expression can be used
        $.get( "addprice.html", function( data ) {
            //console.log(data);
            //console.log('adding new item');
            $('#fbx-price-area').append(data);
            //adding chosen
            $('.chosen-select').chosen();
            $('.chosen-select-deselect').chosen({ allow_single_deselect: true });
        });
    });

    //remove single product col
    $('#fbx-price-area').on('click','.fbx-itemremove', function(e){
        e.preventDefault();
        //console.log('removing item');
        $(this).parents('.fbx-priceitem').remove();
    });

});//jquery dom ready end

