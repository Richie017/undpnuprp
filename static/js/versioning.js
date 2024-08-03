$('.show-version-links-button').on('click', function () {
    $(this).css("display", "none");
    var version_link_div = $(this).parent().next();
    if (version_link_div) {
        version_link_div.css("display", "block");
    }
});