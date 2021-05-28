"""
Definition of views.
"""

import os
import yaml
import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import RegistrationForm
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import redirect


logger = logging.getLogger(__name__)


IGNORE_FILTERS = ['page_size', 'page']


def redirect_admin(request, format=None):
    response = redirect('/admin/')
    return response

class Home(LoginRequiredMixin, TemplateView):
    """Renders the home page."""
    template_name = 'index.html'


class Register(FormView):
    template_name = 'register.html'
    form_class = RegistrationForm

    def get_success_url(self):
        # pull next if available to reroute to login and append next to it
        next_page = self.kwargs.get('next', '/')
        return '/admin/login/?next={}'.format(next_page)

    def form_valid(self, form):
        form.save()
        u = User.objects.get(username=form.instance)
        u.set_password(form.instance.password)
        u.save()
        return super(Register, self).form_valid(form)

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        next_page = kwargs.get('next', '/')
        kwargs['next'] = next_page
        return super().get_context_data(**kwargs)


class Contact(TemplateView):
    """Renders the contact page."""
    template_name = 'contact.html'


class About(TemplateView):
    """Renders the about page."""
    template_name = 'contact.html'


class Swagger(TemplateView):
    template_name = 'swagger.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        filename = os.path.join(__location__, "openapi.yaml")
        try:
            with open(filename) as f:
                content = yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to read file %s" % filename)
            logger.exception(e)
            errorMessage = 'Failed to load swagger doc.'
            context['errorMessage'] = errorMessage
            return context
        swagger_content = json.dumps(content)
        context['swagger_content'] = swagger_content
        return context


class SwaggerAuth(TemplateView):
    template_name = 'swagger.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        filename = os.path.join(__location__, "openapi_auth.yaml")
        try:
            with open(filename) as f:
                content = yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to read file %s" % filename)
            logger.exception(e)
            errorMessage = 'Failed to load swagger doc.'
            context['errorMessage'] = errorMessage
            return context
        swagger_content = json.dumps(content)
        context['swagger_content'] = swagger_content
        return context
