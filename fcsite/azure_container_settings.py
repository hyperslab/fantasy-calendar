from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


ALLOWED_HOSTS = \
    [os.environ['CONTAINER_APP_NAME'] + '.' + os.environ['CONTAINER_APP_ENV_DNS_SUFFIX'],
     os.environ['CONTAINER_APP_HOSTNAME']]
CSRF_TRUSTED_ORIGINS = \
    ['https://' + os.environ['CONTAINER_APP_NAME'] + '.' + os.environ['CONTAINER_APP_ENV_DNS_SUFFIX'],
     'https://' + os.environ['CONTAINER_APP_HOSTNAME']]
DEBUG = False

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

conn_str = os.environ['AZURE_SQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(';')}
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': conn_str_params['Initial Catalog'],
        'HOST': conn_str_params['Server'],
        'USER': conn_str_params['User ID'],
        'PASSWORD': conn_str_params['Password'],
        'OPTIONS': {
            'connection_timeout': 62,
        },
    }
}
USE_TZ = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[contactor] %(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        # Send all messages to console
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
