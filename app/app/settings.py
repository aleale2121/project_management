import os
from distutils.debug import DEBUG
from pathlib import Path

import dj_database_url
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY_DEFAULT = "django-insecure-)9&)se2$z0-@&4j*b)_8qb$6z!9)f#@m(6imw*u7wd6t90b8"
SECRET_KEY = os.environ.get("SECRET_KEY", default=SECRET_KEY_DEFAULT)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = int(os.environ.get("DEBUG", default=0))
# DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "sfpm.herokuapp.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    'django_celery_results',
    "rest_framework.authtoken",
    'django_filters',
    "core",
    "users",
    "chatrooms",
    "channels",
    "drf_yasg",
    "groups",
    "evaluations",
    "titles",
    "semisters",
    "submission_types",
    "submission_dead_lines",
    "top_projects",

]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.routing.application"
CHANNEL_LAYERS = {
	'default': {
		'BACKEND': 'channels_redis.core.RedisChannelLayer',
		'CONFIG': {
			"hosts": ['redis://redis:6379/0'],
		},
	},
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
       'LOCATION': 'redis://redis:6379',
    }
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASS"),
        'ATOMIC_REQUESTS': True,
    }
}

db_from_env = dj_database_url.config(engine="django.db.backends.postgresql_psycopg2", conn_max_age=600)
DATABASES["default"].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
# STATICFILES_DIRS = ('/vol/web/static',)

# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = '/vol/web/static'
MEDIA_ROOT = '/vol/web/media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ["http://localhost:3000", "https://sfpm.herokuapp.com"]
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    "PAGE_SIZE": 100,
}
DJANGO_SETTINGS_MODULE= 'app.settings'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL=True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'yidegaait2010@gmail.com'
EMAIL_HOST_PASSWORD = 'wdivhgmrvjpqqieo' #past the key or password app here
EMAIL_PORT = 587
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'yidegaait2010@gmail.com'
# Celery properties
CELERY_BROKER_URL = 'amqp://admin:admin@rabbit:5672//'
CELERY_RESULT_BACKEND = 'django-db'
# REDIS_URL='redis://redis:6379/0'


AUTH_USER_MODEL = "core.User"
ACCOUNT_UNIQUE_EMAIL = True
APPEND_SLASH = False

