from requests import ConnectionError
from requests import get, post
import json

class TooManyEntities(Exception):
	def __init__(self, entities):
		# Call the base class constructor with the parameters it needs
		super(TooManyEntities, self).__init__("")

		# Now for your custom code...
		self.entities = entities

class RemoteHA:

	api_url = None

	password = None

	def __init__(self, api_url, password):
		self.api_url = api_url
		self.password = password


	def test_connection(self):
		"""
		Tests the Home Assistant connection
		"""
		try:
			test = self.request()

			if test['message'] == "API running.":
				return True

			return False
		except ConnectionError:
			return False

	def get_all_states(self):
		return self.request('states')

	def get_entity_id(self, name):
		entity = self.get_entity(name)

		if entity is None:
			return None

		return entity['entity_id']

	def get_entity(self,name):
		name = name.strip()
		states = self.get_all_states()

		num_ocurrences = 0
		curr_state = None
		found_states = []
		for state in states:
			if state['attributes']['friendly_name'].lower() == name.lower():
				return state
			if name.lower() in state['attributes']['friendly_name'].lower():
				num_ocurrences += 1
				curr_state = state
				found_states.append(curr_state)

		if num_ocurrences == 0:
			print "zero ocurrences"
			return None

		if num_ocurrences > 1:
			raise TooManyEntities(found_states)

		return curr_state

	def switch(self, entity_id, state):
		if 'on' != state.lower() and 'off' != state.lower():
			return False

		data = {
			'entity_id': entity_id,
		}

		print entity_id
		# If it's a light
		if 'light.' in entity_id:
			return self.request( "services/light/turn_%s" % state.lower(), method="POST", data=data)
		if 'switch.' in entity_id:
			return self.request( "services/switch/turn_%s" % state.lower(), method="POST", data=data)



	def request(self, endpoint = "", data=None, method="GET"):

		if data is None:
			data = {}

		url = self.api_url + str(endpoint)
		headers = {'Content-Type': 'application/json'}

		if self.password is not None and self.password is not False :
			headers['x-ha-access'] = self.password

		response = None
		if method.lower() == 'get':
			response = get(url, headers=headers,data=json.dumps( data ) )
		elif method.lower() == 'post':
			response = post(url, headers=headers,data=json.dumps( data ) )

		return json.loads( response.text )

