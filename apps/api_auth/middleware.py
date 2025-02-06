from django.conf import settings
from django.shortcuts import redirect
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import APIException

from rest_framework.response import Response
from rest_framework import status

from rest_framework import exceptions



# from loguru import logger
#
# logger.add("django.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="100 MB", filter="",
#            level="DEBUG", encoding='utf-8')
import logging
logger = logging.getLogger('log_info')
class RedirectIfNotAuthenticatedMiddleware:
    keyword = 'JWT'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"middleware: {request.method} {request.path} {request.get_full_path()} "
                    f"get_args:{request.GET} post_args or file:{request.POST if not request.FILES else request.FILES}  "
                    f"request.body:{request.body}"
                    f"ENV:{request.META.get('ENV','')} "
                    f"REMOTE_ADDR:{request.META.get('REMOTE_ADDR','')} "
                    f"HTTP_HOST:{request.META.get('HTTP_HOST','')} "
                    f"SERVER_PORT:{request.META.get('SERVER_PORT','')} "
                    f"HTTP_ACCEPT_ENCODING:{request.META.get('HTTP_ACCEPT_ENCODING','')} "
                    f"HTTP_AUTHORIZATION:{request.META.get('HTTP_AUTHORIZATION','')} "
                    )

        response = self.get_response(request)
        if hasattr(response, 'content'):
            try:
                content = response.content.decode('utf-8')[:300]
                if not str(content).__contains__("""<!doctype html>"""):
                    logger.info(f"response：{response} content:{content}")
            except Exception as e:
                logger.error(f"response：{response} content error:{str(e)}")

        return response



