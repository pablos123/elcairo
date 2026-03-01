"""Peewee ORM models."""

from peewee import AutoField, IntegerField, Model, SqliteDatabase, TextField

db = SqliteDatabase(None)


class EventModel(Model):
    """Events table."""

    event_id = AutoField()
    name = TextField()
    date = TextField()
    compare_date = IntegerField()
    synopsis = TextField()
    direction = TextField()
    cast = TextField()
    genre = TextField()
    duration = TextField()
    origin = TextField()
    year = TextField()
    age = TextField()
    cost = TextField()
    image_path = TextField()
    image_url = TextField()
    url = TextField()

    class Meta:
        database = db
        table_name = "events"
