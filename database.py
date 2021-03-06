from mongoengine import connect
from config import config

db = connect(
	db= config['database']['name'],
	username = config['database']['username'],
	password = config['database']['password'],
	host = config['database']['host']
	)

def database():
	return db