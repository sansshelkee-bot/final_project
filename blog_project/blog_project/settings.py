"""
Django settings for blog_project project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2nparb@n*k48=foq&66h-%+w6rjewzplkm5v&jdris@*7*(b%e'

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

    # Local apps
    'blog',
    'accounts',
    'comments',

    # Third-party apps
    'crispy_forms',  # UNCOMMENT THIS LINE
    'crispy_bootstrap4',
    'tinymce',
    'taggit',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# MIDDLEWARE - ONLY ONE DEFINITION!
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Remove or comment this if you don't have blog.middleware.RateLimitMiddleware
    # 'blog.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'blog_project.urls'

import os
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages', 
                'django.template.context_processors.media',
                'blog.context_processors.categories',

                # Remove these if you don't have the files yet
                # 'blog.context_processors.categories_processor',
                # 'blog.context_processors.trending_posts_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'TEST': {
            'NAME': 'test_db.sqlite3',
        }
    }
}


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# TinyMCE configuration
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': '''
        textcolor save link image media preview codesample contextmenu
        table code lists fullscreen insertdatetime nonbreaking
        directionality searchreplace wordcount visualblocks
        visualchars autolink lists charmap print hr
        anchor pagebreak
    ''',
    'toolbar1': '''
        fullscreen preview bold italic underline | fontselect
        fontsizeselect | forecolor backcolor | alignleft alignright
        aligncenter alignjustify | indent outdent | bullist numlist table
        | link image media | codesample
    ''',
    'toolbar2': '''
        visualblocks visualchars |
        charmap hr pagebreak nonbreaking anchor | code
    ''',
    'context_menu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}


# Test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'


# Security settings (for production - commented for development)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# For production (uncomment when deploying)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Testing configuration
import sys

if 'test' in sys.argv:
    # Use faster password hasher for tests
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    
    # Speed up tests by using simpler password validation
    AUTH_PASSWORD_VALIDATORS = []






# Add these lines at the end of the file:
LOGIN_REDIRECT_URL = '/'  # Redirect to homepage
LOGOUT_REDIRECT_URL = '/'  # Redirect to homepage after logout
LOGIN_URL = '/accounts/login/'  # Login page URL
LOGIN_REDIRECT_URL = 'profile_view'
# If you have namespace for your blog app:
LOGIN_REDIRECT_URL = 'blog:post_list'