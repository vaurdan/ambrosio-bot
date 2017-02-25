from mongoengine import *
import datetime

from database import database

class User(Document):

	id = IntField(primary_key=True)
	name = StringField(required=True)
	username = StringField(unique_with=['id'])
	input = StringField(required=True)
	created_at = DateTimeField(default=datetime.datetime.now)

	user_data = DictField()

	meta = {'allow_inheritance': True}


def find_by_id( id ):
	return User.objects(id=id).first()
