/**
 * Created by ruddra on 5/26/14.
 */

$(function(){
    $(".date-selector").datepicker({dateFormat: 'dd/mm/yy', maxDate: (new Date).getDate()+ "/" + (new Date).getMonth() + "/" + (new Date).getFullYear() });
});

$(document).ready(function() {
    $('.form-org-settings').submit(function() { // catch the form's submit event
        $.ajax({ // create an AJAX call...
            data: $(this).serialize(), // get the form data
            type: 'post', // GET or POST
            url: $(this).attr('action'), // the file to call
            dataType: 'json',
            success: function(response) { // on success..
//                $('.organization-details).html(response); // update the DIV
                if (response.success == true) {
                    location.reload();
                }
                else {
                    $(".flash_message").html( response.message).addClass("alert-error");
                    $(".flash_message").slideDown();
                    setTimeout(function(){
                        $(".flash_message").slideUp();
                    }, 10000);
                }
            }
        });
        return false;
    });

    $(".settings-switch").change(function(){
        $($(this).data('target')).val($(this).is(":checked")? 'True' : 'False');
    });
});

