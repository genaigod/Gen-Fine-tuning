# coding:utf-8
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing
os.environ['DJANGO_SETTINGS_MODULE'] = 'kohya_ss_admin.settings'
workers = 4
threads = 8
bind = '0.0.0.0:8890'
daemon = 'false'
worker_class = 'gevent'
worker_connections = 2000
max_requests = 2000
accesslog = '/root/kohya_ss_admin/logs/kohya_ss_admin_access.log'
errorlog = '/root/kohya_ss_admin/logs/kohya_ss_admin_gunicorn_error.log'
loglevel = 'debug'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
backlog = 512
proc_name = 'kohya_ss_admin'
timeout = 120
graceful_timeout = 300
keepalive = 3
limit_request_line = 5120
limit_request_fields = 101
limit_request_field_size = 8190