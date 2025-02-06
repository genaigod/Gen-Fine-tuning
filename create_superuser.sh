python manage.py makemigrations --settings=kohya_ss_admin.settings api_auth
python manage.py makemigrations --settings=kohya_ss_admin.settings kohya_ss
python manage.py makemigrations --settings=kohya_ss_admin.settings
python manage.py migrate --settings=kohya_ss_admin.settings api_auth
python manage.py migrate --settings=kohya_ss_admin.settings kohya_ss
python manage.py migrate --settings=kohya_ss_admin.settings
python manage.py createsuperuser --settings=kohya_ss_admin.settings