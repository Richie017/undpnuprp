/**
 * Created by Ziaul Haque on 6/6/2016.
 */

$(document).on('click', ".load-keyinfo", function () {
    if ($(this).attr('disabled') == 'disabled' || $(this).hasClass('disabled')) {
        return false;
    }
    $('#detail-modal-form').find('.modal-body').html('').addClass('loading');
    if ($(this).data('wide') == '1') {
        $('#detail-modal-form').addClass('wide-modal')
    } else {
        $('#detail-modal-form').removeClass('wide-modal')
    }
    var tthis = this;
    
    $('#detail-modal-form').unbind('shown').on('shown', function () {
        $.ajax({
            url: $(tthis).attr('href'),
            type: 'get',
            success: function (data) {
                $('#detail-modal-form').find('.modal-body').removeClass('loading');
                $('#detail-modal-form').find(".modal-header>h4").html($(tthis).data('title') == null ? "Key Information" : "Key Information ("+$(tthis).data('title') +")");
                $('#detail-modal-form').find(".modal-body").html(data);
                $('#detail-modal-form').find('div.ajax-container').attr('data-url', $(tthis).attr('href'));
            }
        });
    });
    $("#detail-modal-form").modal('show');
    return false;
});
