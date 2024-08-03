/**
 *  * Created by Shamil on 21-Jan-16 10:51 AM
 * Organization FIS
 */

//var updateControls = function (addressComponents) {
//    $('#us5-street1').val(addressComponents.addressLine1);
//    $('#us5-city').val(addressComponents.city);
//    $('#us5-state').val(addressComponents.stateOrProvince);
//    $('#us5-zip').val(addressComponents.postalCode);
//    $('#us5-country').val(addressComponents.country);
//}
var showingMap = false;
var latitudeItem = null, longitudeItem = null;
var country = null, division = null, district = null, upazilla = null;
var mapID = 'map-location-picker';

$(function () {
    latitudeItem = $("[id*='latitude']");
    longitudeItem = $("[id*='longitude']");

    if (latitudeItem != null && longitudeItem != null &&
        longitudeItem.length > 0 && latitudeItem.length > 0) {

        var parent = longitudeItem.parent();

        var div = document.createElement('a');
        div.className = 'fbx-marker';
        div.innerHTML = '<i id="' + longitudeItem[0].id + '_map" class="fbx-icon-marker" ' +
        'style="position: absolute;margin: 2px 5px;"></i>';

        parent[0].appendChild(div);

        $('#' + longitudeItem[0].id + '_map').on('click', function () {
            $('#map-location-input-modal').modal('show');
            if (showingMap === false) {
                var geocoder = new google.maps.Geocoder();
                country = $("select[id*='0-country']");
                division = $("input[id*='0-division']");
                district = $("input[id*='0-state']");
                upazilla = $("input[id*='0-province']");
                console.log(country);
                console.log(division);
                console.log(district);
                console.log(upazilla);
                var address = null;
                //if (country != null && division != null && district != null && upazilla != null) {
                //    address = country[0].textContent + ', ' + division[0].textContent + ', '
                //    + district[0].textContent + ', ' + upazilla[0].textContent;
                //}
                console.log(address);
                var latitude = 4.624335;
                var longitude = -74.063644;
                var parameters = { };
                $.ajax({
                    url: 'http://freegeoip.net/json/',
                    data: parameters,
                    type: 'get',
                    dataType: 'json',
                    success: function (result) {
                        latitude = result.latitude;
                        longitude = result.longitude;
                        // the following line is because we want those parts to be executed after the ajax returns and updates the latitude and longitude values
                        initializeMap();
                    },
                    error: function (error) {
                        // the following line is because we want those parts to be executed after the ajax returns and updates the latitude and longitude values
                        initializeMap();
                    }
                });
                function initializeMap() {
                    var zoom = 7;
                    try {
                        if ($(latitudeItem[0]).val() != 0.00)
                            latitude = $(latitudeItem[0]).val();
                        if ($(longitudeItem[0]).val() != 0.00)
                            longitude = $(longitudeItem[0]).val();
                        zoom = 11;
                    } catch (e) {
                        console.log(e)
                    }
                    if (address !== null) {
                        geocoder.geocode({'address': address}, function (results, status) {
                            if (status == google.maps.GeocoderStatus.OK) {
                                latitude = results[0].geometry.location.lat();
                                longitude = results[0].geometry.location.lng();
                                console.log(latitude);
                                console.log(longitude);
                                zoom = 15;
                            }
                            $('#' + mapID).locationpicker({
                                location: {latitude: latitude, longitude: longitude},
                                radius: 50,
                                zoom: zoom,
                                inputBinding: {
                                    latitudeInput: $('#' + latitudeItem[0].id),
                                    longitudeInput: $('#' + longitudeItem[0].id)
                                }
                            });
                        });
                    } else {
                        $('#' + mapID).locationpicker({
                            location: {latitude: latitude, longitude: longitude},
                            radius: 50,
                            zoom: zoom,
                            inputBinding: {
                                latitudeInput: $('#' + latitudeItem[0].id),
                                longitudeInput: $('#' + longitudeItem[0].id)
                            }
                        });
                    }
                    showingMap = true;
                }
            }
        });
        $('#' + latitudeItem[0].id).on("change", function (e) {
            var value = parseFloat($(this).val());
            value = (parseInt(value * 1000000)) / 1000000;
            $(this).val(value);
        });
        $('#' + longitudeItem[0].id).on("change", function (e) {
            var value = parseFloat($(this).val());
            value = (parseInt(value * 1000000)) / 1000000;
            $(this).val(value);
        });

        $('#map-location-input-modal').find(".modal-footer").find(".btn-done")
            .unbind('click').on('click', function () {
                $('#map-location-input-modal').modal('hide');
            });
    }
});