/**
 * Created by shakib on 3/27/2017.
 */
$(function () {
    try {
        var language = '', $language_input = $('input#site-language');
        if ($language_input.length > 0) {
            language = '/' + $language_input.val();
        }
        var selected_header = null;
        var true_path = window.location.pathname.replace(language, '');
        var $header_ul = $('ul.navbar-nav.fbx-nav');
        menu_config.sort(function (a, b) {
            return (a['order'] < b['order']) ? -1 : ((a['order'] > b['order']) ? 1 : 0);
        });
        for (var index = 0; index < menu_config.length; index++) {
            var top_module = menu_config[index];
            var selected = '';
            var top_module_url = language + top_module['link'];
            var keys = Object.keys(url_mapping).filter(function (prop) {
                return true_path.indexOf(prop) === 0;
            });
            if (keys.length > 0) {
                if (url_mapping.hasOwnProperty(keys[0]) && url_mapping[keys[0]] === top_module['title']) {
                    selected_header = top_module;
                    selected = 'active';
                    url = '#';
                }
            }
            var header_node =
                '<li class="fbx-menuitem text-center ' + selected + '"> \
                    <a href="' + top_module_url + '"> \
                        <i class="fbx-icon ' + top_module['icon'] + '"></i> \
                        <span>' + top_module['title'] + '</span> \
                    </a> \
                </li>';
            $header_ul.append(header_node);
        }
        var $sidebar = $('div.fbx-sidebar');
        if (selected_header !== null) {
            for (var index = 0; index < selected_header.items.length; index++) {
                var group_module = selected_header.items[index];
                var open = '';
                if (group_module.items.length < 1) {
                    continue;
                }
                var menu_item_list = '';
                for (var ind = 0; ind < group_module.items.length; ind++) {
                    var menu_item = group_module.items[ind];
                    var url = language + menu_item['link'];
                    var active = '';
                    if (true_path.indexOf(menu_item['link']) === 0) {
                        active = 'active';
                        open = 'parentmenubox_open'
                    }
                    menu_item_list +=
                        '<li class="leftmenuitems_sec_level ' + active + '">\
                            <a href="' + url + '">' + menu_item['title'] + '</a>\
                        </li>';
                }
                var group_item =
                    '<div class="parentmenubox ' + open + '"> \
                            <a class="parentmenuboxtrig">\
                                <span>' + group_module['title'] + '</span> \
                            </a> \
                        <div class="parentmenubox_wrap"> \
                            <ul class="list-unstyled leftmenuitems leftmenuitems_first_level">' + menu_item_list + '</ul> \
                        </div> \
                    </div>';
                $sidebar.append(group_item);
            }
        }
    } catch (e) {
        console.log('menu_config', e);
    }
});