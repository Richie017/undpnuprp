/**
 * Created by tareq on 3/15/17.
 */

Highcharts.theme = {
    // colors: [
    //     "#2e3192", "#da1c5c", "#00a99d", "#f6b80c", "#b61291", "#666666", "#4a5cdd", "#ffa4c9", "#00dbc6", "#ffff61",
    //     "#d581ef", "#b3b3b3"
    // ],
    colors: [
        '#82E0AA',
        '#7FB3D5',
        '#52BE80',
        '#1F618D',
        '#17A589',
        '#95A5A6',
        '#AF7AC5',
        '#5D6D7E',
        '#212F3D'
    ],
    chart: {
        backgroundColor: {
            linearGradient: [0, 0, 500, 500],
            stops: [
                [0, 'rgb(255, 255, 255)'],
                [1, 'rgb(240, 240, 255)']
            ]
        },
    },
    title: {
        style: {
            color: '#00a99d',
            font: 'bold 16px tahoma, arial, helvetica, roboto, sans-serif'
        }
    },
    subtitle: {
        style: {
            color: '#666666',
            font: 'bold 12px tahoma, arial, helvetica, roboto, sans-serif'
        }
    },

    legend: {
        itemStyle: {
            font: '9pt tahoma, arial, helvetica, roboto, sans-serif',
            color: 'black'
        },
        itemHoverStyle: {
            color: 'gray'
        }
    }
};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);