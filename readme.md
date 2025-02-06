# 0 deploy /root

# 1  rest frame web error
```python

ajax：         {"detail":"CSRF Failed: CSRF token missing or incorrect."}


setting.py:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

```


# 2 Q&A
## 2.1
demjson 2.2.4 error
```bash
pip install --upgrade setuptools==57.5.0
```

## 2.2
python manage.py collectstatic
```bash
CREATE DATABASE mydatabase CHARACTER SET utf8mb4;
```
## 2.3
```bash
pacman -S python-mysqlclient

CentOS

yum install mysql-devel -y
yum install python-devel -y
pip install mysqlclient -y

Ubuntu

apt-get install libmysql-dev
apt-get install libmysqlclient-dev
apt-get install python3-dev
pip install mysqlclient
```



# 3 init and create superuser

> set userinfo kohya_ss_admin/views.py:64 


```bash
python manage.py makemigrations --settings=kohya_ss_admin.settings api_auth
python manage.py makemigrations --settings=kohya_ss_admin.settings kohya_ss
python manage.py makemigrations --settings=kohya_ss_admin.settings
python manage.py migrate --settings=kohya_ss_admin.settings api_auth
python manage.py migrate --settings=kohya_ss_admin.settings kohya_ss
python manage.py migrate --settings=kohya_ss_admin.settings
python manage.py createsuperuser --settings=kohya_ss_admin.settings
```

# 4 proj manager

```bash
supervisord -c  supervisord/supervisord.prod.conf
```

# 5 kohya_ss source code replace
> replace 3 files
>

kohya_ss commit version
```bash
(/root/kohya_ss)$ git log -1

commit e5e8be05fe0475a04e61ef668afffc632aa178f5 (HEAD -> master, tag: v24.1.7, origin/master, origin/HEAD)
Author: bmaltais <bernard@ducourier.com>
Date:   Fri Sep 6 07:01:09 2024 -0400

    Update gradio to 4.43.0 to fix issue with fastapi latest release

```

readme
```bash
[kohya_ss_source_code_change_file/blip_caption_gui.py] replace kohya_ss\kohya_gui\blip_caption_gui.py
[kohya_ss_source_code_change_file/lora_gui.py replace kohya_ss\kohya_gui\lora_gui.py
[kohya_ss_source_code_change_file/train_network.py] replace kohya_ss\sd-scripts\train_network.py
```