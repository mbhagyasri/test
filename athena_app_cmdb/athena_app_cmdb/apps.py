from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class athena_app_cmdbConfig(AppConfig):
    name = 'athena_app_cmdb'
    verbose_name = _('App Registry')


    def ready(self):
        import athena_app_cmdb.signals