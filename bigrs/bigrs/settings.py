from bigrs.settings_production import *
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!0$-#hm0-i*&z+uk!1+7&+4xa_09lry*etganx429$j(i*-hyz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'bigrs.urls'

WSGI_APPLICATION = 'bigrs.wsgi.application'
SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ['bigrs.org','cetsp.com.br']
#SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS = ['me@foo.com', 'you@bar.com', '*@bigrs.org']
SOCIAL_AUTH_LOGIN_ERROR_URL = '/socialauth-error'


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '853484359918-tvh363pm7jt4oo21u34fb4v08u9r55bm.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '53O4A1t2OBtDoIwOiIPHWyUO'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': "bigrs",
        'PASSWORD':'bigrs',
        'HOST':'localhost',
        'PORT':'5432',
        'USER':'bigrs',
    }
}

LOGIN_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = '/home/tiago/works/bigrs/static'
STATIC_URL = '/static/'
STATICFILES_DIRS=[ os.path.join(os.path.dirname(BASE_DIR), 'bigrs/static') ]

VIDEO_FILES_ROOT='static/video'
#'/var/www/html/video'
VIDEO_URL_ROOT='http://localhost:81/'
#STATIC_ROOT=os.path.join(os.path.dirname(BASE_DIR), 'static')

ROLEPERMISSIONS_MODULE = 'bigrs.roles'

if DEBUG:
    import mimetypes
    mimetypes.add_type("video/mp4", ".mp4", True)
    mimetypes.add_type("video/mpeg", ".ASF", True)
    mimetypes.add_type("video/mpeg", ".asf", True)

from time import time
t = time()
DEPLOY_VERSION=time()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
   }
}