import logging
import traceback

from rest_framework import views
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, LoginSerializer
from apps.api_auth.authorizations import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

User = get_user_model()
logger = logging.getLogger('log_error')

class UserView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(data={"data": serializer.data, "code": 20000, "message": "get userinfo successfully"})
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={"data": {}, "code": 20002, "message": str(e)})


    def put(self,request):
        try:
            user = request.user
            user.username = request.data.get('username')
            user.telephone = request.data.get('telephone')
            user.email = request.data.get('email')
            user.headimgurl = request.data.get('avatar')
            user.save()
            serializer = UserSerializer(user)
            return Response(data={"data": serializer.data, "code": 20000, "message": "update userinof successfully"})
        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={"data": {}, "code": 20002, "message": str(e)})


