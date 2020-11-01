from time import sleep
import requests

from JFRCModel import JFRCModel


class JFRCRobotConnection:
	"""
	Connects the JFRCModel to a JF-RC Robot using the JF-RC API

	Author: Fredrik Peteri, fredrik@peteri.se
	"""

	def __init__(self, model: JFRCModel):
		self.url = f"http://{model.url}:{model.get_robot_port()}"

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
				'a': int(self.model.steering_value() * 255),
				'b': int(self.model.throttle_value() * 255),
			})
			sleep(0.02)

	def stop(self):
		self.running = False
