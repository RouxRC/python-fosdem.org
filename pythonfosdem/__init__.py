# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask import render_template

from flask.ext.babel import _
from flask.ext.mail import Message

from pythonfosdem.bp_general import blueprint as bp_general
from pythonfosdem.config import DefaultConfig
from pythonfosdem.extensions import babel
from pythonfosdem.extensions import bootstrap
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
from pythonfosdem.extensions import security
from pythonfosdem.extensions import evolution

from pythonfosdem.models import user_datastore

__all__ = ['App', 'create_app']


class App(Flask):
    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', None)

        Flask.__init__(self, *args, **kwargs)

        self.config.from_object(DefaultConfig())

        if config is not None:
            self.config.from_object(config)
        if 'PYTHONFOSDEM_SETTINGS' in os.environ:
            self.config.from_pyfile(os.environ['PYTHONFOSDEM_SETTINGS'])

        self.configure_blueprints()
        self.configure_extensions()
        self.configure_error_handlers()

    def configure_blueprints(self):
        self.register_blueprint(bp_general)

    def configure_extensions(self):
        bootstrap.init_app(self)
        babel.init_app(self)
        mail.init_app(self)
        db.init_app(self)
        security.init_app(self, user_datastore)
        evolution.init_app(self)

    def configure_error_handlers(self):
        @self.errorhandler(404)
        def not_found(error):
            return render_template('errors/404.html'), 404

        @self.errorhandler(500)
        def internal_error(error):
            message = Message(_('[PythonFOSDEM] Error 500'),
                              sender='internal-error@python-fosdem.org',
                              recipients=['stephane@wirtel.be'])
            message.body = render_template('emails/send_error_500.txt', error=error)

            mail.send(message)
            return render_template('errors/500.html'), 500


def create_app(config=None):
    return App(__name__, config=config)
