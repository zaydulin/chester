import os
from datetime import timedelta
from celery.schedules import crontab
from environs import Env
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase, digits

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY", "s6&pl7!-8d97nvje@mqz^4+%p=v)8bxaew)3-y9993q_xn04ir")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", True)

# ALLOWED_HOSTS = ['chestersbets.works-all.ru']
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", ["*"])

# Application definition

INSTALLED_APPS = [
    "daphne",
    "jazzmin",
    "debug_toolbar",
    "events.apps.EventsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Library (Бибилиотеки)
    "ckeditor",
    "captcha",
    "ckeditor_uploader",
    "ipware",
    "django_celery_results",
    # app (Приложения)
    "mainapp.apps.MainappConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'mainapp.blocked_user_middleware.BlockedUserMiddleware',
    # 'mainapp.middleware.BlockIPMiddleware',
    # 'mainapp.middleware.UserSessionMiddleware',
    # 'ipware.middleware.IPWareMiddleware',
]

ROOT_URLCONF = "_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "_project.asgi.application"
WSGI_APPLICATION = "_project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("POSTGRES_DB", "db_chester"),
        "USER": env.str("POSTGRES_USER", "admin"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", "qwe123QWE"),
        "HOST": env.str("DJANGO_POSTGRES_HOST", "localhost"),
        "PORT": env.int("DJANGO_POSTGRES_PORT", 5432),
    }
}
# DATABASES = {
#     "default": {
#          'ENGINE': 'django.db.backends.sqlite3',
#          'NAME': BASE_DIR / 'db.sqlite3',
#      }
# }
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono",
        # 'skin': 'office2013',
        "toolbar_Basic": [["Source", "-", "Bold", "Italic"]],
        "toolbar_YourCustomToolbarConfig": [
            {"name": "document", "items": ["Source", "-", "Save", "NewPage", "Preview", "Print", "-", "Templates"]},
            {"name": "clipboard", "items": ["Cut", "Copy", "Paste", "PasteText", "PasteFromWord", "-", "Undo", "Redo"]},
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll"]},
            {
                "name": "forms",
                "items": [
                    "Form",
                    "Checkbox",
                    "Radio",
                    "TextField",
                    "Textarea",
                    "Select",
                    "Button",
                    "ImageButton",
                    "HiddenField",
                ],
            },
            "/",
            {
                "name": "basicstyles",
                "items": ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript", "-", "RemoveFormat"],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "Blockquote",
                    "CreateDiv",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                    "BidiLtr",
                    "BidiRtl",
                    "Language",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {
                "name": "insert",
                "items": ["Image", "Flash", "Table", "HorizontalRule", "Smiley", "SpecialChar", "PageBreak", "Iframe"],
            },
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
            "/",  # put this to force next toolbar on new line
            {
                "name": "yourcustomtools",
                "items": [
                    # put the name of your editor.ui.addButton here
                    "Preview",
                    "Maximize",
                ],
            },
        ],
        "toolbar": "YourCustomToolbarConfig",  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",  # the upload image feature
                # your extra plugins here
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # 'devtools',
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
    }
}

AUTH_USER_MODEL = "mainapp.User"
SITE_ID = 1

RANDOM_URL_CHARSET = f"{ascii_lowercase}{ascii_uppercase}{digits}"
RANDOM_URL_LENGTH = 32
RANDOM_URL_MAX_TRIES = 4

# Websocket settings
# CSRF_TRUSTED_ORIGINS = "https://chestersbets.works-all.ru"
CSRF_TRUSTED_ORIGINS = ("https://chestersbets.works-all.ru",)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("cb-redis", 6379)],
            "capacity": 1024 * 1024,
        },
    }
}

# Celery settings
CELERY_BROKER_URL = f"redis://{env.str('DJANGO_REDIS_HOST', 'localhost')}:6379/2"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_LOG_FORMAT = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
CELERYD_LOG_FILE = "/var/www/chester/celery.log"

