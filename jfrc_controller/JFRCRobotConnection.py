"""
Class used to send requests to the JF-RC Robot

Author: Fredrik Peteri, fredrik@peteri.se
"""
from time import sleep

import requests

from JFRCModel import JFRCModel

SERVER_PORT = 65520


class JFRCRobotConnection:
	def __init__(self, model: JFRCModel, url="", port=SERVER_PORT):
		self.url = f"http://{url}:{port}"

		try:
			requests.get(self.url + "/jfrc-test")
		except requests.ConnectionError:
			raise RuntimeError(f"Could not connect to {self.url}")

		self.model = model
		self.running = True

	def start(self):
		while self.running:
			self.model.tick()
			requests.post(self.url + "/jfrc-pwms", json={
				'a': self.model.steering_value(),
				'b': self.model.throttle_value(),
			})
			sleep(0.02)

	def stop(self):
		self.running = False

	def steering(self, pos):
		if type(pos) != int or pos not in range(256):
			raise ValueError(f"Steering value has to be an integer in range 0-255")

		requests.post(self.url + "/jfrc-pwms", json={'a': int(pos)})
