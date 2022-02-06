/**
 * Created by shamil on 12/6/16.
 */
var map = null;
var markers = [];
var icons = [];
var center = {lat: 35.0, lng: 70.0};
var infowindows = [];

var $map_view = $('#map-view');
var $map_title = $("#map-title");
var $search_form = $('#search_form');

var update_map = function(data, action_callback) {
    $.ajax({
        url: '?format=json',
        type: 'post',
        data: data,
        dataType: 'json',
        success: function (result) {
            action_callback(result);
            $('body,html').animate({scrollTop: document.body.scrollHeight}, 1000);
            if (result != null) {
                $("#map-title").html(result.title);
                // for (var i = 0; i < markers.length; i++) {
                //     markers[i].setMap(null);
                // }
                // markers = [];
                // icons = [];
                // infowindows = [];
                // var bounds = new google.maps.LatLngBounds();
                // var center = {lat: 35, lng: 70};
                // for (var i = 0; i < result.items.length; i++) {
                //     var data = result.items[i];
                //     var lat = data.latitude;
                //     var lng = data.longitude;
                //     var myLatLng = new google.maps.LatLng(lat, lng);
                //     icons[i] = get_icon(data._type);
                //     markers[i] = new google.maps.Marker({
                //         position: myLatLng,
                //         title: data.title,
                //         icon: icons[i],
                //         _type: data._type
                //     });
                //
                //     infowindows[i] = "<div style='color: " + get_color(data._type) + ";'>Name of Client: " + data.client + "<br/>";
                //     infowindows[i] += "Total: " + data.total + "<br/>";
                //     infowindows[i] += "</div>";
                //
                //     bounds.extend(markers[i].position);
                //
                //     center.lat = (center.lat * i + lat) / (i + 1);
                //     center.lng = (center.lng * i + lng) / (i + 1);
                // }
                // if (result.items.length == 1) {
                //     bounds.extend(new google.maps.LatLng(34.543896, 69.160652));
                //     bounds.extend(new google.maps.LatLng(34.543896, 69.160652));
                //     map.setCenter(center)
                // }
                // else if (result.items.length > 1) {
                //     map.setCenter(bounds.getCenter());
                // } else {
                //     bounds.extend(new google.maps.LatLng(34, 70));
                //     bounds.extend(new google.maps.LatLng(35, 70));
                //     map.setCenter(center)
                // }
                // setTimeout(function () {
                //     for (var i = 0; i < markers.length; i++) {
                //         markers[i].setMap(map);
                //         attachMessage(map, markers[i], infowindows[i]);
                //     }
                //     map.fitBounds(bounds);
                // }, 500);
            }
        },
        error: function (ad) {
            $(tthis).addClass('generic-btn-style').removeClass('generic-danger-btn-style').html('Update Map');
        }
    })
};

$(function () {

    initializeDateTimePicker();

    resizeDiv($map_view, $map_title);
    map = initialize(center);
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById('legend'));

    //load map data
    $(".map-info").on('click', '.load-map-button', function () {
        var tthis = this;
        $(tthis).removeClass('generic-btn-style').addClass('generic-danger-btn-style').html('Please wait... Updating Map');
        var search_params = $search_form.serialize();
        update_map(search_params, function (result) {
            $(tthis).addClass('generic-btn-style').removeClass('generic-danger-btn-style').html('Update Map');
        });
    });
    $("ul.legend li").on('click', function (event) {
        var selected_marker_id = $(this).data('id');
        for (var i = 0; i < markers.length; i++) {
            if (markers[i].client_type == selected_marker_id) {
                if (!markers[i].getVisible()) {
                    markers[i].setVisible(true);
                } else {
                    markers[i].setVisible(false);
                }
            }
        }
    });

    var search_params = $search_form.serialize();
    update_map(search_params, function (result) {
    });
});
window.onresize = function (event) {
    resizeDiv($map_view, $map_title);
};