__author__ = 'daiguanlin'
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or ''
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = ''

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    DEBUG = True


class ProductionConfig(Config):

    pass


config = {'development': DevelopmentConfig, 'default': DevelopmentConfig, 'production': ProductionConfig}
