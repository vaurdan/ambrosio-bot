# -*- coding: utf-8 -*-
from skills import Skill
from tabulate import tabulate

class AdminCommands(Skill):

	def setup_rules(self):
		self.register_command("talk", self.talk)
		self.register_command("users", self.users)

	def talk(self, message):
		string = message.get_content()
		self.send_message( string.replace('/talk ', ''), message, reply=False)

	def users(self, message):

		string = message.get_content()
		args = string.split(" ")

		if args[1] == "list":
			self.list_command(args)
		elif args[1] ==  "set_admin":
			self.set_admin_command(args)

	def list_command(self, args):
		import models.user as UserModel

		print " === User Listing === "
		headers = ['ID', 'Name', 'Username', 'Admin', 'Source']
		table = []
		for user in UserModel.User.objects:
			element = [user.id, user.name, user.username, user.is_admin, user.input ]
			table.append(element)

		print tabulate(table, headers, tablefmt="grid")

	def set_admin_command(self, args):
		import models.user as UserModel

		if len( args ) < 3:
			print "Missing User ID"
			return

		user_id = args[2]
		user = UserModel.find_by_id(user_id)

		if user is None:
			print "Couldn't find user with ID " + str(user_id)
			return

		user.is_admin = True
		user.save()
		print "User " + str( user.username ) + " is now Administrator"

	def register_command(self, name, callback):
		self.add_rule( '^\/' + name, callback, ignore_prefix=True )