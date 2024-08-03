$(document).ready(function () {
    $("#id_survey_target").on('change', function () {
        var $el = $("#id_target_level");
        if (this.value === 'none') {
            $el.empty(); // remove old options'
            $el.select2().trigger('change');

        }

        else if (this.value === 'client') {
            $el.empty(); // remove old options
            var client_choice_list = $("#id_survey_target").data('client');
            $.each(client_choice_list, function (key, value) {
                $el.append($("<option></option>")
                    .attr("value", value).text(key));
            });
            $el.select2().trigger('change');

        }
        else if (this.value === 'infrastructure_unit') {
            $el.empty(); // remove old options
            var iu_choice_list = $("#id_survey_target").data('infrastructure-unit');
            $.each(iu_choice_list, function (key, value) {
                $el.append($("<option></option>")
                    .attr("value", value).text(key));
            });
            $el.select2().trigger('change');
        }
    })
});