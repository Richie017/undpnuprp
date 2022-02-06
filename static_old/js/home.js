/**
 * Created by ActiveHigh on 5/4/14.
 */

$(function(){
    var request = $.ajax({
            url:"/",
            type: "GET",
            data: {noodles : "noodles" , chips : "chips", chicken : "chicken" },
            success:function(data)
            {
                console.log(data)
                },
            });
//    var d1 = [];
//    var _delta = 60 * 60 * 24;
//    var _date = new Date().getTime() - (10 * _delta);
//    for (var i = _date;i < new Date().getTime(); i += _delta) {
//        d1.push([i, noodles ]);
//    }
//
//    var d2 = [];
//    for (var i = _date;i < new Date().getTime(); i += _delta) {
//        d2.push([i,  chips ]);
//    }
//
//    var d3 = [];
//    for (var i = _date;i < new Date().getTime(); i += _delta) {
//        d3.push([i, chicken ]);
//    }
//
//    //home page graph
//    var sales_charts = $('#sales-charts').css({'width':'100%' , 'height':'220px'});
//    $.plot("#sales-charts", [
//        { label: "Noodles", data: d1 },
//        { label: "Chips", data: d2 },
//        { label: "Fried Chicken", data: d3 }
//    ], {
//        hoverable: true,
//        shadowSize: 0,
//        series: {
//            lines: { show: true },
//            points: { show: true }
//        },
//        xaxis: {
//            ticks: 20,
//            mode: "time",
//            minTickSize: [1, "day"]
//        },
//        yaxis: {
//            ticks: 10,
//            min: 0,
//            max: 250,
//            tickDecimals: 1
//        },
//        grid: {
//            backgroundColor: { colors: [ "#fff", "#fff" ] },
//            borderWidth: 1,
//            borderColor:'#555'
//        }
//    });
//
//    $.plot("#product-popularity-charts", [
//        { label: "Noodles", data: d1},
//        { label: "Chips", data: d2},
//        { label: "Fried Chicken", data: d3}
//    ], {
//        series: {
//            bars: {show: true, fill: true, barWidth: 50, align: "left"}
//        },
//        xaxis: {
//            mode: "time",
//            minTickSize: [1, "day"],
//            timeFormat: "%y/%m/%d"
//        },
//        yaxis: {
//            ticks: 10,
//            min: 0,
//            max: 250,
//            tickDecimals: 1
//        },
//        grid: {
//            backgroundColor: { colors: [ "#fff", "#fff" ] },
//            borderWidth: 1,
//            borderColor:'#555'
//        }
//    });
});
