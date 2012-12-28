# -*- coding: utf-8 -*-
"""
    pythonfosdem.models
    ~~~~~~~~~~~~~~~~~~~

    Models for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime
import hashlib

from flask.ext.security import RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security import UserMixin
from flask.ext.security.core import current_user

from pythonfosdem.extensions import db


class CommonMixin(object):
    @property
    def created_on(self):
        return datetime.date(self.created_at.year, self.created_at.month, self.created_at.day)


class ModelData(db.Model, CommonMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    ref_model = db.Column(db.String(80), nullable=False)
    ref_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, CommonMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)


class User(db.Model, UserMixin, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    biography = db.Column(db.Text)
    twitter = db.Column(db.String(255))
    site = db.Column(db.String(255))
    company = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def gravatar(self, size=None, default='identicon'):
        url = 'http://www.gravatar.com/avatar/{md5}.jpg?d={default}'
        if size is not None:
            url += '&s={size}'
        return url.format(md5=hashlib.md5(self.email).hexdigest, default=default, size=size)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Event(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)


class Speaker(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    short_bio = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    twitter = db.Column(db.String(255))
    site = db.Column(db.String(255))
    company = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
    #    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    #    event = db.relationship('Event', backref=db.backref('speakers', lazy='dynamic'))


class Talk(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('talks', lazy='dynamic'))
    description = db.Column(db.Text, nullable=False)
    site = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    approved = db.Column(db.Boolean)
    state = db.Column(db.String(16), default='draft')
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
    #    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    #    event = db.relationship('Event', backref=db.backref('talks', lazy='dynamic'))

    votes = db.relationship('TalkVote', backref="talk")

    @property
    def points(self):
        return sum(v.value for v in self.votes)

    @property
    def current_user_vote(self):
        for v in self.votes:
            if v.user_id == current_user.id:
                return v
        return None

class TalkProposal(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255, convert_unicode=True), nullable=False)
    lastname = db.Column(db.String(255, convert_unicode=True), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255, convert_unicode=True))
    twitter = db.Column(db.String(255))
    site_url = db.Column(db.String(255))
    biography = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255, convert_unicode=True), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
    # active = db.Column(db.Boolean, default=True)
    #event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    #event = db.relationship('Event', backref=db.backref('talk_proposals', lazy='dynamic'))


class TalkVote(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    talk_id = db.Column(db.Integer, db.ForeignKey('talk.id'), nullable=False)

    value = db.Column(db.Integer, nullable=False, default=False)
