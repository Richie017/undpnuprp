/**
 * Created by shamil on 12/6/16.
 */

var initialize = function (center) {
    var mapOptions = {
        center: center,
        zoom: 10
    };
    return new google.maps.Map(document.getElementById('map-view'), mapOptions);
};

var attachMessage = function (map, marker, message) {
    var infowindow = new google.maps.InfoWindow({
        content: message,
        size: new google.maps.Size(50, 50)
    });
    google.maps.event.addListener(marker, 'click', function () {
        infowindow.open(map, marker);
    });
};

var get_icon = function (value) {
    var $legend_element = $('ul.legend');
    var _path = $legend_element.find("li[data-id=" + value + "] svg g path").attr('d');
    var _fill_color = $legend_element.find("li[data-id=" + value + "] svg g path").css('fill');
    var _svg_img = {
        url: '/static/img/marker-purple.svg',
        scaledSize: new google.maps.Size(20, 30),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(12, 12)
    };

    if (_path != null && _fill_color != null) {
        _svg_img = {
            path: _path,
            fillColor: _fill_color,
            fillOpacity: 1,
            scaledSize: new google.maps.Size(20, 30),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(12, 12),
            scale: .07
        };
    }
    return _svg_img;
};

var get_color = function (value) {
    var _color = $('ul.legend').find("li[data-id=" + value + "]").data('color');
    if (_color == null) {
        _color = '#dd00dd'
    }
    return _color;
};

var initializeDateTimePicker = function () {
    $(".date-selector").datepicker({
        format: 'dd-mm-yyyy'
    });
    $(".datetimepicker").datetimepicker({
        pick12HourFormat: true,
        pickTime: false
    });

    if ($("#id_from_date").val() == "") {
        var today = new Date();
        var one_month = (today.getDate() - 30);
        var one_month_old_date = new Date(today.setDate(one_month));
        $("#id_from_date").val($.datepicker.formatDate("d/mm/yy", one_month_old_date));
    }
    if ($("#id_to_date").val() == "") {
        var today = new Date();
        var yesterday = (today.getDate() - 1);
        var yesterday_date = new Date(today.setDate(yesterday));
        $("#id_to_date").val($.datepicker.formatDate("d/mm/yy", yesterday_date));
    }

    $(document).on("click", ".date-button-left", function () {
        var input = $(this).parent().find(".date-time-picker");
        input.val($.datepicker.formatDate("d/mm/yy", new Date($.datepicker.parseDate("d/mm/yy", input.val()).getTime() - (1 * 24 * 60 * 60 * 1000))));
    });

    $(document).on("click", ".date-button-right", function () {
        var input = $(this).parent().find(".date-time-picker");
        input.val($.datepicker.formatDate("d/mm/yy", new Date($.datepicker.parseDate("d/mm/yy", input.val()).getTime() + (1 * 24 * 60 * 60 * 1000))));
    });
};

var resizeDiv = function ($map_view, $map_title) {
    var window_height = $(window).height();
    var title_height = $map_title.height();
    var vph = window_height - title_height * 1.5;
    $map_view.css({'height': vph + 'px'});
};