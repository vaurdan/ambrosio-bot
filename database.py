from peewee import SqliteDatabase
from slugify import slugify


db = SqliteDatabase( "ambrosio.db", threadlocals=True )

def database():
	return db