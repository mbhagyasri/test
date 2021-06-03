# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

from __future__ import unicode_literals

import logging
from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager

logger = logging.getLogger(__name__)


_call = lambda inst, method: hasattr(inst, method) and getattr(inst, method)()


class SoftDeleteModel(models.Model):

    objects = SoftDeleteManager()
    raw_objects = models.Manager()

    deleted = models.BooleanField(db_column='deleted', default='f')

    class Meta(object):
        abstract = True

    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, *args, **kwargs):
        self.cascade_delete()

    def undelete(self):
        self.cascade_undelete()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.deleted = True
        current_time = timezone.now()
        if hasattr(self, 'deleted_at'):
            self.deleted_at = current_time
        if hasattr(self, 'deletedAt'):
            self.deletedAt = current_time
        self.save()

    def soft_undelete(self):
        self.deleted_at = None
        self.id = self.original_id
        self.original_id = None
        self.deleted = False
        self.save()

    def hard_delete(self):
        return super(SoftDeleteModel, self).delete()

    def cascade_delete(self):
        self.chain_action('delete')
        self.soft_delete()

    def cascade_undelete(self):
        self.chain_action('undelete')
        self.soft_undelete()

    def get_all_related_objects(self):
        return (
            f for f in self._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete
        )

    def chain_action(self, method_name):
        for relation in self.get_all_related_objects():
            accessor_name = relation.get_accessor_name()
            acessor = getattr(self, accessor_name, None)
            if acessor:
                if issubclass(acessor.__class__, (SoftDeleteModel, SoftDeleteManager,)):
                    _call(acessor, method_name)
