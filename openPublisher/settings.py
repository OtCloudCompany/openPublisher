from pathlib import Path
import os
from django.conf.locale.en import formats as en_formats
from web3 import Web3

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-le&j75j$)k@#xverf@y_o_7dwt73*@*he)6r6aml$i=fa37eh%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'accounts',
    'journals',
    'manuscripts'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'openPublisher.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'openPublisher.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

# Set to True to wrap each view in a transaction on the database
ATOMIC_REQUESTS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MAX_UPLOAD_SIZE = 5242880
FILE_UPLOAD_PERMISSIONS = 0o640

BASE_URL = 'localhost'
LOGIN_URL = '/profiles/login'

en_formats.DATE_FORMAT = 'd-m-Y'
en_formats.DATETIME_FORMAT = 'd-m-Y H:i:s'
en_formats.DATE_INPUT_FORMATS = ['%d-%m-%Y']
en_formats.DATETIME_INPUT_FORMATS = ['%d-%m-%Y %H:%i:%s']

AUTH_USER_MODEL = 'accounts.Profile'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60*60*24  # 24 hours

APPEND_SLASH = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = [
    'http://localhost:4200',
    # Add other domains that need to be allowed
]

CORS_ALLOW_CREDENTIALS = True

# WEB3 TOOLS
W3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/33402a9c3c794b65ae627ce14205f81a'))
W3_OWNERS_ADDRESS = Web3.to_checksum_address("0x674938B41B6ed666989f4C476A721224288F0b1E".lower())
W3_CONTRACT_ADDRESS = Web3.to_checksum_address("0x0f20c349b63e3f42c64dcd70b40530869c6c99c5")
W3_PRIV_KEY = '0xd3af8e91942b26667d2d0e04bbc06b9cbe67b162daf8c3db3e31aac1d2f41eb5'  # open('priv_key.txt').readline()
W3_TEST_ACCOUNTS = [
    W3_OWNERS_ADDRESS,
    Web3.to_checksum_address("0x0297F6C254CeD9B8A3A3d829dfA80ccB73d5e6ED".lower()),
    Web3.to_checksum_address("0xB4a271B7e99B07Cd8989f8e1C7ccfc42Fd41eC6A".lower())
]
INFURA_API_KEY = '33402a9c3c794b65ae627ce14205f81a'
INFURA_SECRET_KEY = '93c55cc9d9634b2090ce32c68f6cf699'
