global = if window? then window else process

define 'cs!xlform/model.row', [
        'underscore',
        'backbone',
        'cs!xlform/model.base',
        'cs!xlform/model.configs',
        'cs!xlform/model.utils',
        'cs!xlform/model.surveyDetail',
        'cs!xlform/model.aliases',
        'cs!xlform/model.rowDetail',
        'cs!xlform/model.choices',
        'cs!xlform/mv.skipLogicHelpers',
        ], (
            _,
            Backbone,
            base,
            $configs,
            $utils,
            $surveyDetail,
            $aliases,
            $rowDetail,
            $choices,
            $skipLogicHelpers,
            )->

  row = {}

  class row.BaseRow extends base.BaseModel
    @kls = "BaseRow"
    constructor: (attributes={}, options={})->
      for key, val of attributes when key is ""
        delete attributes[key]
      super(attributes, options)

    initialize: ->
      @convertAttributesToRowDetails()

    isError: -> false
    convertAttributesToRowDetails: ->
      for key, val of @attributes
        unless val instanceof $rowDetail.RowDetail
          @set key, new $rowDetail.RowDetail({key: key, value: val}, {_parent: @}), {silent: true}
    attributesArray: ()->
      arr = ([k, v] for k, v of @attributes)
      arr.sort (a,b)-> if a[1]._order < b[1]._order then -1 else 1
      arr
    isInGroup: ->
      @_parent?._parent?.constructor.kls is "Group"

    detach: (opts)->
      if @_parent
        @_parent.remove @, opts
        @_parent = null
      ` `

    selectableRows: () ->
      questions = []
      limit = false

      non_selectable = ['datetime', 'time', 'note', 'calculate', 'group']

      survey = @getSurvey()
      if survey == null
        return null
      survey.forEachRow (question) =>
        limit = limit || question is @
        if !limit && question.getValue('type') not in non_selectable
          questions.push question
      , includeGroups:true
      questions

    export_relevant_values: (survey_arr, additionalSheets)->
      survey_arr.push(@toJSON2())

    toJSON2: ->
      outObj = {}
      for [key, val] in @attributesArray()
        if key is 'type' and val.get('typeId') in ['select_one', 'select_multiple', 'free_choice_field']
          result = {}
          result[val.get('typeId')] = val.get('listName')
        else
          result = @getValue(key)
        unless @hidden
          if _.isBoolean(result)
            outObj[key] = $configs.boolOutputs[if result then "true" else "false"]
          else if '' isnt result
            outObj[key] = result
      outObj

    toJSON: ->
      outObj = {}
      for [key, val] in @attributesArray()
        result = @getValue(key)
        unless @hidden
          if _.isBoolean(result)
            outObj[key] = $configs.boolOutputs[if result then "true" else "false"]
          else
            outObj[key] = result
      outObj

  class SimpleRow extends Backbone.Model
    finalize: -> ``
    getTypeId: -> @get('type')
    linkUp: ->
    _isSelectQuestion: ()-> false
    get_type: ->
      $skipLogicHelpers.question_types[@getTypeId()] || $skipLogicHelpers.question_types['default']
    getValue: (which)-> @get(which)

  class RankRow extends SimpleRow
    initialize: ->
      @set('type', 'rank__level')
    export_relevant_values: (surv, sheets)->
      surv.push @attributes

  class ScoreRankMixin
    _extendAll: (rr)->
      extend_to_row = (val, key)=>
        if _.isFunction(val)
          rr[key] = (args...)->
            val.apply(rr, args)
        else
          rr[key] = val
      _.each @, extend_to_row
      extend_to_row(@forEachRow, 'forEachRow')

      rr._afterIterator = (cb, ctxt)->
        obj =
          export_relevant_values: (surv, addl)->
            surv.push(type: "end #{rr._beginEndKey()}")
          toJSON: ()->
            type: "end #{rr._beginEndKey()}"
        cb(obj)  if ctxt.includeGroupEnds

      _toJSON = rr.toJSON

      rr.clone = ()->
        attributes = rr.toJSON2()

        options =
          _parent: rr._parent
          add: false
          merge: false
          remove: false
          silent: true

        r2 = new row.Row(attributes, options)
        r2._isCloned = true
  
        if rr._rankRows
          # if rr is a rank question
          for rankRow in rr._rankRows.models
            r2._rankRows.add(rankRow.toJSON())
          r2._rankLevels = rr.getSurvey().choices.add(name: $utils.txtid())
          for item in rr.getList().options.models
            r2._rankLevels.options.add(item.toJSON())
          r2.set('kobo--rank-items', r2._rankLevels.get('name'))
          @convertAttributesToRowDetails()
          r2.get('type').set('list', r2._rankLevels)
        else
          # if rr is a score question
          for scoreRow in rr._scoreRows.models
            r2._scoreRows.add(scoreRow.toJSON())
          r2._scoreChoices = rr.getSurvey().choices.add(name: $utils.txtid())
          for item in rr.getList().options.models
            r2._scoreChoices.options.add(item.toJSON())
          r2.set('kobo--score-choices', r2._scoreChoices.get('name'))
          @convertAttributesToRowDetails()
          r2.get('type').set('list', r2._scoreChoices)
        r2

      rr.toJSON = ()->
        out = _toJSON.call(rr)
        out.type = "begin #{rr._beginEndKey()}"
        if typeof @_additionalJson is 'function'
          _.extend(out, @_additionalJson())
        out

      _.each @constructor.prototype, extend_to_row
      if rr.attributes.__rows
        for subrow in rr.attributes.__rows
          @[@_rowAttributeName].add(subrow)
        delete rr.attributes.__rows

    getValue: (which)->
      @get(which)

    forEachRow: (cb, ctx)->
      cb(@)
      @[@_rowAttributeName].each (subrow)-> cb(subrow)
      @_afterIterator(cb, ctx)  if '_afterIterator' of @


  class RankRows extends Backbone.Collection
    model: RankRow

  class RankMixin extends ScoreRankMixin
    constructor: (rr)->
      @_rankRows = new RankRows()
      @_rowAttributeName = '_rankRows'
      @_extendAll(rr)
      rankConstraintMessageKey = 'kobo--rank-constraint-message'
      if !rr.get(rankConstraintMessageKey)
        rr.set(rankConstraintMessageKey, 'Items cannot be selected more than once')

    _beginEndKey: ->
      'rank'

    linkUp: (ctx)->
      rank_list_id = @get('kobo--rank-items')?.get('value')
      if rank_list_id
        @_rankLevels = @getSurvey().choices.get(rank_list_id)
      else
        @_rankLevels = @getSurvey().choices.create()
      @_additionalJson = =>
        'kobo--rank-items': @getList().get('name')
      @getList = => @_rankLevels

    export_relevant_values: (survey_arr, additionalSheets)->
      if @_rankLevels
        additionalSheets['choices'].add(@_rankLevels)
      begin_xlsformrow = _.clone(@toJSON2())
      begin_xlsformrow.type = "begin rank"
      survey_arr.push(begin_xlsformrow)
      ``

  class ScoreChoiceList extends Array

  class ScoreRow extends SimpleRow
    initialize: ->
      @set('type', 'score__row')
    export_relevant_values: (surv, sheets)->
      surv.push(@attributes)

  class ScoreRows extends Backbone.Collection
    model: ScoreRow

  class ScoreMixin extends ScoreRankMixin
    constructor: (rr)->
      @_scoreRows = new ScoreRows()
      @_rowAttributeName = '_scoreRows'
      @_extendAll(rr)

    _beginEndKey: ->
      'score'

    linkUp: (ctx)->
      @getList = ()=> @_scoreChoices
      @_additionalJson = ()=>
        'kobo--score-choices': @getList().get('name')
      score_list_id_item = @get('kobo--score-choices')
      if score_list_id_item
        score_list_id = score_list_id_item.get('value')
        if score_list_id
          @_scoreChoices = @getSurvey().choices.get(score_list_id)
        else
          ctx.warnings.push "Score choices list not found"
          @_scoreChoices = @getSurvey().choices.add({})
      else
        ctx.warnings.push "Score choices list not set"
        @_scoreChoices = @getSurvey().choices.add(name: $utils.txtid())
      ``

    export_relevant_values: (survey_arr, additionalSheets)->
      score_list = @_scoreChoices
      if score_list
        additionalSheets['choices'].add(score_list)
      output = _.clone(@toJSON2())
      output.type = "begin score"
      output['kobo--score-choices'] = @getList().get('name')
      survey_arr.push(output)
      ``

  class row.Row extends row.BaseRow
    @kls = "Row"
    initialize: ->
      ###
      The best way to understand the @details collection is
      that it is a list of cells of the XLSForm spreadsheet.
      The column name is the "key" and the value is the "value".
      We opted for a collection (rather than just saving in the attributes of
      this model) because of the various state-related attributes
      that need to be saved for each cell and this allows more room to grow.

      E.g.: {"key": "type", "value": "select_one colors"}
            needs to keep track of how the value was built
      ###
      if @_parent
        defaultsUnlessDefined = @_parent.newRowDetails || $configs.newRowDetails
        defaultsForType = @_parent.defaultsForType || $configs.defaultsForType
      else
        console?.error "Row not linked to parent survey."
        defaultsUnlessDefined = $configs.newRowDetails
        defaultsForType = $configs.defaultsForType

      if @attributes.type and @attributes.type of defaultsForType
        curTypeDefaults = defaultsForType[@attributes.type]
      else
        curTypeDefaults = {}

      defaults = _.extend {}, defaultsUnlessDefined, curTypeDefaults

      for key, vals of defaults
        unless key of @attributes
          newVals = {}
          for vk, vv of vals
            newVals[vk] = if ("function" is typeof vv) then vv() else vv
          @set key, newVals


      if @attributes.type is 'score'
        new ScoreMixin(@)
      else if @attributes.type is 'rank'
        new RankMixin(@)

      @convertAttributesToRowDetails()


      typeDetail = @get("type")
      tpVal = typeDetail.get("value")
      processType = (rd, newType, ctxt)=>
        # if value changes, it could be set from an initialization value
        # or it could be changed elsewhere.
        # we need to keep typeId, listName, and orOther in sync.
        [tpid, p2, p3] = newType.split(" ")
        typeDetail.set("typeId", tpid, silent: true)
        if p2
          typeDetail.set("listName", p2, silent: true)
          matchedList = @getSurvey().choices.get(p2)
          if matchedList
            typeDetail.set("list", matchedList)
        typeDetail.set("orOther", p3, silent: true)  if p3 is "or_other"
        if (rtp = $configs.lookupRowType(tpid))
          typeDetail.set("rowType", rtp, silent: true)
        else
          throw new Error "type `#{tpid}` not found"
      processType(typeDetail, tpVal, {})
      typeDetail.on "change:value", processType
      typeDetail.on "change:listName", (rd, listName, ctx)->
        rtp = typeDetail.get("rowType")
        typeStr = "#{typeDetail.get("typeId")}"
        if rtp.specifyChoice and listName
          typeStr += " #{listName}"
        if rtp.orOtherOption and typeDetail.get("orOther")
          typeStr += " or_other"
        typeDetail.set({value: typeStr}, silent: true)
      typeDetail.on "change:list", (rd, cl, ctx)->
        if typeDetail.get("rowType").specifyChoice
          clname = cl.get("name")
          unless clname
            clname = $utils.txtid()
            cl.set("name", clname, silent: true)
          @set("value", "#{@get('typeId')} #{clname}")
    getTypeId: ->
      @get('type').get('typeId')
    clone: ->
      attributes = {}
      options =
        _parent: @_parent
        add: false
        merge: false
        remove: false
        silent: true


      _.each @attributes, (value, key) => attributes[key] = @getValue key

      newRow = new row.Row attributes, options

      newRowType = newRow.get('type')
      if newRowType.get('typeId') in ['select_one', 'select_multiple', 'free_choice_field']
        newRowType.set 'list', @getList().clone()
        newRowType.set 'listName', newRowType.get('list').get 'name'

      return newRow

    finalize: ->
      existing_name = @getValue("name")
      unless existing_name
        names = []
        @getSurvey().forEachRow (r)->
          name = r.getValue("name")
          names.push(name)  if name
        label = @getValue("label")
        @get("name").set("value", $utils.sluggifyLabel(label, names))
      @

    get_type: ->
      $skipLogicHelpers.question_types[@getTypeId()] || $skipLogicHelpers.question_types['default']

    _isSelectQuestion: ->
      # TODO [ald]: pull this from $aliases
      @get('type').get('typeId') in ['select_one', 'select_multiple', 'free_choice_field']

    getList: ->
      _list = @get('type')?.get('list')
      if (not _list) and @_isSelectQuestion()
        _list = new $choices.ChoiceList(name: $utils.txtid())
        @setList(_list)
      _list

    setList: (list)->
      listToSet = @getSurvey().choices.get(list)
      unless listToSet
        @getSurvey().choices.add(list)
        listToSet = @getSurvey().choices.get(list)
      throw new Error("List not found: #{list}")  unless listToSet
      @get("type").set("list", listToSet)
    parse: ->
      val.parse()  for key, val of @attributes

    linkUp: (ctx)->
      val.linkUp(ctx)  for key, val of @attributes

  class row.RowError extends row.BaseRow
    constructor: (obj, options)->
      @_error = options.error
      unless global.xlfHideWarnings
        console?.error("Error creating row: [#{options.error}]", obj)
      super(obj, options)
    isError: -> true
    getValue: (what)->
      if what of @attributes
        @attributes[what].get('value')
      else
        "[error]"

  row
