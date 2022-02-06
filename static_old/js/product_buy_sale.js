var op_products = [];

$(document).ready(function(){
    $("#table-productinstance").on("change",".hub_product, .hub_prod_quantity", function(){
        var tr = $(this).closest('tr');
        var product= tr.find('.hub_product');
        var dist=tr.find('.hub_product').val();
        var prodQuantity=tr.find('.hub_prod_quantity').val();
        var prodTPrice=tr.find('.hub_total_price');
        var price = 0;
        var product = null;
        for(var i =0; i < op_products.length; i++){
            if (op_products[i].id == dist){
                product = op_products[i];
                break;
            }
        }
        if (product == null){
            product=[];
            
        };
        price = product.tp;
    $(prodTPrice).val(price*(parseInt(prodQuantity == "" ? "0": prodQuantity)))
    });
    $('#id_hub').change(function(){
        var dist = $(this).val();

        if ($("#id_distributor").length > 0){
            $.ajax({
                url: "/administration/hubs/details/" + dist + "?format=json&property=distributors",
                type: "get",
                success: function(data) {
                    op_products = [];
                    $('#id_distributor').empty();
                    $(data.distributors).each(function()
                    {
                        var option = $('<option />');
                        option.attr('value', this.id).text(this.first_name + " " + this.last_name);
                        $('#id_distributor').append(option);
                    });
                    $("#id_distributor").trigger("liszt:updated");
                    $('#id_distributor').change();
                }});
        }else{
            $.ajax({
                url: "/inventory/operational-products/buy?disable_pagination=1&format=json&hub=" + dist,
                type: "get",
                success: function(data) {
                    $('#id_form-0-product').empty();
                    op_products = data.aaData;
                    $(data.aaData).each(function()
                    {
                        var option = $('<option />');
                        option.attr('value', this.id).text(this.name + " " + this.description);
                        $('#id_form-0-product').append(option);
                    });
                    $("#id_form-0-product").trigger("liszt:updated");
                    $("#id_form-0-product , #id_form-0-quantity").unbind('change').change(function(){
                        var price = 0;
                        var product = null;
                        for(var i =0; i < op_products.length; i++){
                            if (op_products[i].id == $("#id_form-0-product").val()){
                                product = op_products[i];
                                break;
                            }
                        }
                        price = product.tp;
//                        $("#id_unit_price").val(price);
                        $("#id_form-0-total_price").val(price * ($("#id_form-0-quantity").val() == "" ? "0": $("#id_form-0-quantity").val()));
                    });

                    $('#id_form-0-product').change();
                }});
        }

        if ($("#id_aparajita").length > 0) {
            $.ajax({
                url: "/administration/hubs/details/" + dist + "?format=json&property=aparajitas",
                type: "get",
                success: function(data) {
//                $("#sales-return-sales").chosen(data);
                    $('#id_aparajita').empty();
                    var option = $('<option />');
                    option.attr('value', '').text('Other User');
                    $('#id_aparajita').append(option);
                    $(data.aparajitas).each(function()
                    {
                        var option = $('<option />');
                        option.attr('value', this.id).text(this.first_name + " " + this.last_name);
                        $('#id_aparajita').append(option);
                    });
                    $("#id_aparajita").trigger("liszt:updated");
                }});
        }
    });

    $('#id_distributor').change(function(){
        var dist = $(this).val();
        $.ajax({
            url: "/inventory/operational-products/buy?disable_pagination=1&format=json&&dist=" + dist,
            type: "get",
            success: function(data) {
//                $("#sales-return-sales").chosen(data);
                $('#id_form-0-product').empty();
                op_products = data.aaData;
                $(data.aaData).each(function()
                {
                    var option = $('<option />');
                    option.attr('value', this.id).text(this.name + " " + this.description);
                    $('#id_form-0-product').append(option);
                });
                $("#id_form-0-product, #id_form-0-quantity").unbind('change').change(function(){
                    var price = 0;
                    var product = null;
                    for(var i =0; i < op_products.length; i++){
                        if (op_products[i].id == $("#id_form-0-product").val()){
                            product = op_products[i];
                            break;
                        }
                    }
                    price = product.tp;
//                    $("#id_unit_price").val(price);
                    $("#id_form-0-total_price").val(price * ($("#id_form-0-quantity").val() == "" ? "0": $("#id_form-0-quantity").val()));
                });
                $("#id_form-0-product").trigger("liszt:updated");
            }});

    });



    $('#id_hub').change();
});