#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    The command line of Python-FOSDEM.org

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask import url_for
from flask.ext.babel import _
from flask.ext.mail import Message
from flask.ext.script import Manager
from flask.ext.script.commands import ShowUrls
from pythonfosdem import create_app
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
import pythonfosdem.tools
import pythonfosdem.models
import pythonfosdem.xml_importer
from pythonfosdem.models import Talk
from pythonfosdem.models import User


def main():
    manager = Manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.add_command('routes', ShowUrls())

    @manager.command
    def send_talk_emails():
        with mail.connect() as conn:
            for talk in Talk.query.filter_by(state='validated').limit(1):
                values = {
                    'url_talk': url_for('general.talk_show', record_id=talk.id, slug=talk.slug, _external=True),
                    'speaker': talk.user.name,
                    'talk_name': talk.name,
                    'talk_description': talk.description,
                    'talk': talk,
                }

                message = Message(_('[Python-FOSDEM] Your talk has been accepted !'),
                                  recipients=[talk.user.email],
                                  sender='info@python-fosdem.org',
                                  bcc=['stephane@wirtel.be']
                                  )
                message.body = render_template('emails/talk_accepted.txt', **values)
                conn.send(message)

    @manager.command
    def send_speaker_emails():
        with mail.connect() as conn:
            for user in User.query.order_by(User.name).all():
                if user.is_speaker:
                    print user.name
                    print user.password
                    print render_template('emails/speaker_email.txt', user=user)
                    message = Message(_('[Python-FOSDEM] Information and Questions'),
                                      sender='info@python-fosdem.org',
                                      recipients=['stephane@wirtel.be'],
                                      bcc=['stephane@wirtel.be']
                                      )
                    message.body = render_template('emails/speaker_email.txt', user=user)
                    conn.send(message)

    @manager.command
    def import_xml(filename):
        with open(filename, 'r') as fp:
            xml_records = pythonfosdem.xml_importer.parse(fp)

            for xml_id, xml_record in xml_records.iteritems():
                instance, proxy = pythonfosdem.tools.create_or_update(xml_record.model, xml_id)
                instance_is_new = instance.id is None

                for field_name, field_value in xml_record.fields.iteritems():
                    current_field = getattr(instance, field_name)

                    if isinstance(field_value, dict) and 'reference' in field_value:
                        ref_model, ref_id, record = pythonfosdem.tools.get_xml_id_or_raise(field_value['reference'])
                        setattr(instance, field_name, record)
                    elif pythonfosdem.tools.is_relationship(proxy, field_name):
                        for nested_xml_id in xml_record.fields[field_name].split(','):
                            operator = '+'
                            if nested_xml_id[0] in ('+', '-'):
                                operator, nested_xml_id = nested_xml_id[0], nested_xml_id[1:]

                            ref_model, ref_id, record = pythonfosdem.tools.get_xml_id_or_raise(nested_xml_id)

                            if operator == '-':
                                current_field.remove(record)
                            else:
                                current_field.append(record)
                    else:
                        setattr(instance, field_name, field_value)

                db.session.add(instance)
                db.session.flush()

                if instance_is_new:
                    instance_model_data = pythonfosdem.models.ModelData(name=xml_id,
                                                                        ref_model=xml_record.model,
                                                                        ref_id=instance.id)
                    db.session.add(instance_model_data)
                    db.session.flush()

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
