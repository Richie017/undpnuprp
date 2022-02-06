/**
 * Created by ruddra on 12/28/14.
 */


$(document).ready(function () {

    $('#select_dropdown').change(function () {
        var e = document.getElementById("select_dropdown");
        var value = e.options[e.selectedIndex].value;

        $.ajax({
            url: "your-url",
            type: "post", // or "get"
            data: value,
            success: function (data) {

                alert(data.result);
            }
        });

    });
});