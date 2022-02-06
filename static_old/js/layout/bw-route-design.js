/**
 *  * Created by Shamil on 14-Jan-16 2:52 PM
 * Organization FIS
 */


var mapRouteRequestNumber = 0;
//var color_list = ["#CC4949", "#49CC49", "#5649CC", "#CC49AE", "#49CCCA", "#CCCA49", "#9C49CC", "#ED7A1C", "#ED1C69"];
//var color_list = ["#C72424", "#24C724"];

var directionsDisplayNormal;
var directionsDisplayOptimized;
var directionsService;

var clients = null;
var map = null;
var client_markers = [];
var infoWindow = null;
var mapScript = null;

var parentClient = null;
var parentMarker = null;

var mapPolygon = null;

String.prototype.toTitleCase = function () {
    return this.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
};

var swapRows = function (row, sibling, parent, isDown) {
    var td1 = row.find('td:eq(0)');
    var td2 = sibling.find('td:eq(0)');
    var temp = td2[0].textContent;
    td2[0].textContent = td1[0].textContent;
    td1[0].textContent = temp;
    if (isDown == true) sibling = sibling.next();
    parent[0].insertBefore(row[0], sibling[0]);
    row.addClass('updated-row');
    window.setTimeout(function () {
        row.removeClass('updated-row');
    }, 1000);
};

var swapArrayValue = function (array, fIndex, sIndex) {
    array[fIndex] = array[fIndex] ^ array[sIndex];
    array[sIndex] = array[fIndex] ^ array[sIndex];
    array[fIndex] = array[fIndex] ^ array[sIndex];
    return array;
};

var swapArrayValueWithAttribute = function (array, attrib, fIndex, neighbour) {
    var sIndex = -1;
    for (var index = 0; index < array.length; index++) {
        if ((array[fIndex][attrib] - neighbour) === array[index][attrib])
            sIndex = index;
    }
    if (sIndex === -1) return;
    array[fIndex][attrib] = array[fIndex][attrib] ^ array[sIndex][attrib];
    array[sIndex][attrib] = array[fIndex][attrib] ^ array[sIndex][attrib];
    array[fIndex][attrib] = array[fIndex][attrib] ^ array[sIndex][attrib];
    return {
        fIndex: fIndex,
        sIndex: sIndex
    }
};

var getMarkedIndex = function (id) {
    var index = 0;
    var pks = $("#pk_sequence").val().split(",");
    for (; index < pks.length; index++) {
        if (parseInt(pks[index]) === id) break;
    }
    return {
        index: index,
        pks: pks
    };
};

var getMatchedIndex = function (array, id) {
    var index = 0;
    for (; index < array.length; index++) {
        if (array[index]['id'] === id) break;
    }
    return index;
};

var updateClientPkSerialInput = function (pks) {
    var value = "";
    for (var i = 0; i < pks.length; i++) {
        (i == 0) ? value += "" + pks[i] : value += "," + pks[i];
    }
    $("#pk_sequence").val(value);
};

var updateinfoWindow = function (marker1, marker2) {
    if (infoWindow !== null)
        infoWindow.setContent(marker1.sequence_no + ' -> ' + marker1.html);
    marker1.setIcon(getMarkerIconWithNumber(marker1.sequence_no, 'FE6256'))
    marker2.setIcon(getMarkerIconWithNumber(marker2.sequence_no, 'FE6256'))
};

function compare(a, b) {
    if (a['sequence_no'] < b['sequence_no'])
        return -1;
    else if (a['sequence_no'] > b['sequence_no'])
        return 1;
    else
        return 0;
}

function getSortedCopiedMarkerArray(markers) {
    var sorted_markers = [];
    for (var i = 0; i < markers.length; i++) {
        sorted_markers.push(markers[i]);
    }
    return sorted_markers.sort(compare);
}

var pullUp = function (id) {
    console.log(id);
    var object = getMarkedIndex(id);

    if (object.index > 0) {
        var tthis = $("#up_" + id);
        var row = tthis.closest('tr');
        swapRows(row, row.prev(), row.closest('tbody'), false);
        var updated_pks = swapArrayValue(object.pks, object.index, object.index - 1);
        updateClientPkSerialInput(updated_pks);

        var index = getMatchedIndex(clients, id);
        swapArrayValueWithAttribute(clients, 'sequence_no', index, 1);
        var indexes = swapArrayValueWithAttribute(client_markers, 'sequence_no', index, 1);
        //updateMapRoute(client_markers);
        updateMapRoute(getSortedCopiedMarkerArray(client_markers));
        updateinfoWindow(client_markers[indexes.fIndex], client_markers[indexes.sIndex]);
    }
};

