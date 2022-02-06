__author__ = 'Sohel'
from django.db.models.signals import m2m_changed

from blackwidow.core.models.track_change.TrackModelM2MChangeModel import TrackModelM2MChangeModel

"""Sample Usage"""
"""
class Topping(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        db_table = 'topping'

class Pizza(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    toppings = models.ManyToManyField(Topping)

    class Meta:
        db_table = 'pizza'


TrackModelRelationChange.add_to_watch(Pizza.toppings) ###This is the line need to be added to watch the changes on ManyToManyField.

"""

class TrackModelRelationChange(object):

    def __init__(self, arg):
        pass

    @staticmethod
    def track_time_change(model_name):
        track_model_m2m_change_obj,created = TrackModelM2MChangeModel.objects.get_or_create(model_name=model_name)
        track_model_m2m_change_obj.save() ### Need to call save here because save method updates the modification time.

    @staticmethod
    def on_relation_state_change(sender,**kwargs):
        if "post" in kwargs["action"]:
            model_name = kwargs["instance"].__class__.__name__
            TrackModelRelationChange.track_time_change(model_name)

    @staticmethod
    def add_to_watch(manytomanyfield):
        m2m_changed.connect(TrackModelRelationChange.on_relation_state_change, sender=manytomanyfield.through)
