/*exported ImportController*/
'use strict';

kobo.controller('ImportController', ['$scope', '$rootScope', '$cookies', ImportController]);

function ImportController($scope, $rootScope, $cookies) {
    document.getElementById("dynamic_survey_form").style.display = "none";
    $rootScope.canAddNew = false;
    $rootScope.activeTab = 'Import CSV';
    $scope.csrfToken = $cookies.csrftoken;
}