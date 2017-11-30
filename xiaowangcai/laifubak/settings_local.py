import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True
TPLPATH = os.path.join(BASE_DIR, 'static/templates')
DatabaseLocal = {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'laifu_test',
             'USER': 'root',
             'PASSWORD': 'shouzhuanvip',
             'PORT': '3306',
 }