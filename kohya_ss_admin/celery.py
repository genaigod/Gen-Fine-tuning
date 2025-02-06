import os

from celery import Celery

proj = 'kohya_ss_admin'
is_prod = os.environ.get("my_env")
# setting_env = "settings" #
"""
$ export my_env=dev; celery.exe -A ai_draw_plat_v1 worker -l info
"""
setting_env = "settings" if is_prod == 'prod' else "settings"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{proj}.{setting_env}')

app = Celery(f'{proj}')

app.config_from_object(f'{proj}.{setting_env}', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')