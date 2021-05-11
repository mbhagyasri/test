"""App RegistryApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from athena_app_cmdb.ui.forms import BootstrapAuthenticationForm
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # pull in /api
    path('api', include('athena_app_cmdb.urls', namespace='app-registry-api',)),
    path('api/token/create', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/login/', auth_views.LoginView.as_view(
        template_name='login.html', authentication_form=BootstrapAuthenticationForm,
        extra_context={'message': ''}, ), name='login'),
    path('admin/', admin.site.urls, name='admin'),
    path('', include('athena_app_cmdb.ui.urls', namespace='app-registry', )),
    path('/', include('athena_app_cmdb.ui.urls', namespace='app-registry', )),


]

admin.site.login_form = BootstrapAuthenticationForm
