/**
 * Created by Mahmud on 11/5/2014.
 */


var map = null;
var markers = [];
var center = {lat:0, lng:0};
var route_points = [];
var directionsDisplay;
var way_points  = [];
var directionsService = new google.maps.DirectionsService();
function initialize(center) {
    var mapOptions = {
        center: center,
        zoom: 8
    };

    return new google.maps.Map(document.getElementById('map-view'), mapOptions);
}
$(function(){
    $("#ul-manage-tab").find('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        directionsDisplay = new google.maps.DirectionsRenderer();
        markers = [];
        route_points = [];
        way_points = [];
        for(var i = 0; i < mapData.length; i++){
            var lat = parseFloat(mapData[i].location.latitude);
            var lng = parseFloat(mapData[i].location.longitude);
            markers[i] = new google.maps.Marker({
                position: new google.maps.LatLng(lat, lng),
                animation: google.maps.Animation.DROP,
                title: mapData[i].transport_type
            });
            center.lat = (center.lat * i + lat)/(i+1);
            center.lng = (center.lng * i + lng)/(i+1);

            route_points[route_points.length] = new google.maps.LatLng(lat, lng);
            way_points.push({location: new google.maps.LatLng(lat, lng), stopover:true});
        }
        map = initialize(center);
        for(var i = 0; i < markers.length; i++) {
            markers[i].setMap(map);
        }

        var route_path = new google.maps.Polyline({
            path: route_points,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });

        route_path.setMap(map);

        //directionsDisplay.setMap(map);
        //
        //var request = {
        //    origin: route_points[0],
        //    destination: route_points[route_points.length - 1],
        //    waypoints: way_points,
        //    optimizeWaypoints: true,
        //    travelMode: google.maps.TravelMode.DRIVING
        //};
        //directionsService.route(request, function(response, status) {
        //    if (status == google.maps.DirectionsStatus.OK) {
        //        //directionsDisplay.setDirections(response);
        //        //var route = response.routes[0];
        //        //var summaryPanel = document.getElementById('directions_panel');
        //        //summaryPanel.innerHTML = '';
        //        //// For each route, display summary information.
        //        //for (var i = 0; i < route.legs.length; i++) {
        //        //    var routeSegment = i + 1;
        //        //    summaryPanel.innerHTML += '<b>Route Segment: ' + routeSegment + '</b><br>';
        //        //    summaryPanel.innerHTML += route.legs[i].start_address + ' to ';
        //        //    summaryPanel.innerHTML += route.legs[i].end_address + '<br>';
        //        //    summaryPanel.innerHTML += route.legs[i].distance.text + '<br><br>';
        //        //}
        //    }
        //});
    })
});