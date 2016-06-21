# -*- coding: utf-8 -*-
import bson
from pymongo import MongoClient
from werkzeug.routing import BaseConverter
from flask import abort, _request_ctx_stack


try:
    from flask import _app_ctx_stack
    ctx_stack = _app_ctx_stack
except ImportError:
    ctx_stack = _request_ctx_stack


class BSONObjectIdConverter(BaseConverter):

    def to_python(self, value):
        try:
            return bson.ObjectId(value)
        except bson.errors.InvalidId:
            raise abort(400)

    def to_url(self, value):
        return str(value)


class mongokat_container(object):
    """mongokat model container
    """

    def __init__(self, client, db, models):
        self.client = client

        for one_model in models:
            """register model to container
            """
            name = one_model.__name__
            if hasattr(one_model, '_db_'):
                db = getattr(one_model, '_db_')
            setattr(self, name, one_model(self.client[db][name]))

    def __del__(self):
        self.client.close()
        del self.client

    def __getitem__(self, name):
        return getattr(self, name)


class model_interface(object):
    """request handler
    """

    def __init__(self, app=None):
        self.registered_models = []

        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        app.config.setdefault('MONGODB_HOSTS', '127.0.0.1:27017')
        app.config.setdefault('MONGODB_DATABASE', 'colorsbee')
        app.config.setdefault('MONGODB_USER', 'colorsbee')
        app.config.setdefault('MONGODB_PASSWORD', 'colorsbee')

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self._teardown_request)
        elif hasattr(app, 'teardown_request'):
            app.teardown_request(self._teardown_request)
        else:
            app.after_request(self._teardown_request)

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['model_interface'] = self

        app.url_map.converters['ObjectId'] = BSONObjectIdConverter

        self.app = app

    def connect(self):
        if self.app is None:
            raise RuntimeError("The model interface was not init to the current application.")
        ctx = ctx_stack.top
        model_container = getattr(ctx, 'model_container', None)
        if model_container is None:
            mongodb_uri = "mongodb://{0}:{1}@{2}".format(ctx.app.config.get('MONGODB_USER'),
                                                         ctx.app.config.get('MONGODB_PASSWORD'),
                                                         ctx.app.config.get('MONGODB_HOSTS')
                                                         )
            ctx.model_container = mongokat_container(MongoClient(mongodb_uri),
                                                     ctx.app.config.get('MONGODB_DATABASE'),
                                                     self.registered_models
                                                     )

    def register(self, models):
        if not isinstance(models, (list, tuple, set, frozenset)):
            model_collections = [models]
        for one_model in models:
            if one_model not in self.registered_models:
                self.registered_models.append(one_model)

    @property
    def connected(self):
        ctx = ctx_stack.top
        return getattr(ctx, 'model_container', None) is not None

    def disconnect(self):
        """delete model_container who would auto close connection"""
        if self.connected:
            ctx = ctx_stack.top
            del ctx.model_container

    def __getattr__(self, name):
        if not self.connected:
            self.connect()
        model_container = getattr(ctx_stack.top, 'model_container')
        return getattr(model_container, name)

    def __getitem__(self, name):
        if not self.connected:
            self.connect()
        model_container = getattr(ctx_stack.top, 'model_container')
        return model_container[name]

    def _teardown_request(self, response):
        self.disconnect()
        return response


