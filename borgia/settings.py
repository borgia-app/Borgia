"""
Django settings for borgia project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
#-*- coding: utf-8 -*-

import os, re

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'need to be changed'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # 'www.borgia.iresam.org' en prod, '*' pour une simulation de prod en local.

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
    'users',
    'shops',
    'notifications',
    'finances',
    'settings_data',
    'modules',
    'stocks',
    'graphene_django',
	'static_precompiler',
    'django_celery_results'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'contrib.models.LoginRequiredMiddleware',
    'contrib.models.RedirectLoginProfile',
    'contrib.models.SaveLoginUrlMiddleware',
]

ROOT_URLCONF = 'borgia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications'
            ],
            # Permet de rajouter extra à la
            'builtins': ['users.templatetags.users_extra']
        },
    },
]

WSGI_APPLICATION = 'borgia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

# Token auth backend
TOKEN_CHECK_ACTIVE_USER = True
TOKEN_TIMEOUT_DAYS = 7

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en²/1.9/howto/static-files/
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/gadzarts/'
LOGIN_URL = '/auth/login/'

LOGIN_EXEMPT_URLS = [
    '/auth/login/',
    '/auth/password_reset/',
    '/auth/password_reset/done/',
    '/auth/done/',
    '/ajax/username_from_username_part/',
    '/local/jsi18n',
    '/admin/',
    '/self/lydias/callback/',
    '/arduino/connect/',
    '/arduino/checkuser/',
    '/arduino/checkvolumeavailable/',
    '/arduino/purchase/',
]

LOGIN_EXEMPT_URL_PATTERNS = [
    re.compile('%s[\w-]+%s' % ('/auth/gadzarts/', '/')),
    re.compile('%s[\w-]+%s' % ('/auth/', '/')),
    re.compile('^%s$' % ('/graphql')),
    re.compile('^%s.+%s[\d]+%s$' % ('/jwt/token/', '/', '.json')),
    re.compile('^%s.+%s[\d]+%s$' % ('/jwt/invalidate/', '/', '.json')),
    re.compile('^%s$' % ('/jwt/new.json')),
    re.compile('^%s.+$' % ('/media/img/avatars/')),
    re.compile('^%s.+$' % ('/static/media/img/'))
    ]

STATIC_URL = '/static/'
# STATIC_ROOT = 'static/static_root/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'static_root')
STATICFILES_DIRS = (
    # 'static/static_dirs/',
    os.path.join(BASE_DIR, 'static', 'static_dirs'),
)

if (DEBUG == True):
    STATIC_PRECOMPILER_ROOT = os.path.join(BASE_DIR, 'static', 'static_dirs')


MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')
MEDIA_URL = '/media/'

# Lydia
LYDIA_API_TOKEN = 'need to be changed'
LYDIA_VENDOR_TOKEN = 'need to be changed'  # Trésorerie
# Foyer : 57e524da19aba655147763
LYDIA_CALLBACK_URL = 'https://borgia.iresam.org/self/lydias/callback/'  # https ou non selon le dns
LYDIA_CONFIRM_URL = 'http://borgia.iresam.org/gadzarts/self/lydias/confirm/'

# Penser à activer 'autoriser l'acces par les applications moins sécurisées' dans Gmail
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ae.ensam.assoc@gmail.com'
SERVER_EMAIL = 'ae.ensam.assoc@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ae.ensam.assoc@gmail.com'
EMAIL_HOST_PASSWORD = 'Alexandre57'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Electrovanne
ARDUINO_PRIVATE = 'need to be changed'

ADMINS = []

# Durée de validité du token reset password
PASSWORD_RESET_TIMEOUT_DAYS = 1  # en jours

# Deconnection automatique
SESSION_COOKIE_AGE = 7200

# Mobile application
MOBILE_SECRET_KEY = 'need to be changed'
JWT_ALGORITHM = 'HS256'
JWT_TOKEN_TIMEOUT = 7  # days

# Les paramètres modifiables sont des objets Settings de l'app settings_data
# A modifier directement dans l'application
# [LYDIA_MIN_PRICE, LYDIA_MAX_PRICE, MARGIN_PROFIT]

CENTER_NAME = "Center Name"
DEFAULT_TEMPLATE = "light" #Default template, en minuscule

# Celery
CELERY_RESULT_BACKEND = 'django-db'
