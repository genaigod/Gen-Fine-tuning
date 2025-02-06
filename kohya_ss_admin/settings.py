import random
import os

os.environ["ENV"] = "prod"

from kohya_ss_admin.base import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'kohya_ss_admin.settings')

KOHYA_SS_CONF = {
    "url": "http://127.0.0.1:7866/",
    # "dirname": r"E:\devspace\kohya_ss",
    "dirname": r"/root/kohya_ss_admin"
}

print("启动环境是:", os.environ["ENV"])

