import json
import random

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from apps.api_auth.models import ApiUser
from lib.Utils import Utils


# Create your models here.
class AsyncTask(models.Model):
    task_id = models.CharField(max_length=100, verbose_name='task_id')
    status = models.CharField(max_length=100, default='PENDING', verbose_name='任务状态')
    op_type = models.IntegerField(default=0, verbose_name='op_type', blank=True, null=True)
    lora_url = models.TextField(default='', verbose_name='lora_url', blank=True, null=True)
    task_params = models.TextField(default='', verbose_name='task_params', blank=True, null=True)
    ret = models.TextField(default='', verbose_name='ret', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='created_at')
    completed_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='completed_at')


    def __str__(self):
        return f"AsyncTask: {self.task_id}"

    class Meta:
        verbose_name = "Kohya_SS task"
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)
