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
from athena_app_cmdb import views as api_views
from athena_app_cmdb import excel_upload_views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.contrib.auth import views as auth_views

app_name = 'app-registry'

urlpatterns = [
    path('', include('athena_app_cmdb.ui.urls')),
    path('/', include('athena_app_cmdb.ui.urls')),
    path('token/create', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('monitor', api_views.monitor, name='monitor'),
    path('admin/login/', auth_views.LoginView.as_view(
        template_name='login.html', authentication_form=BootstrapAuthenticationForm,
        extra_context={'message': ''}, ), name='login'),
    path('admin/', admin.site.urls, name='admin'),
    path('load-from-excel', excel_upload_views.LoadFromExcel.as_view(), name='api-load-from-excel'),
    path('bulk-update', api_views.athena_app_cmdbBulkUpdate.as_view(), name='api-bulk-update'),
    path('<slug:objname>', api_views.athena_app_cmdbList.as_view(), name='athena_app_cmdb-list'),
    path('<slug:objname>/detail', api_views.athena_app_cmdbListDetail.as_view(), name='athena_app_cmdb-list-detail'),
    path('<slug:objname>/sync-update', api_views.athena_app_cmdbBulkSyncUpdate.as_view(), name='item-sync-update'),
    path('<slug:objname>/<slug:item>', api_views.athena_app_cmdbItem.as_view(), name='api-item'),
    path('<slug:objname>/<uuid:item>/detail', api_views.athena_app_cmdbItemDetail.as_view(), name='api-item-detail'),
    path('<slug:parentobjname>/<uuid:parent>/associations',
         api_views.athena_app_cmdbAssociationsList.as_view(), name='athena_app_cmdb-associations-list'),
    path('<slug:parentobjname>/<uuid:parent>/associations/<slug:childobjname>',
         api_views.athena_app_cmdbAssociationsChildList.as_view(), name='athena_app_cmdb-associations-child-list'),
    path('<slug:parentobjname>/<uuid:parent>/associations/<slug:childobjname>/<uuid:child>',
         api_views.athena_app_cmdbAssociationsChildCreateDestroy.as_view(),
         name='athena_app_cmdb-associations-child-createdestroy'),
]

admin.site.login_form = BootstrapAuthenticationForm
