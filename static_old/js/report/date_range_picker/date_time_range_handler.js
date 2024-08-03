/**
 * Created by asif on 3/13/17.
 */


// To add the functionality of this js follow below steps
$(function () {
    var start;
    var end;
    var date_range_initial = $("#id_date_range").prop("defaultValue");
    var startLimit = $("#id_date_range").data("start-limit");
    var endLimit = $("#id_date_range").data("end-limit");
    var openDirection = $("#id_date_range").data("open-direction");
    var initial_empty = $("#id_date_range").data("initial-empty");
    var initJson = {
        locale: {
            format: 'DD/MM/YYYY'
        },
        alwaysShowCalendars: true,
        linkedCalendars: false,
        ranges: {
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(7, 'days'), moment()],
            'Last 30 Days': [moment().subtract(30, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    };

    // If initial empty is true initially empty date range will be shown
    if (initial_empty) {
        initJson['autoUpdateInput'] = false;
        $("#id_date_range").val('');
    }
    // date range should be populated with some initial value
    else {

        // if an initial date range is given
        if (date_range_initial) {
            date_range_initial = date_range_initial.split("-");
            var start_date = date_range_initial[0].trim();
            var end_date = date_range_initial[1].trim();
            start = moment(start_date, 'DD/MM/YYYY');
            end = moment(end_date, 'DD/MM/YYYY');

        }
        // if both start and end limit is given
        else if (startLimit != undefined && endLimit != undefined) {
            start = moment().subtract(startLimit, 'days');
            end = moment().subtract(endLimit, 'days');

        }
        // if only start limit is given
        else if (startLimit != undefined) {
            endLimit = 1;
            start = moment().subtract(startLimit, 'days');
            end = moment().subtract(endLimit, 'days');

        }
        // if only end limit is given
        else if (endLimit != undefined) {
            startLimit = 30;
            start = moment().subtract(startLimit, 'days');
            end = moment().subtract(endLimit, 'days');

        }
        // nothing is given so By default show last 30 days report
        else {

            startLimit = 30;
            endLimit = 1;
            start = moment().subtract(startLimit, 'days');
            end = moment().subtract(endLimit, 'days');

        }

        initJson['startDate'] = start;
        initJson['endDate'] = end;

    }

    function cb(start, end) {
        $("#id_date_range").val(start.format('DD/MM/YYYY') + ' - ' + end.format('DD/MM/YYYY'));
        $('#dashboard-refresh-btn').trigger('click');
    }


    if (openDirection != undefined) {
        initJson['opens'] = openDirection;
    }

    $('.date-range-picker').daterangepicker(initJson, cb);


    // cb(start, end);

});
