import datetime
import os
import sys
import time
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kohya_ss_admin.settings')

from django.conf import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def cron_reset_pending_working_tasks():
    import django

    django.setup()

    from apps.kohya_ss.models import AsyncTask

    # tasks = AsyncTask.objects.get(status="PENDING")
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta
    # 获取当前时间
    current_time = timezone.now()

    three_hours_ago = current_time - timedelta(minutes=60*6)
    tasks = AsyncTask.objects.filter(Q(status='PENDING') | Q(status='TRAINING'),
                                     created_at__lte=three_hours_ago)
    if tasks:
        print(tasks)
        for item in tasks:
            # tp = TaskParamsSerializer(item)
            print(1111, item)
            item.status = 'FAILED'
            item.save()
    else:
        print(tasks)

    from gradio_client import Client
    client = Client(settings.KOHYA_SS_CONF["url"])
    ret = client.predict(api_name="/is_train_lora")
    if ret:
        return

if __name__ == '__main__':

    while 1:
        try:
            print(datetime.datetime.now())
            cron_reset_pending_working_tasks()
            time.sleep(600)
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(600)