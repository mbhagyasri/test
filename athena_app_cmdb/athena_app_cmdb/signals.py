# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import logging
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed
from .utils.helper_methods import trigger_apsink, trigger_external_secrets_plan
from .utils.helper_methods import trigger_resource_plan
from .models import Resource, Asset

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete, m2m_changed], dispatch_uid='apsink')
def call_app_sink(sender, **kwargs):
    """
    Trigger app-registry-sink Bamboo build after PRODUCTION asset definition update.
    app-registry-sink triggers the Platform Orchestration builds
    :param sender:
    :param kwargs:
    :return:
    """
    trigger_apsink()



@receiver([m2m_changed], sender=Asset, dispatch_uid='attachments')
@receiver([m2m_changed], sender=Resource, dispatch_uid='attachments')
def call_external_secrets(sender, **kwargs):
    """
    Trigger platform-resources external-secret bamboo plan after asset attachement update.
    :param sender:
    :param kwargs:
    :return:
    """
    trigger_external_secrets_plan()


@receiver([post_save, post_delete], sender=Resource, dispatch_uid='resources')
def call_resource_manager(sender, **kwargs):
    """
    Trigger platform-resources env-manager bamboo plan after resource definition update
    :param sender:
    :param kwargs:
    :return:
    """
    trigger_resource_plan()

