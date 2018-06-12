import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_entries(self):
        return Journal.select().where(Journal.user == self)

    @classmethod
    def create_user(cls, email, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError("User already exists")


class Journal(Model):
    title = CharField(max_length=100)
    user = ForeignKeyField(
        model=User,
        related_name='entries'
    )
    entrydate = DateTimeField(default=datetime.datetime.now)
    timespent = FloatField()
    learned = CharField(max_length=1000)
    resources = TextField(default=None)

    @classmethod
    def create_entry(cls, title, entrydate, user, timespent, learned,
                     resources):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    entrydate=entrydate,
                    user=user,
                    timespent=timespent,
                    learned=learned,
                    resources=resources)
        except IntegrityError:
            raise ValueError("Journal already exists")

    class Meta:
        database = DATABASE
        order_by = ('-entrydate',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Journal, User], safe=True)
    DATABASE.close()