CELERY_BEAT_SCHEDULE = {
    # пн
    "create_events_of_tournament_id1": {
        "task": "events.tasks.create_events_of_tournament_id1",
        "schedule": crontab(
            hour="*/4",
        ),
    },
    "create_events_of_tournament_id2": {
        "task": "events.tasks.create_events_of_tournament_id2",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="mon"
        ),
    },
    # вт
    "create_events_of_tournament_id3": {
        "task": "events.tasks.create_events_of_tournament_id3",
        "schedule": crontab(
            hour="4",
            day_of_week="tue"
        ),
    },
    "create_events_of_tournament_id4": {
        "task": "events.tasks.create_events_of_tournament_id4",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="tue"
        ),
    },
    # ср
    "create_events_of_tournament_id6": {
        "task": "events.tasks.create_events_of_tournament_id6",
        "schedule": crontab(
            hour="4",
            day_of_week="wed"
        ),
    },
    "create_events_of_tournament_id7": {
        "task": "events.tasks.create_events_of_tournament_id7",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="wed"
        ),
    },
    # чт
    "create_events_of_tournament_id12": {
        "task": "events.tasks.create_events_of_tournament_id12",
        "schedule": crontab(
            hour="4",
            day_of_week="thu"
        ),
    },
    "create_events_of_tournament_id13": {
        "task": "events.tasks.create_events_of_tournament_id13",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="thu"
        ),
    },
    # пт
    "create_events_of_tournament_id15": {
        "task": "events.tasks.create_events_of_tournament_id15",
        "schedule": crontab(
            hour="4",
            day_of_week="fri"
        ),
    },
    "create_events_of_tournament_id21": {
        "task": "events.tasks.create_events_of_tournament_id21",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="fri"
        ),
    },
    # сб
    "create_events_of_tournament_id25": {
        "task": "events.tasks.create_events_of_tournament_id25",
        "schedule": crontab(
            hour="4",
            day_of_week="sat"
        ),
    },
    "create_events_of_tournament_id36": {
        "task": "events.tasks.create_events_of_tournament_id36",
        "schedule": crontab(
            hour="4",
            minute="20",
            day_of_week="sat"
        ),
    },
    "create_additional_info_for_events_1": {
        "task": "events.tasks.create_additional_info_for_events_id1",
        "schedule": crontab(
            hour="4",
            minute="40",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_2": {
        "task": "events.tasks.create_additional_info_for_events_id2",
        "schedule": crontab(
            hour="4",
            minute="50",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_3": {
        "task": "events.tasks.create_additional_info_for_events_id3",
        "schedule": crontab(
            hour="5",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_4": {
        "task": "events.tasks.create_additional_info_for_events_id4",
        "schedule": crontab(
            hour="5",
            minute="10",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_6": {
        "task": "events.tasks.create_additional_info_for_events_id6",
        "schedule": crontab(
            hour="5",
            minute="20",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_7": {
        "task": "events.tasks.create_additional_info_for_events_id7",
        "schedule": crontab(
            hour="5",
            minute="30",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_12": {
        "task": "events.tasks.create_additional_info_for_events_id12",
        "schedule": crontab(
            hour="5",
            minute="40",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_13": {
        "task": "events.tasks.create_additional_info_for_events_id13",
        "schedule": crontab(
            hour="5",
            minute="50",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_15": {
        "task": "events.tasks.create_additional_info_for_events_id15",
        "schedule": crontab(
            hour="6",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_21": {
        "task": "events.tasks.create_additional_info_for_events_id21",
        "schedule": crontab(
            hour="6",
            minute="10",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_25": {
        "task": "events.tasks.create_additional_info_for_events_id25",
        "schedule": crontab(
            hour="6",
            minute="20",
            day_of_week="mon-sun"
        ),
    },
    "create_additional_info_for_events_36": {
        "task": "events.tasks.create_additional_info_for_events_id36",
        "schedule": crontab(
            hour="6",
            minute="30",
            day_of_week="mon-sun"
        ),
    },

    # вск
    "create_tournament": {
        "task": "events.tasks.create_tournament",
        "schedule": crontab(
            hour="3",
            day_of_week="sun"
        ),
    },
    "get_match_stream_link_football": {
        "task": "events.tasks.get_match_stream_link",
        "schedule": crontab(minute="*"),
    },
    "fetch_event_data_id1": {
        "task": "events.tasks.fetch_event_data_id1",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id2": {
        "task": "events.tasks.fetch_event_data_id2",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id3": {
        "task": "events.tasks.fetch_event_data_id3",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id4": {
        "task": "events.tasks.fetch_event_data_id4",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id6": {
        "task": "events.tasks.fetch_event_data_id6",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id7": {
        "task": "events.tasks.fetch_event_data_id7",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id12": {
        "task": "events.tasks.fetch_event_data_id12",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id13": {
        "task": "events.tasks.fetch_event_data_id13",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id15": {
        "task": "events.tasks.fetch_event_data_id15",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id21": {
        "task": "events.tasks.fetch_event_data_id21",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_id25": {
        "task": "events.tasks.fetch_event_data_id25",
        "schedule": crontab(minute="*/2"),
    },
    "fetch_event_data_i36": {
        "task": "events.tasks.fetch_event_data_id36",
        "schedule": crontab(minute="*/2"),
    },
}
CELERY_RESULT_BACKEND = "django-db"

# CSRF SETTINGS
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

RECAPTCHA_PUBLIC_KEY = "6Lezmb8oAAAAAO65cpU3w6qIu1vAzGd-nzyx0CKJ"
RECAPTCHA_PRIVATE_KEY = "6Lezmb8oAAAAAF3vLlbePB9gJWPNfnybWj0YHjRb"
RECAPTCHA_DEFAULT_ACTION = "generic"
RECAPTCHA_SCORE_THRESHOLD = 0.5
LOGIN_URL = "/login/"
JAZZMIN_SETTINGS = {
    "site_brand": "Админ Панель"
}
INTERNAL_IPS = [
    "127.0.0.1",

]