var pullDown = function (id) {
    console.log(id);
    var object = getMarkedIndex(id);
    if (object.index < object.pks.length - 1) {
        var tthis = $("#down_" + id);
        var row = tthis.closest('tr');
        swapRows(row, row.next(), row.closest('tbody'), true);
        var updated_pks = swapArrayValue(object.pks, object.index, object.index + 1);
        updateClientPkSerialInput(updated_pks);

        var index = getMatchedIndex(clients, id);
        swapArrayValueWithAttribute(clients, 'sequence_no', index, -1);
        var indexes = swapArrayValueWithAttribute(client_markers, 'sequence_no', index, -1);
        //updateMapRoute(client_markers);
        updateMapRoute(getSortedCopiedMarkerArray(client_markers));
        updateinfoWindow(client_markers[indexes.fIndex], client_markers[indexes.sIndex]);
    }
};

var loadScript = function (src, callback) {
    if (mapScript == null) {
        mapScript = document.createElement("script");
        mapScript.type = "text/javascript";
        if (callback)script.onload = callback;
        document.getElementsByTagName("head")[0].appendChild(mapScript);
        mapScript.src = src;
    } else {
        initialize();
    }
};

var getMarkerIconWithNumber = function (number, color) {
    return 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + number + '|' + color + '|000000';
};

var updateMapRoute = function (markers) {
    if (mapRouteRequestNumber > 0) {
        setTimeout(function () {
            updateMapRoute(markers);
        }, 3000);
    }
    var origin = null;
    var destination = null;
    var waypoints = [];
    if (markers.length == 2) {
        origin = markers[0];
        destination = markers[markers.length - 1];
        google.maps.event.addListener(origin, 'click', function () {
            infoWindow.setContent(this.sequence_no + ' -> ' + this.html);
            infoWindow.open(map, this);
        });
        google.maps.event.addListener(destination, 'click', function () {
            infoWindow.setContent(this.sequence_no + ' -> ' + this.html);
            infoWindow.open(map, this);
        });
    } else if (markers.length == 1) {
        google.maps.event.addListener(markers[0], 'click', function () {
            infoWindow.setContent(this.sequence_no + ' -> ' + this.html);
            infoWindow.open(map, this);
        });
    } else if (markers.length < 1) {
        return;
    }
    var points = []
    points.push(parentMarker.position);
    if (markers.length > 0) {
        for (var i = 0; i < markers.length; i++) {
            var map_marker = markers[i];
            var next_marker = null;
            if (i == markers.length - 1) next_marker = markers[0];
            else if (i != markers.length - 1) next_marker = markers[i + 1];
            google.maps.event.addListener(map_marker, 'click', function () {
                infoWindow.setContent(this.sequence_no + ' -> ' + this.html);
                infoWindow.open(map, this);
            });
            if (i == 0) {
                origin = map_marker;
            } else if (i == markers.length - 1) {
                destination = map_marker;
            } else {
                waypoints.push({
                    location: map_marker.position,
                    stopover: true
                });
            }
            points.push(map_marker.position);
        }
    }
    if (mapPolygon !== null)
        mapPolygon.setMap(null);
    mapPolygon = new google.maps.Polygon({
        path: points,
        geodesic: true,
        fillColor: "#2e3192",
        fillOpacity: 0.05,
        strokeColor: '#CB3837',
        strokeOpacity: 1.0,
        strokeWeight: 4
    });
    mapPolygon.setMap(map);
};

var initialize = function () {
    var mapCanvas = document.getElementById('map_div');
    var zoom = 7;
    var mapCenter = new google.maps.LatLng(23.7808875, 90.2792375);
    var mapOptions = {
        center: mapCenter,
        zoom: zoom,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(mapCanvas, mapOptions);
    map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById('legend'));
    directionsDisplayNormal = new google.maps.DirectionsRenderer;
    directionsDisplayOptimized = new google.maps.DirectionsRenderer;
    directionsService = new google.maps.DirectionsService;

    if (clients !== null) {
        var bounds = new google.maps.LatLngBounds();
        infoWindow = new google.maps.InfoWindow({
            content: "Loading..."
        });
        var latlong;
        if (parentClient !== null) {
            latlong = new google.maps.LatLng(parentClient['latitude'], parentClient['longitude']);
            bounds.extend(latlong);
            parentMarker =
                new google.maps.Marker(
                    {
                        position: latlong,
                        map: map,
                        title: parentClient.name,
                        html: parentClient.code + ': ' + parentClient.name,
                        sequence_no: 0,
                        icon: getMarkerIconWithNumber(0, '1E9C1E')
                    }
                );
        }
        for (var index = 0; index < clients.length; index++) {
            var client = clients[index];
            infoWindow = new google.maps.InfoWindow({
                content: client.code + ': ' + client.name
            });
            latlong = new google.maps.LatLng(client['latitude'], client['longitude']);
            var marker =
                new google.maps.Marker(
                    {
                        position: latlong,
                        map: map,
                        title: client.name,
                        html: client.code + ': ' + client.name + client['buttonHtml'],
                        sequence_no: client['sequence_no'],
                        icon: getMarkerIconWithNumber(client['sequence_no'], 'FE6256')
                    }
                );
            client_markers.push(marker);
            bounds.extend(latlong);
        }
        map.fitBounds(bounds);
        map.setCenter(bounds.getCenter());

        updateMapRoute(getSortedCopiedMarkerArray(client_markers));
        //updateMapRoute(client_markers.sort(compare));
    }
};

