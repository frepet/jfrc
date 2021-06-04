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
				0: int(1000 + self.model.steering_value() * 1000),
				1: int(1000 + self.model.throttle_value() * 1000),
			})
			sleep(0.02)

	def stop(self):
		self.running = False
