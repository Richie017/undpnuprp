/**
 * Created by Ziaul Haque on 1/16/2018.
 */

var qa_tag_template = '<a href="#" class="document-tag-link" onclick="return qa_tag_click(this);">^<\/a>';
var qa_tag_only_comma = 0;
var qa_tags_examples = '';
var qa_tags_complete = ''; // Ex: 'django,redis-cache,mc-translation'
var qa_tags_max = 10;
var _count_added = 0;

function qa_html_unescape(html) {
    return html.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
}

function qa_html_escape(text) {
    return text.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function qa_tag_click(link) {
    var id_tag_input = $(link).data('id_tag_input');
    var id_tag_examples_title = $(link).data('id_tag_examples_title');
    var id_tag_complete_title = $(link).data('id_tag_complete_title');
    var id_tag_hints = $(link).data('id_tag_hints');
    var elem = document.getElementById(id_tag_input);

    var parts = qa_tag_typed_parts(elem);

    // removes any HTML tags and ampersand
    var tag = qa_html_unescape(link.innerHTML.replace(/<[^>]*>/g, ''));

    var separator = qa_tag_only_comma ? ', ' : ' ';

    // replace if matches typed, otherwise append
    var new_value = (parts.typed && (tag.toLowerCase().indexOf(parts.typed.toLowerCase()) >= 0))
        ? (parts.before + separator + tag + separator + parts.after + separator) : (elem.value + separator + tag + separator);

    // sanitize and set value
    if (qa_tag_only_comma) {
        elem.value = new_value.replace(/[\s,]*,[\s,]*/g, ', ').replace(/^[\s,]+/g, '');
    }
    else {
        elem.value = new_value.replace(/[\s,]+/g, ' ').replace(/^[\s,]+/g, '');
    }
    elem.focus();
    qa_tag_hints(null, id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints);
    return false;
}

function qa_tag_hints(skipcomplete, id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints) {
    var elem = document.getElementById(id_tag_input);
    var html = '';
    var completed = false;

    // first try to auto-complete
    if (qa_tags_complete && !skipcomplete) {
        var parts = qa_tag_typed_parts(elem);

        if (parts.typed) {
            html = qa_tags_to_html(
                (qa_html_unescape(qa_tags_examples + ',' + qa_tags_complete)).split(','),
                parts.typed.toLowerCase(), id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints
            );
            if (html) {
                completed = true;
            }
        }
    }

    // otherwise show examples
    if (qa_tags_examples && !completed) {
        html = qa_tags_to_html(
            (qa_html_unescape(qa_tags_examples)).split(','), null,
            id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints);
    }

    // set title visibility and hint list
    document.getElementById(id_tag_examples_title).style.display = (html && !completed) ? '' : 'none';
    document.getElementById(id_tag_complete_title).style.display = (html && completed) ? '' : 'none';
    document.getElementById(id_tag_hints).innerHTML = html;
}

function qa_tags_to_html(tags, matchlc, id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints) {
    var html = '';
    var added = 0;
    var tag_seen = {};

    for (var i = 0; i < tags.length; i++) {
        var tag = tags[i];
        var taglc = tag.toLowerCase();

        if (!tag_seen[taglc]) {
            tag_seen[taglc] = true;

            if ((!matchlc) || (taglc.indexOf(matchlc) >= 0)) { // match if necessary
                var inner = '';
                if (matchlc) { // if matching, show appropriate part in bold
                    var match_start = taglc.indexOf(matchlc);
                    var match_end = match_start + matchlc.length;
                    inner = '<span style="font-weight:normal;">'
                        + qa_html_escape(tag.substring(0, match_start)) + '<u>'
                        + qa_html_escape(tag.substring(match_start, match_end)) + '</u>'
                        + qa_html_escape(tag.substring(match_end))
                        + '</span>';
                } else {
                    // otherwise show as-is
                    inner = qa_html_escape(tag);
                }
                var updated_qa_tag_template = qa_tag_template.replace(/\^/g, inner.replace('$', '$$$$')) + ' '; // replace ^ in template, escape $s
                updated_qa_tag_template = $(updated_qa_tag_template).attr('data-id_tag_input', id_tag_input);
                updated_qa_tag_template.attr('data-id_tag_examples_title', id_tag_examples_title);
                updated_qa_tag_template.attr('data-id_tag_complete_title', id_tag_complete_title);
                updated_qa_tag_template.attr('data-id_tag_hints', id_tag_hints);
                html += updated_qa_tag_template.prop('outerHTML');
                if (++added >= qa_tags_max) {
                    break;
                }
            }
        }
    }
    return html;
}

function qa_caret_from_end(elem) {
    if (document.selection) { // for IE
        elem.focus();
        var sel = document.selection.createRange();
        sel.moveStart('character', -elem.value.length);
        return elem.value.length - sel.text.length;

    } else if (typeof(elem.selectionEnd) !== 'undefined') {
        // other browsers
        return elem.value.length - elem.selectionEnd;
    }
    else {
        // by default return safest value
        return 0;
    }
}

function qa_tag_typed_parts(elem) {
    var caret = elem.value.length - qa_caret_from_end(elem);
    var active = elem.value.substring(0, caret);
    var passive = elem.value.substring(active.length);

    // if the caret is in the middle of a word, move the end of word from passive to active
    if (active.match(qa_tag_only_comma ? /[^\s,][^,]*$/ : /[^\s,]$/)
        && (adjoinmatch = passive.match(qa_tag_only_comma ? /^[^,]*[^\s,][^,]*/ : /^[^\s,]+/))) {
        active += adjoinmatch[0];
        passive = elem.value.substring(active.length);
    }

    // find what has been typed so far
    var typed_match = active.match(qa_tag_only_comma ? /[^\s,]+[^,]*$/ : /[^\s,]+$/) || [''];

    return {
        before: active.substring(0, active.length - typed_match[0].length),
        after: passive,
        typed: typed_match[0]
    };
}

var loadTagSuggestionSelector = function ($mParent) {
    var $tagInputItem = null;
    var $parent = $mParent;
    if ($parent !== undefined) {
        $tagInputItem = $parent.find("input[class*='enable_tagging']");
    } else {
        $tagInputItem = $("input[class*='enable_tagging']");
    }

    if ($tagInputItem != null && $tagInputItem.length > 0) {
        var $div_parent = $tagInputItem.parent();

        var tag_input_level = $tagInputItem.attr('name');
        var id_tag_input = $tagInputItem.attr('id') + '_' + _count_added;
        var id_tag_examples_title = 'tag_examples_title_' + _count_added;
        var id_tag_complete_title = 'tag_complete_title_' + _count_added;
        var id_tag_hints = 'tag_hints_' + _count_added;
        $tagInputItem.attr('id', id_tag_input); // updating input element id to support tagging for formset


        var adding_div = document.createElement('div');
        adding_div.className = 'document-tag-tall-note';
        adding_div.innerHTML = '<span id="' + id_tag_examples_title + '" style="display:none;">Example ' + tag_input_level + ': </span>'
            + '<span id="' + id_tag_complete_title + '" style="display:none;">Matching ' + tag_input_level + ': </span>'
            + '<span id="' + id_tag_hints + '"></span>';

        $div_parent.append(adding_div);

        $tagInputItem.on("keyup", function (e) {
            qa_tag_hints(null, id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints);
        });

        $tagInputItem.on("mouseup", function (e) {
            qa_tag_hints(null, id_tag_input, id_tag_examples_title, id_tag_complete_title, id_tag_hints);
        });

        _count_added += 1;
    }
};


$(function () {
    var parameters = {};
    $.ajax({
        url: '/document-tags/?format=json&disable_pagination=1',
        type: 'get',
        data: parameters,
        dataType: 'json',
        success: function (result) {
            var _tag_array = [];
            $.each(result.items, function (index, object) {
                _tag_array.push(object.name);
            });
            qa_tags_complete = _tag_array.toString();
        },
        error: function (err) {
        }
    });
});
