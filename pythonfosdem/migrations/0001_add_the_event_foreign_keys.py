# -*- coding: utf-8 -*-
from flask.ext.evolution import BaseMigration
from pythonfosdem.extensions import db
from pythonfosdem.models import Event


class Migration(BaseMigration):
    def up(self):
        db.create_all()
        event = Event(name='Python @ FOSDEM 2013')
        db.session.add(event)
        # db.session.flush()

        self.execute('ALTER TABLE speaker ADD COLUMN event_id INTEGER')
        self.execute('ALTER TABLE speaker ADD FOREIGN KEY (event_id) REFERENCES event(id)')
        self.execute('UPDATE speaker SET event_id = %s', (event.id,))
        self.execute('ALTER TABLE speaker ALTER COLUMN event_id SET NOT NULL')

        self.execute('ALTER TABLE talk ADD COLUMN event_id INTEGER')
        self.execute('ALTER TABLE talk ADD FOREIGN KEY (event_id) REFERENCES event(id)')
        self.execute('UPDATE talk SET event_id = %s', (event.id,))
        self.execute('ALTER TABLE speaker ALTER COLUMN event_id SET NOT NULL')

        self.execute('ALTER TABLE talk_proposal ADD COLUMN event_id INTEGER')
        self.execute('ALTER TABLE talk_proposal ADD FOREIGN KEY (event_id) REFERENCES event(id)')
        self.execute('UPDATE talk_proposal SET event_id = %s', (event.id,))
        self.execute('ALTER TABLE speaker ALTER COLUMN event_id SET NOT NULL')

        db.session.commit()
