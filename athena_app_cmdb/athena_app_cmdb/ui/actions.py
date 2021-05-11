# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import pydash
from django.utils import timezone
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy


# Global MSVx soft delete action
def soft_delete_selected(modeladmin, request, queryset):

    """
    Default action which solf deletes the selected objects.
    This action first displays a confirmation page which shows all the
    deletable objects, or, if the user has no permission one of the related
    childs (foreignkeys), a "permission denied" message.
    Next, it deletes all selected objects and redirects back to the change list.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    deletable_objects, model_count, perms_needed, protected = modeladmin.get_deleted_objects(queryset, request)

    # The user has already confirmed the deletion.
    # Do the deletion and return None to display the change list view again.
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = str(obj)
                modeladmin.log_deletion(request, obj, obj_display)
                queryset.update(deleted_at=timezone.now(), deleted=1)
            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        # Return None to display the change list page again.
        return None

    objects_name = model_ngettext(queryset)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = {
        **modeladmin.admin_site.each_context(request),
        'title': title,
        'objects_name': str(objects_name),
        'deletable_objects': [deletable_objects],
        'model_count': dict(model_count).items(),
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'media': modeladmin.media,
    }

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(request, modeladmin.delete_selected_confirmation_template or [
        "admin/%s/%s/delete_selected_confirmation.html" % (app_label, opts.model_name),
        "admin/%s/delete_selected_confirmation.html" % app_label,
        "admin/delete_selected_confirmation.html"
    ], context)


def set_dr_status_failover(modeladmin, request, queryset):
    n = queryset.count()
    if n:
        for obj in queryset:
            properties = obj.properties
            obj.properties = pydash.objects.set_(properties, 'managed_options.disaster_recovery_services,status',
                                                 'failover')
        modeladmin.message_user(request, _("Successfully updated %(count)d %(items)s.") % {
            "count": n, "items": model_ngettext(modeladmin.opts, n)
        }, messages.SUCCESS)


def set_dr_status_failback(modeladmin, request, queryset):
    n = queryset.count()
    if n:
        for obj in queryset:
            properties = obj.properties
            obj.properties = pydash.objects.set_(properties, 'managed_options.disaster_recovery_services,status',
                                                 'failback')
        modeladmin.message_user(request, _("Successfully updated %(count)d %(items)s.") % {
            "count": n, "items": model_ngettext(modeladmin.opts, n)
        }, messages.SUCCESS)


def set_dr_status_operational(modeladmin, request, queryset):
    n = queryset.count()
    if n:
        for obj in queryset:
            properties = obj.properties
            obj.properties = pydash.objects.set_(properties, 'managed_options.disaster_recovery_services,status',
                                                 'operational')
        modeladmin.message_user(request, _("Successfully updated %(count)d %(items)s.") % {
            "count": n, "items": model_ngettext(modeladmin.opts, n)
        }, messages.SUCCESS)


def set_dr_status_in_progress(modeladmin, request, queryset):
    n = queryset.count()
    if n:
        for obj in queryset:
            properties = obj.properties
            obj.properties = pydash.objects.set_(properties, 'managed_options.disaster_recovery_services,status',
                                                 'in progress')
        modeladmin.message_user(request, _("Successfully updated %(count)d %(items)s.") % {
            "count": n, "items": model_ngettext(modeladmin.opts, n)
        }, messages.SUCCESS)
