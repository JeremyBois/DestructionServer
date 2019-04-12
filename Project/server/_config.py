# Project/server/_config.py

import os
from path import Path


# Grab the folder where this script lives
basedir = Path(__file__).dirname().abspath()


class BaseConfig(object):
    """Base configuration."""
    APP_NAME = 'Destruction Server App'
    ROOT_DIR = basedir / '../../'
    DATA_DIR = basedir / '../../Data'
    BCRYPT_LOG_ROUNDS = 4     # minimal value for encryption
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    DEBUG = False
    ENV = ''


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    PROPAGATE_EXCEPTIONS = True


# class TestingConfig(BaseConfig):
#     """Testing configuration."""
#     DATABASE_NAME = '../tests/tests.db'
#     DATABASE_PATH = basedir / DATABASE_NAME
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
#     TESTING = True
#     PROPAGATE_EXCEPTIONS = True


# class ProductionConfig(BaseConfig):
#     """Production configuration."""
#     BCRYPT_LOG_ROUNDS = 12
#     WTF_CSRF_ENABLED = True
#     PROPAGATE_EXCEPTIONS = False

#     # Heroku
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProductionPythonAnywhereConfig(BaseConfig):
    """Production configuration."""
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    PROPAGATE_EXCEPTIONS = False

    # # Sqlite with python anywhere
    # DATABASE_NAME = os.environ.get('DATABASE_NAME')
    # DATABASE_PATH = basedir / DATABASE_NAME
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
