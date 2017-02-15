from peewee import *
import datetime

from database import database

class User(Model):

	id = PrimaryKeyField()
	name = CharField()
	username = CharField(unique=True)
	input = CharField()
	created_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = database()

