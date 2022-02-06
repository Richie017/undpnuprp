/**
 * Created by mahmudul on 2/18/14.
 */

$(document).ready(function(){

    $("form").validate({
        submitHandler: function(form) {
            form.submit();
        }
    });

    $("form").find(".input-validation-error").each(function(){
        $(this).change(function(){
            $(this).parent().find(".input-validation-error").removeClass("input-validation-error");
            $(this).parent().find(".errorlist").remove();
        })
    });
});