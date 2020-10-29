"""
Class used to send requests to the JF-RC Robot

Author: Fredrik Peteri, fredrik@peteri.se
"""
import requests


class JFRCRobotConnection:
	def __init__(self, url="", port=8081):
		self.url = f"http://{url}:{port}"

		try:
			requests.get(self.url + "/jfrc-test")
		except requests.ConnectionError:
			raise RuntimeError(f"Could not connect to {self.url}")

	def steering_left(self):
		requests.post(self.url + "/jfrc-pwms", json={'a': 0})

	def steering_right(self):
		requests.post(self.url + "/jfrc-pwms", json={'a': 255})

	def steering_forward(self):
		requests.post(self.url + "/jfrc-pwms", json={'a': 127})
