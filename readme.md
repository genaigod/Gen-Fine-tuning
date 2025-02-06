# Gen-Fine-tuning Platform

## Introduction
This is a task management platform designed for Kohya_SS LoRA training. It supports API-based LoRA training task submission, progress tracking, and copying trained LoRA models to Stable Diffusion.

---

## Table of Contents
1. [Deployment](#deployment)
2. [REST Framework Web Error](#rest-framework-web-error)
3. [Q&A](#qa)
   - [Demjson 2.2.4 Error](#demjson-224-error)
   - [Collect Static Files](#collect-static-files)
   - [MySQL Client Installation](#mysql-client-installation)
4. [Initialize and Create Superuser](#initialize-and-create-superuser)
5. [Project Manager](#project-manager)
6. [Kohya_SS Source Code Replacement](#kohya_ss-source-code-replacement)

---

## Deployment
Deploy the project to `/root`.

## REST Framework Web Error
If you encounter the following CSRF error in your REST framework:
```bash
ajax: {"detail":"CSRF Failed: CSRF token missing or incorrect."}

```
Update your settings.py with the following configuration:

```bash
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}
```

## Q&A
### Demjson 2.2.4 Error

To resolve the demjson 2.2.4 error, upgrade setuptools:
```bash
pip install --upgrade setuptools==57.5.0
```

### Collect Static Files
Run the following command to collect static files:
```bash
python manage.py collectstatic
```
Ensure your database is created with the correct character set:

```bash
CREATE DATABASE mydatabase CHARACTER SET utf8mb4;
```
### MySQL Client Installation
Install the MySQL client based on your operating system:

```bash
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

### Initialize and Create Superuser
Set user information in kohya_ss_admin/views.py:64, then run the following commands:

```bash
python manage.py makemigrations --settings=kohya_ss_admin.settings api_auth
python manage.py makemigrations --settings=kohya_ss_admin.settings kohya_ss
python manage.py makemigrations --settings=kohya_ss_admin.settings
python manage.py migrate --settings=kohya_ss_admin.settings api_auth
python manage.py migrate --settings=kohya_ss_admin.settings kohya_ss
python manage.py migrate --settings=kohya_ss_admin.settings
python manage.py createsuperuser --settings=kohya_ss_admin.settings
```

## Kohya_SS Source Code Replacement
Replace the following files in the Kohya_SS source code:

### Kohya_SS Commit Version
```bash
(/root/kohya_ss)$ git log -1

commit e5e8be05fe0475a04e61ef668afffc632aa178f5 (HEAD -> master, tag: v24.1.7, origin/master, origin/HEAD)
Author: bmaltais <bernard@ducourier.com>
Date:   Fri Sep 6 07:01:09 2024 -0400

    Update gradio to 4.43.0 to fix issue with fastapi latest release
```

### Files to Replace
```bash
[kohya_ss_source_code_change_file/blip_caption_gui.py] -> kohya_ss/kohya_gui/blip_caption_gui.py
[kohya_ss_source_code_change_file/lora_gui.py] -> kohya_ss/kohya_gui/lora_gui.py
[kohya_ss_source_code_change_file/train_network.py] -> kohya_ss/sd-scripts/train_network.py
```