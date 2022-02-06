__author__ = 'Tareq'


class ActiveInactiveModelMixin(object):
    def activate(self, *args, **kwargs):
        from blackwidow.core.models.log.activation_log import ActivationLog
        if not self.is_active:
            self.is_active = True
            self.save()
            try:
                name = self.code + ': ' + self.name
            except:
                name = self.code
            ActivationLog.log(model=self, name=name, action='Activate')

    def deactivate(self, *args, **kwargs):
        from blackwidow.core.models.log.activation_log import ActivationLog
        if self.is_active:
            self.is_active = False
            self.save()
            try:
                name = self.code + ': ' + self.name
            except:
                name = self.code
            ActivationLog.log(model=self, name=name, action='De-activate')
