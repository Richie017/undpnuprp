/**
 * Created by Ziaul Haque on 1/9/2017.
 */

var charts = [];

var _initializeHighChart = function _initializeHighChart(data, element) {
    var options = data.options;
    options['series'] = data.data;
    return new Highcharts.chart(element, options);
};


var _drawSingleChart = function drawSingleChart(data, element) {
    var chart = null;
    chart = _initializeHighChart(data, element);
    if (chart != null) {
        var chart_details = {
            'chart': chart,
            'data': data.data,
            'options': data.options
        };

        charts.push(chart_details);
    }
    // remove highchart credit url
    $('.highcharts-credits').html("");
};