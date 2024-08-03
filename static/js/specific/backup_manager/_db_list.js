/**
 * Created by Ziaul Haque on 5/16/2016.
 */


var _loadDataTable = function loadDataTable() {
    $('.fileTable').dataTable({
        "bSort": false,
        "bFilter": true,
        "bInfo": true,
        "bJQueryUI": false,
        "bPaginate": true
    }).fnAdjustColumnSizing();
    InitializeDataTableCss();
};

function InitializeDataTableCss() {
    var _dataTableSearchBox = $('.dataTables_filter label');
    var _dataTableSearchField = $('.dataTables_filter input');
    var _dataTableLengthBox = $('.dataTables_length select');
    _dataTableSearchBox.contents().get(0).remove();
    _dataTableSearchField.attr({
        'placeholder': 'Search',
        'class': 'form-control input-sm'
    });
    _dataTableSearchField.css({
        'margin-left': '-2px',
        'border-radius': '2px'

    });
    _dataTableLengthBox.css({
        'background-color': '#fff',
        'padding': '3px 10px',
        'border': '1px solid #ccc',
        'display': 'inline-block',
        'border-radius': '2px'
    });
}