var createTable = function (tableDiv, columnNames, items) {
    var table = document.createElement("TABLE");
    table.border = "1";
    table.setAttribute('class', 'table table-striped table-bordered table-condensed dataTable no-footer');

    if (items.length >= 0) {
        var thead = document.createElement("THEAD");
        var columnCount = columnNames.length;

        var row = thead.insertRow(-1);
        var headerCell;
        headerCell = document.createElement("TH");
        headerCell.innerHTML = 'Sequence';
        row.appendChild(headerCell);
        for (var i = 1; i < columnCount; i++) {
            headerCell = document.createElement("TH");
            headerCell.innerHTML = columnNames[i].toTitleCase();
            row.appendChild(headerCell);
        }
        row.appendChild(document.createElement("TH"));
        table.appendChild(thead);

        var tbody = document.createElement("TBODY");
        var value = "", weight = "";
        for (var i = 0; i < items.length; i++) {
            row = tbody.insertRow(-1);
            var id = items[i].id;
            (i == 0) ? value += "" + id : value += "," + id;
            (i == 0) ? weight += "" + 1000 * i : weight += "," + 1000 * i;
            for (var j = 0; j < columnCount; j++) {
                var cell = row.insertCell(-1);
                if (j == 0) {
                    cell.innerHTML = (i + 1) + '';
                }
                else if (columnNames[j] === 'name') {
                    cell.innerHTML = '<a href="' + items[i].detail_link + '" target="_blank">' +
                    items[i][columnNames[j]] + '</a>'
                } else {
                    cell.innerHTML = items[i][columnNames[j]];
                }
                items[i]['latitude'] = parseFloat(items[i]['latitude']);
                items[i]['longitude'] = parseFloat(items[i]['longitude']);
            }
            var button_cell = row.insertCell(-1);
            items[i]['sequence_no'] = i + 1;
            items[i]['buttonHtml'] = '&nbsp;&nbsp;<a id="marker_up_' + id + '" class="fbx-up" onclick="pullUp(' + id + ')">' +
            '<i class="fbx-icon-up"></i>' +
            '</a>&nbsp;&nbsp;' +
            '<a id="marker_down_' + id + '" class="fbx-down" onclick="pullDown(' + id + ')">' +
            '<i class="fbx-icon-down"></i>' +
            '</a>';
            button_cell.innerHTML = '&nbsp;&nbsp;<a id="up_' + id + '" class="fbx-up" onclick="pullUp(' + id + ')">' +
            '<i class="fbx-icon-up"></i>' +
            '</a>&nbsp;&nbsp;' +
            '<a id="down_' + id + '" class="fbx-down" onclick="pullDown(' + id + ')">' +
            '<i class="fbx-icon-down"></i>' +
            '</a>';

        }
        table.appendChild(tbody);
        $("#pk_sequence").val(value);
        $("#weight_sequence").val(weight);
    }


    var dvTable = document.getElementById(tableDiv);
    dvTable.innerHTML = "";
    dvTable.appendChild(table);

    clients = items;
    loadScript('http://maps.googleapis.com/maps/api/js?v=3&callback=initialize');
};

var resizeMapDiv = function () {
    var view_port_height = $("#viewport").height();
    var title_height = $("#section_header").height();
    var vph = view_port_height - title_height;
    $('#map_div').css({'height': vph + 'px'});
}

var loadClientData = function (select2, url, val) {
    if (typeof url !== 'undefined' && url !== '' && typeof val !== 'undefined' && val !== '') {
        $(select2).select2('enable', false);
        var id = $(select2).data('route-design-id');
        if (id === 'None' || typeof id === 'undefined' || id === '') {
            id = 0;
        }
        $.ajax({
            url: url + val + "&route_design_id=" + id,
            type: 'get',
            success: function (result) {
                if (result.success === true) {
                    clients = null;
                    client_markers = [];
                    infoWindow = null;
                    parentClient = result.items.splice(0, 1)[0];
                    createTable('client_table', result.headers, result.items);
                }
            },
            complete: function (e) {
                $(select2).select2('enable', true);
            }
        });
    }
};

$(function () {
    var route_select2 = "#id-route-select2";
    $(document).off('change', route_select2).on('change', route_select2, function () {
        loadClientData(this, $(this).data('clients-url'), $(this).val());
    });
    loadClientData(route_select2, $(route_select2).data('clients-url'), $(route_select2).val());

    $(document).on('click', ".btn-map-full-screen", function () {
        console.log('Clicked');
        var table_div = document.getElementById('client_table_div');
        if (table_div.style.display == 'inline-block') {
            table_div.style.display = 'none';
            $("#map_div_parent").removeClass('col-md-6').addClass('col-md-12');
            $("html, body").animate({scrollTop: $(document).height()}, 1000);
            google.maps.event.trigger(map, "resize");
        } else {
            table_div.style.display = 'inline-block';
            $("#map_div_parent").removeClass('col-md-12').addClass('col-md-6');
        }
    });
    resizeMapDiv();
});