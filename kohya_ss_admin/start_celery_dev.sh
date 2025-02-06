
set DJANGO_SETTINGS_MODULE=kohya_ss_admin.settings_prod && celery -A proj worker --loglevel=info
set DJANGO_SETTINGS_MODULE=kohya_ss_admin.settings && celery -A proj worker --loglevel=info
set DJANGO_SETTINGS_MODULE=kohya_ss_admin.settings
celery.exe -A kohya_ss_admin worker -l info  -P eventlet

(base) (venv) PS E:\devspace\kohya_ss_admin> set DJANGO_SETTINGS_MODULE=kohya_ss_admin.settings
(base) (venv) PS E:\devspace\kohya_ss_admin> celery.exe -A kohya_ss_admin worker -l info  -P eventlet

