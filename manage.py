from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from models import *

migrate = Migrate(app, db)
manager = Manager(app)

# migrations
manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def create_admin():
    """Creates the admin user."""
    db.session.add(User(email='admin@hello.com', password='admin', admin=True))
    db.session.commit()

@manager.command
def create_data():
    """Creates sample data."""
    pass


if __name__ == '__main__':
    manager.run()