from modeltranslation.translator import translator

from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.entity.section import Section

__author__ = 'Tareq'

translator.register(Section, Section.get_translator_options())
translator.register(Question, Question.get_translator_options())
translator.register(Answer, Answer.get_translator_options())
