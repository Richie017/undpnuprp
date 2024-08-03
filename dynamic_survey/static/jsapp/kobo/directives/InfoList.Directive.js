/* exported InfoListDirective */
/* global staticFilesUri */
'use strict';

kobo.directive('infoList', function ($http, $rootScope, $miscUtils, $location) {
    var rootUrl = window._rootUrl || '';
    var approve_permission = window._approve_permission;
    return {
        restrict: 'A',
        templateUrl: staticFilesUri + 'templates/InfoList.Template.html',
        scope: {
            items: '=',
            refreshItemList: '&',
            canAddNew: '@',
            name: '@',
            linkTo: '@',
            deleteItem: '&',
            canDelete: '@',
            addNewMessage: '=',
            isLoading: '=',
            cloneSurvey: '='
        },
        link: function (scope) {
            scope.kobocatLinkExists = function (item) {
                return window.koboConfigs && window.koboConfigs.kobocatServer;
            };
            scope.deleteSurveyDraft = function deleteSurveyDraft(item) {
                swal({
                    title: 'Are you sure you want to delete this item?',
                    showCancelButton: true,
                    reverseButtons: true,
                    confirmButtonColor: '#00a99d',
                    cancelButtonColor: '#d33',
                    iconColor: '#333'

                }).then(function () {
                    scope.deleteItem({item: item});
                    swal({
                        type: 'success',
                        title: 'You have succesfully deleted the item.',
                        confirmButtonColor: '#00a99d',
                        cancelButtonColor: '#d33',
                        iconColor: '#333'

                    })
                })
            };

            scope.publishSurvey = function publishSurveyDraft(item) {
                swal({
                    title: 'Are you sure you want to publish this survey?',
                    showCancelButton: true,
                    reverseButtons: true,
                    confirmButtonColor: '#00a99d',
                    cancelButtonColor: '#d33',
                    iconColor: '#333'
                }).then(function () {
                    window.location.href = scope.getPublishLink(item);
                })
            };
            scope.disableSurvey = function disableSurvey(item) {
                swal({
                    title: 'Are you sure you want to disable this survey?',
                    showCancelButton: true,
                    reverseButtons: true,
                    confirmButtonColor: '#00a99d',
                    cancelButtonColor: '#d33',
                    iconColor: '#333'

                }).then(function () {
                    window.location.href = scope.getMutateLink(item);
                })
            };
            scope.rePublishSurvey = function rePublishSurvey(item) {
                swal({
                    title: 'Are you sure you want to publish this survey again?',
                    showCancelButton: true,
                    reverseButtons: true,
                    confirmButtonColor: '#00a99d',
                    cancelButtonColor: '#d33',
                    iconColor: '#333'

                }).then(function () {
                    window.location.href = scope.getMutateLink(item);
                })
            };

            scope.getHrefFromDetailLink = function (item) {
                console.log();
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = item.detail_link;
                var linkTag = tempDiv.firstChild;
                var href = linkTag.getAttribute("href");
                return href;

            };

            $miscUtils.bootstrapSurveyUploader(function (response) {
                window.importFormWarnings = response.warnings || [];

                $location.path('/builder/' + response.survey_draft_id);
            });

            scope.getHashLink = function (item) {
                var linkTo = scope.linkTo;
                return linkTo ? '/' + linkTo + '/' + item.id : '';
            };

            scope.getPublishLink = function (item) {
                return rootUrl + '/approve/' + item.id;
            };

            scope.getMutateLink = function (item) {
                return rootUrl + '/mutate/' + item.id;
            };

            scope.itemError = function (item) {
                if (!item._summary) {
                    try {
                        item._summary = JSON.parse(item.summary);
                    } catch (e) {
                        item._summary = {};
                    }
                }
                return item._summary.error
            };

            scope.getLink = function (item, format) {
                if (!format) {
                    format = "xml";
                }
                return rootUrl + '/assets/' + item.id + "?format=" + format;
            };
            scope.getApprovePermission = function (item) {
                if (approve_permission === 'True') {
                    return true;
                }
                return false;
            };

            scope.toggleAddFormDropdown = function () {
                scope.showAddFormDropdown = scope.isShowAddFormDropdownShowing = !scope.showAddFormDropdown
            };

            scope.hideAddFormDropdown = function () {
                scope.showAddFormDropdown = false;
                scope.$apply();
            };

            scope.hideDownloadFormDropdown = function (item) {
                item.showDownloadDropdown = false;
                scope.$apply();
            };

            scope.toggleDownloadFormDropdown = function (item) {
                item.showDownloadDropdown = item.isShowing = !item.showDownloadDropdown
            };

            scope.canDelete = scope.canDelete === 'true';
            $rootScope.canAddNew = scope.canAddNew === 'true';

            $rootScope.activeTab = scope.name;
        }
    };
});