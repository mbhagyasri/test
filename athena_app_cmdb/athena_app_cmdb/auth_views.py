# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2019 =================================================


import pydash
import json
import logging

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.backends import TokenBackend
from django.views.decorators.cache import never_cache

from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

from django.contrib.auth.models import User
from rest_framework import permissions


from libs.utility.config_parsers import get_config
from . import serializers

logger = logging.getLogger(__name__)
config = get_config()


@method_decorator(never_cache, name='dispatch')
class ExamplePermissionClass(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {
            'user': str(request.user),
            'message': 'User is authenticated'
        }
        return Response(content, status=200, content_type='application/json')


@method_decorator(never_cache, name='dispatch')
class UserListView(APIView):

    permission_classes = (permissions.AllowAny, )

    def get(self, request):
        decrypt_data = {}
        data = User.objects.all()
        obj_serializer = serializers.UserSerializer(data, many=True)
        decrypt_data = obj_serializer.data

        return Response({"Users": decrypt_data})

