#!/usr/bin/env python

import os
import hmac
from hashlib import sha1
from flask import Flask, g
from flask.ext.babel import Babel, format_datetime
from .models import db
from .routes import index, settings, media, bookmark, developer
from .routes import admin, api
from .tasks import make_celery
from .helpers.account import load_current_user
from .helpers.value import thumb, human_time

def create_app(config=None):
    app = Flask(__name__, template_folder='views')
    app.static_folder = os.path.abspath('static')

    app.config.from_pyfile('configs/default.py')

    production_config = os.path.join(os.path.dirname(__file__), 'configs/production.py')
    if os.path.exists(production_config):
        app.config.from_pyfile(production_config)

    if isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(os.path.abspath(config))

    register_hook(app)
    register_babel(app)
    register_celery(app)
    register_celery_beat(app)
    register_jinja2(app)
    register_database(app)
    register_route(app)

    return app

def register_hook(app):
    @app.before_request
    def current_user():
        g.user = load_current_user()

def register_babel(app):
    babel = Babel(app)

def register_celery(app):
    app.celery = make_celery(app)

def register_celery_beat(app):
    from .tasks.schedule import fetch_lists

def register_jinja2(app):
    @app.template_filter('timeago')
    def timeago(value):
        return human_time(value)

    @app.template_filter('dateformat')
    def dateformat(_datetime, format='yyyy-MM-dd H:mm'):
        return format_datetime(_datetime, format)

    @app.template_filter('thumbor')
    def thumbor(url, width, height, unsafe=False):
        return thumb(url, width, height, unsafe)

    @app.template_filter('remove_url')
    def remove_url(text):
        import re
        return re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text, flags=re.MULTILINE)

def register_database(app):
    db.init_app(app)
    db.app = app

def register_route(app):
    app.register_blueprint(admin.account.blueprint, url_prefix='/admin/account')
    app.register_blueprint(admin.list_media.blueprint, url_prefix='/admin/list-media')
    app.register_blueprint(admin.list_tweet.blueprint, url_prefix='/admin/list-tweet')
    app.register_blueprint(admin.list_user.blueprint, url_prefix='/admin/list-user')
    app.register_blueprint(admin.main.blueprint, url_prefix='/admin')
    app.register_blueprint(api.main.blueprint, url_prefix='/api')
    app.register_blueprint(developer.blueprint, url_prefix='/developer')
    app.register_blueprint(bookmark.blueprint, url_prefix='/bookmark')
    app.register_blueprint(media.blueprint, url_prefix='/media')
    app.register_blueprint(settings.blueprint, url_prefix='/settings')
    app.register_blueprint(index.blueprint, url_prefix='')
