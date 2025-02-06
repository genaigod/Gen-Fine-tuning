import jwt
from datetime import timedelta, datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.authentication import BaseAuthentication,get_authorization_header
from rest_framework import exceptions
# from django.contrib.auth import get_user_model
from .models import ApiUser
# MTUser = get_user_model()

def generate_jwt(user):
    expire_time = datetime.now() + timedelta(days=7)
    return jwt.encode({"userid":user.pk, "exp": expire_time},key=settings.SECRET_KEY).decode('utf-8')

class JWTAuthentication(BaseAuthentication):
    keyword = 'JWT'
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            msg = "Authorization empty or not startswith jwt"
            raise exceptions.AuthenticationFailed({"data": [], "code": 20002, "message": f"{msg}"})

        if len(auth) == 1:
            msg = "JWT HEADER is invalid！"
            raise exceptions.AuthenticationFailed({"data": [], "code": 20002, "message": f"{msg}"})
        elif len(auth) > 2:
            msg = 'JWT HEADER is invalid！'
            raise exceptions.AuthenticationFailed({"data": [], "code": 20002, "message": f"{msg}"})

        try:
            jwt_token = auth[1]
            jwt_info = jwt.decode(jwt_token,settings.SECRET_KEY)
            userid = jwt_info.get('userid')
            print(36, userid)
            try:
                user = ApiUser.objects.get(pk=userid)
                request.user = user
                return user, jwt_token
            except Exception as e:
                msg = 'user does not exist！'
                raise exceptions.AuthenticationFailed({"data": [], "code": 20002, "message": f"{msg}:{e}"})

        except jwt.ExpiredSignatureError as e:
            msg = "JWT Token expired！"
            raise exceptions.AuthenticationFailed({"data": [], "code": 20002, "message": f"{msg}:{e}"})

        except Exception as e:
            raise exceptions.NotAuthenticated({"data": [], "code": 20002, "message": f"auth failed:{e}"})
