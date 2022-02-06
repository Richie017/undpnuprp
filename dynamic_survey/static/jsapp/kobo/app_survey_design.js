/* global angular */
/* global TopLevelMenuDirective */
/* global InfoListDirective */
/* global BuilderDirective */
/* global userDetailsFactory */
/* global restApiFactory */
/* global RouteToService */
/* global ConfigurationService */
/* global MiscUtilsService */
/* global staticFilesUri */
/* global $ */
/* global log */

'use strict';

var kobo = angular.module('dkobo', [
    'ngRoute',
    'ngCookies',
    'ngResource',
    'ui.utils',
    'ui.select',
    'ngSanitize'
]);
if (window._staticUrl !== undefined) {
    kobo.config(function ($sceDelegateProvider) {
            $sceDelegateProvider.resourceUrlWhitelist([
                // Allow same origin resource loads.
                'self',
                // Allow loading from our assets domain. **.
                'https://' + window._staticUrl + '/**',
                // 'https://assetsnuprpinfo.s3.amazonaws.com/**',
            ]);
        }
    );
}
kobo.filter('propsFilter', function () {
    return function (items, props) {
        var out = [];
        if (angular.isArray(items)) {
            items.forEach(function (item) {
                var itemMatches = false;
                var keys = Object.keys(props);
                for (var i = 0; i < keys.length; i++) {
                    var prop = keys[i];
                    var text = props[prop].toLowerCase();
                    var words = text.split(' ');
                    for (var j = 0; j < words.length; j++) {
                        if (item[prop].toString().toLowerCase().indexOf(words[j]) !== -1) {
                            itemMatches = true;
                            break;
                        }
                    }
                    if (itemMatches === true) {
                        break;
                    }
                }
                if (itemMatches) {
                    out.push(item);
                }
            });
        } else {
            // Let the output be the input untouched
            out = items;
        }
        return out;
    };
});

kobo.config(function ($routeProvider, $locationProvider, $httpProvider) {

    //http://django-angular.readthedocs.org/en/latest/integration.html

    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

    $routeProvider.when('/forms', {
        templateUrl: staticFilesUri + 'templates/Forms.Template.html',
        controller: 'FormsController'
    });


    $routeProvider.when('/builder/:id', {
        templateUrl: staticFilesUri + 'templates/Builder.Template.html',
        controller: 'BuilderController'
    });

    $routeProvider.when('/viewer/:id', {
        templateUrl: staticFilesUri + 'templates/Viewer.Template.html',
        controller: 'BuilderController'
    });


    $routeProvider.otherwise({
        redirectTo: '/forms'
    });
});
