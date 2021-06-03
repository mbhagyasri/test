# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global.
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2019 =================================================
from __future__ import unicode_literals
import logging
from django.db import models
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class SoftDeleteQueryMixin(object):
    def delete(self):
        for model_instance in self.all():
            model_instance.delete()

    def undelete(self):
        for model_instance in self.raw_all():
            model_instance.undelete()


class SoftDeleteQuerySet(SoftDeleteQueryMixin, QuerySet):
    pass


class SoftDeleteManager(SoftDeleteQueryMixin, models.Manager):

    def get_raw_queryset(self):
        return super(SoftDeleteManager, self).get_queryset() if self.model else None

    def get_queryset(self):
        if self.model:
            query_set = SoftDeleteQuerySet(self.model, using=self._db)
            return query_set.exclude(deleted=True)

    def get(self, *args, **kwargs):
        return self.get_raw_queryset().get(*args, **kwargs)

    def raw_all(self, *args, **kwargs):
        return self.get_raw_queryset().all(*args, **kwargs)
