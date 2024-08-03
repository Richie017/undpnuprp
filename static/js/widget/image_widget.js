/**
 * Created by Ziaul Haque on 8/28/2016.
 */


$(document).ready(function () {
    function _previewImage(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $(input).parent().parent().find('img').attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    var $form = $('form');

    $form.on("change", "input[type='file']", function () {
        _previewImage(this);
    });

    function _clearImage(input) {
        // '<img class="thumbnail-border" height="100" width="100" src="/static/img/dummy-photo.png" />'
        if ($(input).is(':checked') == true) {
            $(input).data('src', $(input).parent().parent().find('img').attr('src'));
            $(input).parent().parent().find('input:file').attr('disabled', 'disabled');
            $(input).parent().parent().find('img').attr('src', '/static/img/dummy-photo.png');
        } else {
            $(input).parent().parent().find('input:file').removeAttr('disabled');
            $(input).parent().parent().find('img').attr('src', $(input).data('src'));
        }

    }

    $form.on("change", "input[class='clear_image']", function () {
        _clearImage(this);
    });

    $('.fake-file').find('input').val('No file chosen');
    $form.on("change", ".custom-upload input[type=file]", function () {
        var file_path = $(this).val();
        if (file_path == undefined || file_path == "") {
            $(this).parent().find('.fake-file input').val("No file chosen");
        }
        else {
            var _file = file_path.substring(file_path.lastIndexOf("\\") + 1);
            $(this).parent().find('.fake-file input').val(_file);
        }
    });
});

