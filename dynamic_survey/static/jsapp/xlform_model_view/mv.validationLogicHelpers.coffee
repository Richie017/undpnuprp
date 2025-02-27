define 'cs!xlform/mv.validationLogicHelpers', [
  'xlform/model.validationLogicParser',
  'cs!xlform/mv.skipLogicHelpers'
], ($validationLogicParser, $skipLogicHelpers) ->

  validationLogicHelpers = {}

  class validationLogicHelpers.ValidationLogicHelperFactory extends $skipLogicHelpers.SkipLogicHelperFactory
    create_presenter: (criterion_model, criterion_view) ->
      return new validationLogicHelpers.ValidationLogicPresenter criterion_model, criterion_view, @current_question, @survey, @view_factory
    create_builder: () ->
      return new validationLogicHelpers.ValidationLogicBuilder @model_factory, @view_factory, @survey, @current_question, @
    create_context: () ->
      return new validationLogicHelpers.ValidationLogicHelperContext @model_factory, @view_factory, @, @serialized_criteria

  class validationLogicHelpers.ValidationLogicPresenter extends $skipLogicHelpers.SkipLogicPresenter
    change_question: () -> return

  class validationLogicHelpers.ValidationLogicBuilder extends $skipLogicHelpers.SkipLogicBuilder
    _parse_skip_logic_criteria: (criteria) ->
      return $validationLogicParser criteria

    _get_question: () ->
      @current_question

    build_empty_criterion: () ->
      operator_picker_view = @view_factory.create_operator_picker @current_question.get_type()

      response_value_view = @view_factory.create_response_value_view @current_question, @current_question.get_type(), @_operator_type()

      presenter = @build_criterion_logic @model_factory.create_operator('empty'), operator_picker_view, response_value_view

      presenter.model.change_question @current_question.cid

      return presenter

    questions: () ->
      [@current_question]
    _operator_type: () ->
      operator_type = super
      if !operator_type?
        operator_type_id = @current_question.get_type().operators[0]
        operator_type = $skipLogicHelpers.operator_types[if operator_type_id == 1 then @current_question.get_type().operators[1] else operator_type_id]
      return operator_type

  class validationLogicHelpers.ValidationLogicHelperContext extends $skipLogicHelpers.SkipLogicHelperContext
    use_mode_selector_helper: () ->
      @state = new validationLogicHelpers.ValidationLogicModeSelectorHelper @view_factory, @
      @render @destination
    use_hand_code_helper: () ->
      @state = new validationLogicHelpers.ValidationLogicHandCodeHelper(@state.serialize(), @builder, @view_factory, @)
      if @questionTypeHasNoValidationOperators()
        @state.button = @view_factory.create_empty()
      @render @destination
      return
    constructor: (@model_factory, @view_factory, @helper_factory, serialized_criteria) ->
      @state = serialize: () -> return serialized_criteria
      if @questionTypeHasNoValidationOperators()
        @use_hand_code_helper()
      else
        super
    questionTypeHasNoValidationOperators: () ->
      operators = $skipLogicHelpers.question_types[@helper_factory.current_question.getValue('type').split(' ')[0]]?.operators
      if !operators
        operators = $skipLogicHelpers.question_types['default'].operators
      operators.length == operators[0]

  class validationLogicHelpers.ValidationLogicModeSelectorHelper extends $skipLogicHelpers.SkipLogicModeSelectorHelper
    constructor: (view_factory, @context) ->
      super
      @handcode_button = view_factory.create_button '<i>${}</i> Manually enter your validation logic in XLSForm code', 'skiplogic__button skiplogic__select-handcode'

  class validationLogicHelpers.ValidationLogicHandCodeHelper extends $skipLogicHelpers.SkipLogicHandCodeHelper
    render: ($destination) ->
      $destination.replaceWith(@$handCode)
      @button.render().attach_to @$handCode
      @button.bind_event 'click', () =>
        @$handCode.replaceWith($destination)
        @context.use_mode_selector_helper()
    serialize: () ->
      @textarea.val()
    constructor: () ->
      super
      @$handCode = $("""
        <div class="card__settings__fields__field">
          <label for="#{@context.helper_factory.current_question.cid}-handcode">Validation Code:</label>
          <span class="settings__input">
            <input type="text" name="constraint" id="#{@context.helper_factory.current_question.cid}-handcode" class="text" value="#{@criteria}">
          </span>
        </div>
      """)
      @textarea = @$handCode.find('#' + @context.helper_factory.current_question.cid + '-handcode')


  validationLogicHelpers