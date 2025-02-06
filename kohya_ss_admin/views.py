import json
import logging
import traceback

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from rest_framework import views, status
from rest_framework.response import Response
from apps.api_auth.authorizations import generate_jwt
from apps.api_auth.models import ApiUser
from apps.api_auth.serializers import UserSerializer
from lib.Utils import Utils

logger = logging.getLogger('log_error')


class IndexView(views.APIView):
    def get(self, request):
        try:

            from hashlib import sha1
            from django.http import HttpResponse

            iframe_content = """
           <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title></title>
                <meta keywords="">
                <meta description="ai plat kohya_ss admin。">
                <meta name='viewport' content='width=device-width,initial-scale=1,minimum-scale=1,maximum-scale=1,user-scalable=no'/>
            </head>
            <body>
                <style>
                </style>
                <div id="app">
                   
                </div>
            </body>
            </html>
            """

            return HttpResponse(iframe_content, content_type='text/html')

            # return HttpResponse("<img src='https://api.btstu.cn/sjbz/api.php?lx=suiji&format=images&method=zsy' />")

        except Exception as e:
            # print(str(traceback.format_exc()))
            return Response(data={"data": {}, "code": 20002, "message": str(e)})



class SdDdRedirectUrlView(views.APIView):
    def post(self, request):
        try:
            attrs = request.data
            username = 'x'
            open_id = 'xx'
            """
            # sig= md5($USER$PNmd5($YEAR$M$D$secret)) 
                eg: 
                    v1= "20231110"+"714b9c04e3d8a1fc65bb721fde81a31d" 
                    md5(v1)  md5(20231120714b9c04e3d8a1fc65bb721fde81a31d) = 373b679c50b6ce8b8aa5b6e3ca1e5a1a
                    v2 = "ljz" + "xxxx" + v1  
                    sig = md5(v2)  md5(ljzxxxx373b679c50b6ce8b8aa5b6e3ca1e5a1a) = 77547c0d070cf24fc5779614a5f2f1bd
            """
            sig = attrs.get("sig")
            if username is None or open_id is None:
                raise Exception("username or nid not in request param")
            real_sig = Utils.get_signature(username+open_id, '714b9c04e3d8a1fc65bb721fde81a31d')
            if sig != real_sig:
                raise Exception(f"user:{username} pn:{open_id} sig:{sig} is error")
            user_dict_data = {
                "username": username,
                "openid": open_id,
                "unionid": open_id,
                "privilege": "",
                "nickname": username
            }
            act = "get token"
            try:
                user = ApiUser.objects.get(openid=open_id, unionid=open_id)
            except:
                print(traceback.format_exc())
                user_dict_data['privilege'] = ','.join(user_dict_data['privilege'])
                user = ApiUser.objects.create(**user_dict_data)
                user.save()
                act = "get token"
            token = generate_jwt(user)
            user_serializer = UserSerializer(user)
            data = {"token": token, "user": user_serializer.data}
            return Response(data={"data": data, "code": 20000, "message": f"{act} success"})
        except Exception as e:
            logger.error(traceback.format_exc())
            print(str(traceback.format_exc()))
            return Response(data={"data": {}, "code": 20002, "message": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

