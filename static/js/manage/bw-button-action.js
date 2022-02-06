/**
 *  * Created by Shamil on 03-Jan-16 1:55 PM
 * Organization FIS
 */

$(function () {

    $(document).on('click', "a.restore-action", function () {
        if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
            return false;
        }
        var tthis = $(this).attr('href');
        TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
            function () {
                window.location.href = tthis;
            },
            function () {

            });
        return false;

    });

    $(document).on('click', "a.manage-action", function () {
        if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
            return false;
        }
        if ($(this).hasClass('all-action') && $(this).hasClass('confirm-action')) {
            var tthis = $(this).attr('href');
            TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
                function () {
                    window.location.href = tthis;
                },
                function () {

                });
            return false;
        }

        else if ($(this).hasClass('prompt_expiry_date_required')) {
            var tthis = $(this).attr('href');
            TemplateAlert.Confirm("Expiry date missing", "Please set expiry date before stock out. You need to edit the order to set expiry dates.",
                function () {
                    window.location.href = tthis;
                },
                function () {

                },
                "Edit",
                "Cancel");
            return false;
        }

        if ($(this).hasClass('popup')) {
            var tthis_url = $(this).attr('href');
            window.open(tthis_url, "", "");
            window.focus();
            return false;
        }


        if ($(this).hasClass('multi-action') && !$(this).hasClass('ignore-multi')) {
            var tthis = $(this).attr('href');
            TemplateAlert.Confirm("Confirmation", "Are you sure you want to continue?",
                function () {
                    window.location.href = tthis;
                },
                function () {

                });
            return false;
        }
        return true;
    });

    $(document).on('click', '.run-importer', function () {
        var tthis = $(this);
        TemplateAlert.Confirm("Confirmation", "Clicking 'Yes' will start the importer. The page will auto refresh periodically. Please be patient while the importer runs.",
            function () {
                window.location.href = $(tthis).prop('href');
            },
            function () {

            });
        return false;
    });
});