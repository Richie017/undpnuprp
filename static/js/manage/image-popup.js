/**
 * Created by tareq on 6/1/16.
 */

var initialize_popup_images = function (parent) {
    var all_thumbnail_elements, thumbnail_gallery;
    if (parent == undefined || parent == null) {
         all_thumbnail_elements = $('.popup-thumbnail');
         thumbnail_gallery = $('.thumbnail-gallery');
    } else {
        all_thumbnail_elements = $(parent).find('.popup-thumbnail');
        thumbnail_gallery = $(parent).find('.thumbnail-gallery');
    }
    all_thumbnail_elements.magnificPopup({
        type: 'image',
        mainClass: 'mfp-fade'
    });

    thumbnail_gallery.each(function () { // the containers for all your galleries
        $(this).magnificPopup({
            delegate: 'a', // the selector for gallery item
            type: 'image',
            gallery: {
                enabled: true
            },
            image: {
                titleSrc: function (item) {
                    return $(item.el).parent().find('span').html();
                }
            }
        });
    });
};

$(function () {
    initialize_popup_images();
});