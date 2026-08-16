import json

import requests

import _config


class VerbAPI:

	baseURL = None
	apiKey = None

	def __init__(self):
		super(VerbAPI, self).__init__()
		self.baseURL = _config.erp_baseUrlProduction
		self.apiKey = _config.erp_apiKeyProduction

	def apiGet(self, URI: str):
		"""Fonction privé de requêtes API GET """
		return self._api(URI, 'GET')

	def apiPost(self, URI: str, data):
		"""Fonction privé de requêtes API POST"""
		return self._api(URI, 'POST', data)

	def apiPut(self, URI: str, data):
		"""Fonction privé de requêtes API PUT """
		return self._api(URI, 'PUT', json.dumps(data))

	def _api(self, URI, webVerbType='GET', data=None):
		"""Fonction privé de requêtes API"""
		headers = {'DOLAPIKEY': self.apiKey}
		url = self.baseURL + URI
		if webVerbType == 'GET':
			response = requests.get(url, headers=headers)
		elif webVerbType == 'POST':
			response = requests.post(url, headers=headers, data=data)
		elif webVerbType == 'PUT':
			headers['Accept'] = 'application/json'
			headers['Content-Type'] = 'application/json'
			response = requests.put(url, headers=headers, data=data)
		else:
			raise Exception('_api request type unknown : ' + webVerbType)
		if response.status_code == 404:  # pas de data
			return []

		if response.status_code != 200:
			raise Exception('_api status_code : ' + str(response.status_code) + " URL : " + url)

		return response.json()
