/**
 * Created by Ashraful Islam on 1/5/2017.
 * Copied from GDFL project. Author was Ziaul Haque
 */


var _InitializeMarkerCluster = function _InitializeMarkerCluster(map, markers) {
    var mcOptions = {
        styles: [
            {
                url: "/static/img/marker.png",
                height: 96,
                width: 96,
                textColor: '#ffffff',
                textSize: 18
            }
        ],
        gridSize: 60,
        minimumClusterSize: 2
    };
    return new MarkerClusterer(map, markers, mcOptions);
};
