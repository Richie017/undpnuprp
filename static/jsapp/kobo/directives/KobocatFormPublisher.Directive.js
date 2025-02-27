kobo.directive('kobocatFormPublisher', ['$http', '$api', '$miscUtils', '$routeTo', function ($http, $api, $miscUtils, $routeTo) {
    return {
        scope: {
            item: '='
        },
        templateUrl: staticFilesUri + 'templates/KobocatFormPublisher.Template.html',
        link: function (scope, element, attributes) {
            var dialog = element.find('.forms__kobocat__publisher');
            scope.publish = function () {
                // var spinner = '<i class="fa fa-spin fa-spinner"></i> Deploying Project';
                // $('button.save-button .ui-button-text').html(spinner);
                // $('button.save-button').addClass('save-button--deploying');
                // function success (results, headers) {
                //     $('button.save-button .ui-button-text').html('Deploy and View New Project');
                //     $('button.save-button').removeClass('save-button--deploying');
                //     scope.close();
                //     $miscUtils.alert('Survey Publishing succeeded');
                //     $routeTo.external(results.published_form_url);
                // }
                // function fail (response) {
                //     $('button.save-button .ui-button-text').html('Deploy and View New Project');
                //     $('button.save-button').removeClass('save-button--deploying');
                //     scope.show_form_name_exists_message = true;
                //     scope.error_message = 'Survey Publishing failed: ' + (response.data.text || response.data.error || response.data.detail);
                // }
                //
                // var id = scope.form_name ? dkobo_xlform.model.utils.sluggifyLabel(scope.form_name) : '';
                // $api.surveys
                //     .publish({id: scope.item.id, title:scope.form_label, id_string: id}).then(success, fail);
                $http({
                    method: 'GET',
                    url: window._rootUrl + '/parser/' + scope.item.id
                }).then(function successCallback(response) {
                    // this callback will be called asynchronously
                    // when the response is available
                    dialog.dialog('close');
                    swal({
                        title: 'Success!',
                        text: 'You have successfully deployed the survey',
                        type: 'success',
                        confirmButtonText: 'Done'
                    })

                }, function errorCallback(response) {
                    // called asynchronously if an error occurs
                    // or server returns response with an error status
                    dialog.dialog('close');
                    swal({
                        title: 'Survey Deployment Failed!',
                        text: response.data,
                        type: 'error',
                        confirmButtonText: 'Close'
                    })


                });
            };

            scope.form_label = scope.item.name;

            scope.open = function () {
                scope.show_publisher = true;
                dialog.dialog('open');
            };
            scope.close = function () {
                scope.show_publisher = false;
                dialog.dialog('close');
            };
            scope.show_publisher = false;

            scope.show_form_name_exists_message = false;
            scope.get_form_id = function (item) {
                if (_.isString(item)) {
                    item.summary = JSON.parse(item.summary);
                }
                item.summary.form_id;
            };
            scope.form_name = scope.get_form_id(scope.item);

            dialog.dialog({
                modal: true,
                height: 325,
                width: 325,
                autoOpen: false,
                title: 'Deploy Survey',
                draggable: false,
                resizable: false,
                position: {my: "center", at: "center", of: ".main"},
                buttons: [
                    {
                        text: "Deploy This Survey Project",
                        "class": 'save-button',
                        click: scope.publish
                    },
                    {
                        text: "Cancel",
                        "class": 'cancel-button',
                        click: scope.close
                    }
                ],
                open: function () {
                    $('.ui-widget-overlay').bind('click', function () {
                        dialog.dialog('close');
                    });
                }

            });
        }
    }
}]);