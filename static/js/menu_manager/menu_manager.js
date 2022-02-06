var oldContainer;
var draggingItem;
var group = $("ol.menu_manager").sortable({
    group: 'serialization',
    handle: 'i.drag-icon',
    afterMove: function (placeholder, container) {
        if (oldContainer != container) {
            if (oldContainer)
                oldContainer.target.removeClass("active");
            container.target.addClass("active");
            oldContainer = container;
        }
    },
    onDragStart: function ($item, container, _super, event) {
        draggingItem = $item.parent();
        _super($item, container);
    },
    onDrop: function ($item, container, _super) {
        container.target.removeClass("active");
        _super($item, container);
    },
    isValidTarget: function ($item, container) {
        if ((draggingItem.hasClass('side_module') && container.target.hasClass('side_module')) ||
            (draggingItem.hasClass('side_menu_item') && container.target.hasClass('side_menu_item'))) {
            return true;
        } else {
            return false;
        }
    }
});

$(".switch-container").on("click", ".switch", function (e) {
    var method = $(this).hasClass("active") ? "enable" : "disable";
    $(e.delegateTarget).next().sortable(method);
});

$("ol.side_module > li").each(function () {
    $(this).click(function (e) {
        e.stopPropagation();
    });
});

$("ol.side_menu_item li").click(function (e) {
    e.stopPropagation();
});

$("ol.menu_manager > li > p").each(function () {
    $(this).click(function (e) {
        $(this).parent().children().children().slideToggle();
        e.stopPropagation();
    });
});

$("ol.side_module > li > p").each(function () {
    $(this).click(function (e) {
        $(this).parent().children().children().slideToggle();
        e.stopPropagation();
    });
});

$(function () {
    $("#submit_top").on('click', function () {
        var data = group.sortable("serialize").get();
        $('#menu_data').val(JSON.stringify(data));
        console.log(data);
        $('#submit').click();
    });

    $("#btn_cancel").on('click', function () {
        history.go(-1);
    });

    $('.edit-group-icon').each(function (e) {
        var id = $(this).data('id');
        $(this).click(function (e) {
            var id = $(this).data('id');
            var $input_box = $('li input.edit-group-box[data-id=' + id + ']');
            $input_box.toggleClass('hide');
            if ($input_box.hasClass('hide')) {
                var value = $input_box.val();
                var $list_elem = $('li.group-li[data-id=' + id + ']');
                $list_elem.attr('data-name', value);
                $('p.group-p[data-id=' + id + ']').html(value);
            }
        });
        var $input_box = $('li input.edit-group-box[data-id=' + id + ']');
        $input_box.on('keypress', function (event) {
            if (event.which === 13) {
                var id = $(this).data('id');
                $input_box.toggleClass('hide');
                if ($input_box.hasClass('hide')) {
                    var value = $input_box.val();
                    var $list_elem = $('li.group-li[data-id=' + id + ']');
                    $list_elem.attr('data-name', value);
                    $('p.group-p[data-id=' + id + ']').html(value);
                }
            }
        });
    });

    $('.edit-item-icon').each(function (e) {
        var id = $(this).data('id');
        $(this).click(function (e) {
            var id = $(this).data('id');
            var $input_box = $('li input.edit-item-box[data-id=' + id + ']');
            $input_box.toggleClass('hide');
            if ($input_box.hasClass('hide')) {
                var value = $input_box.val();
                var $list_elem = $('li.item-li[data-id=' + id + ']');
                $list_elem.attr('data-name', value);
                $('p.item-p[data-id=' + id + ']').html(value);
            }
        });
        var $input_box = $('li input.edit-item-box[data-id=' + id + ']');
        $input_box.on('keypress', function (event) {
            if (event.which === 13) {
                var id = $(this).data('id');
                $input_box.toggleClass('hide');
                if ($input_box.hasClass('hide')) {
                    var value = $input_box.val();
                    var $list_elem = $('li.item-li[data-id=' + id + ']');
                    $list_elem.attr('data-name', value);
                    $('p.item-p[data-id=' + id + ']').html(value);
                }
            }
        });
    });
});