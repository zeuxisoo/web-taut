# coding: utf-8

import hashlib
from datetime import datetime
from flask.ext.bcrypt import Bcrypt
from .base import SessionMixin, db

class Account(db.Model, SessionMixin):
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username      = db.Column(db.String(30), nullable=False, unique=True, index=True)
    email         = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password      = db.Column(db.String(100), nullable=False)
    role          = db.Column(db.String(10), default='user')
    create_at     = db.Column(db.DateTime, default=datetime.utcnow)
    update_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        if 'password' in kwargs:
            self.password = self.password_hash(kwargs.pop('password'))

    def __str__(self):
        return self.email

    def __repr__(self):
        return '<Account: %s>' % self.id

    def password_verify(self, password):
        return Bcrypt().check_password_hash(self.password, password)

    def avatar(self, size=48):
        md5email = hashlib.md5(self.email).hexdigest()
        query = "{0}?s={1}{2}".format(md5email, size, db.app.config['GRAVATAR_EXTRA'])
        return db.app.config['GRAVATAR_BASE_URL'] + query

    def update_password(self, new_password):
        self.password = self.password_hash(new_password)

    @staticmethod
    def password_hash(password, rounds=None):
        return Bcrypt().generate_password_hash(password, rounds=rounds)

    def to_json(self):
        return {
            'id'       : self.id,
            'username' : self.username,
            'email'    : self.email,
            'role'     : self.role
        }
