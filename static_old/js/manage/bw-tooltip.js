/**
 * Created by tareq on 8/28/16.
 */
var initializeToolTip = function _initializeToolTip() {
    Tipped.create('.fis-plus-ico', "Create");
    Tipped.create('.fis-link-ico', "Add");
    Tipped.create('.fis-remove-ico', "Remove");
    Tipped.create('.fis-create-ico', "Edit");
    console.log("tipped-tooltip initialized.");
};

$(document).ready(function () {
    initializeToolTip();
});