# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import shlex
import logging
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q
from athena_app_cmdb import models


logger = logging.getLogger(__name__)


# generic input filter class
class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class DRProtectedStatusFilter(admin.SimpleListFilter):
    title = _('DR Protected Status')
    parameter_name = 'drservices_status'

    def lookups(self, request, model_admin):
        return (
            ('operational', 'operational'),
            ('in progress', 'in progress'),
            ('failover', 'failover'),
            ('failback', 'failback')
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            return queryset.filter(properties__managed_options__disaster_recovery_services__status=value)
        return queryset


class DRProtectedFilter(admin.SimpleListFilter):
    title = _('DR Protected')
    parameter_name = 'drservices_active'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(properties__managed_options__disaster_recovery_services__active=True)
        elif value == 'No':
            return queryset.exclude(properties__managed_options__disaster_recovery_services__active=True)
        return queryset


class ManagementOrCustomerResourceFilter(admin.SimpleListFilter):
    title = _('Management Type')
    parameter_name = 'msvx_management'

    def lookups(self, request, model_admin):
        return (
            ('customer', 'Customer'),
            ('management', 'MSVx management')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "customer":
            return queryset.exclude(properties__roles__contains='management')
        elif value == 'management':
            return queryset.filter(properties__roles__contains='management')
        return queryset


class SupportingOSFilter(InputFilter):
    parameter_name = "supporting_os"
    title = _('Supporting OS')

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return
        any_name = Q()
        for bit in shlex.split(value):
            any_name |= (
                Q(properties__supporting_os__icontains=bit)
            )
        logger.info(any_name)
        return queryset.filter(any_name)


class DRProtectionGroupFilter(InputFilter):
    title = _('Protection Group')
    parameter_name = 'protection_group'

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return
        any_name = Q()
        for bit in shlex.split(value):
            any_name |= (
                Q(properties__managed_options__disaster_recover_services__protection_group=bit)
            )
        logger.info(any_name)
        return queryset.filter(any_name)


class DrProtectionGroupFilter(admin.SimpleListFilter):
    title = _('Protection Group')
    parameter_name = 'protection_group'

    def lookups(self, request, model_admin):
        pg = set([c.name for c in models.protection_group.objects.all()])
        return [(c.name, c.name) for c in pg]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(properties__managed_options__disaster_recover_services__protection_group=value)
        return queryset
