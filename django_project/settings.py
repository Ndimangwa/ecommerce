from pathlib import Path
import os
#from dotenv import load_dotenv
import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#Load dotenv
#load_dotenv()
LOCAL_CONNECT = False
if LOCAL_CONNECT:
    from dotenv import load_dotenv
    load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['gewgawed-unincorporated-hoa.ngrok-free.dev', 'localhost', '127.0.0.1', 'zoomtong.com', 'ecommerce-production-753f.up.railway.app']
CSRF_TRUSTED_ORIGINS = ['https://gewgawed-unincorporated-hoa.ngrok-free.dev', 'https://zoomtong.com', 'https://ecommerce-production-753f.up.railway.app']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #My Local Apps
    'store.apps.StoreConfig',
    'cart.apps.CartConfig',
    'payment.apps.PaymentConfig',
    'authorization.apps.AuthorizationConfig',
    'whitenoise.runserver_nostatic',
    #PayPal
    'paypal.standard.ipn',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates/"),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.CartProcessor',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

"""
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL_YOO'))
    #'default': {
    #    'ENGINE':'django.db.backends.postgresql',
    #    'NAME':'django_ecommerce',
    #    'USER':'postgres',
    #    'PASSWORD':os.environ['DB_PASSWORD_YOO'],
    #    'HOST':'postgres.railway.internal',
    #    'PORT':'5432',
    #}
}
"""
#Working with Database
from urllib.parse import urlparse 
#Connecting within railway
DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') if LOCAL_CONNECT else os.environ.get('DATABASE_URL')
db_info = urlparse(DATABASE_URL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'railway',
        'USER': db_info.username,
        'PASSWORD': db_info.password,
        'HOST': db_info.hostname,
        'PORT': db_info.port
    }
}

# User class
AUTH_USER_MODEL='authorization.User'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = ['static/']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFileStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#PayPal Stuff
PAYPAL_TEST = True # Turn this to False during production , this is a Sandbox Account
#Merchant Email
PAYPAL_RECEIVER_EMAIL = 'business@darone.com'