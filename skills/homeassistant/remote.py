from requests import ConnectionError
from requests import get
import json

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


	def request(self, endpoint = ""):
		url = self.api_url + str(endpoint)
		headers = {'content-type': 'application/json'}

		if self.password is not None and self.password is not False :
			headers['x-ha-access'] = self.password

		response = get(url, headers=headers)

		return json.loads(response.text)

