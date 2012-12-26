#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    The command line of Python-FOSDEM.org

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from pythonfosdem import create_app
from pythonfosdem.extensions import db
from pythonfosdem.extensions import evolution
from pythonfosdem.models import user_datastore

def main():
    manager = Manager(create_app)

    @manager.command
    def migrate(action):
        """
        Make the migration of the schema
        """
        evolution.manager(action)

    @manager.command
    def db_populate():
        admin = user_datastore.create_role(name='admin')
        speaker = user_datastore.create_role(name='speaker')     # noqa

        stephane = user_datastore.create_user(name=u'Stéphane Wirtel',
                                              password='1234',
                                              email='stephane@wirtel.be',
                                              active=True,
                                              )
        christophe = user_datastore.create_user(name='Christophe Simonis',
                                                password='1234',
                                                email='christophe@simonis.kn.gl',
                                                active=True,
                                                )

        # TODO create Ludo and Tarek

        user_datastore.add_role_to_user(stephane, admin)
        user_datastore.add_role_to_user(christophe, admin)

        db.session.commit()

    @manager.command
    def db_create():
        db.create_all()

    @manager.command
    def db_drop():
        db.drop_all()

    manager.run()

if __name__ == '__main__':
    main()
