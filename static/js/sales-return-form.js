$(document).ready(function(){

    $('#sales-return-outlet').change(function(){
        var e = document.getElementById("sales-return-outlet");
        var outletcode = e.options[e.selectedIndex].value;
        $(".sales-return-sales option").each(function() {
            $(this).remove();
        });
        $('.sales-return-sales').append('<option>--</option>');
//        var outletdata= $(this).val()
        $.ajax({
            url: "/inventory/sales-returns/get-sales-code",
            type: "post",
            data: outletcode,
            success: function(data) {
                $(data.message).each(function()
                {
                    var option = $('<option />');
                    option.attr('value', this.id).text(this.code);
                    $('.sales-return-sales').append(option);
//                    $("#sales-return-sales").chosen(this);
                });
                $(".sales-return-sales").trigger("liszt:updated");
            }});

    });

});