"""athena_app_cmdbApp URL Configuration

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

from django.urls import path
from . import views
from . import excel_upload_views


app_name = 'app-registry'
urlpatterns = [
    path('/', views.api_root, name='app-registry-home'),
    path('/load-from-excel', excel_upload_views.LoadFromExcel.as_view(), name='api-load-from-excel'),
    path('/bulk-update', views.athena_app_cmdbBulkUpdate.as_view(), name='api-bulk-update'),
    path('/<slug:objname>', views.athena_app_cmdbList.as_view(), name='athena_app_cmdb-list'),
    path('/<slug:objname>/detail', views.athena_app_cmdbListDetail.as_view(), name='athena_app_cmdb-list-detail'),
    path('/<slug:objname>/sync-update', views.athena_app_cmdbBulkSyncUpdate.as_view(), name='item-sync-update'),
    path('/<slug:objname>/<uuid:item>', views.athena_app_cmdbItem.as_view(), name='api-item'),
    path('/<slug:objname>/<uuid:item>/detail', views.athena_app_cmdbItemDetail.as_view(), name='api-item-detail'),
    path('/<slug:parentobjname>/<uuid:parent>/associations',
         views.athena_app_cmdbAssociationsList.as_view(), name='athena_app_cmdb-associations-list'),
    path('/<slug:parentobjname>/<uuid:parent>/associations/<slug:childobjname>',
         views.athena_app_cmdbAssociationsChildList.as_view(), name='athena_app_cmdb-associations-child-list'),
    path('/<slug:parentobjname>/<uuid:parent>/associations/<slug:childobjname>/<uuid:child>',
         views.athena_app_cmdbAssociationsChildCreateDestroy.as_view(), name='athena_app_cmdb-associations-child-createdestroy'),

]
