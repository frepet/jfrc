import json

from PySide2.QtCore import QObject, Signal

from Servo import Servo


class JFRCModel(QObject):
	"""
	Model for a JFRC Robot, stores servos and settings for the whole robot.
	Has two signals are available, steering_updated and throttle_updated.

	tick() should be called frequently to update the servos.

	Author: Fredrik Peteri, fredrik@peteri.se
	"""

	# Some default settings
	robot_settings = {
		"name": "Defaults",
		"servos": {
			0: {
				"mapping": {
					"function": "linear",
					"params": [0.0, 1.0],
				},
				"gain": 0.05,
			},
		},
		"keymap": {
			"turn_left": "A",
			"turn_right": "D",
			"turn_center": "C",
			"forward": "W",
			"reverse": "S",
		},
		"url": "localhost",
		"robot_port": 65520,
		"camera_port": 65521,
		"camera_size": (800, 600)
	}

	servos = {
		"steering": Servo(mapping=Servo.linear_mapping(0.0, 1.0), gain=0.05),
		"throttle": Servo(mapping=Servo.linear_mapping(0.0, 1.0)),
	}

	# Signals the steering value from 0.0-1.0
	steering_updated = Signal(float)

	# Signals the throttle value from 0.0-1.0
	throttle_updated = Signal(float)

	def throttle_value(self):
		return self.servos["throttle"].get()

	def steering_value(self):
		return self.servos["steering"].get()

	def move_left(self):
		self.servos["steering"].move_low = True

	def left_stop(self):
		self.servos["steering"].move_low = False

	def move_right(self):
		self.servos["steering"].move_high = True

	def right_stop(self):
		self.servos["steering"].move_high = False

	def move_center(self):
		self.servos["steering"].move_center = True

	def center_stop(self):
		self.servos["steering"].move_center = False

	def forward(self):
		self.servos["throttle"].set_high()
		self.throttle_updated.emit(self.servos["throttle"].value)

	def neutral(self):
		self.servos["throttle"].set_center()
		self.throttle_updated.emit(self.servos["throttle"].value)

	def reverse(self):
		self.servos["throttle"].set_low()
		self.throttle_updated.emit(self.servos["throttle"].value)

	def left(self):
		self.servos["steering"].set_low()
		self.steering_updated.emit(self.servos["steering"].value)

	def right(self):
		self.servos["steering"].set_high()
		self.steering_updated.emit(self.servos["steering"].value)

	def center(self):
		self.servos["steering"].set_center()
		self.steering_updated.emit(self.servos["steering"].value)

	def save(self, filename):
		if filename == '':
			return
		with open(filename, "w") as f:
			f.write(json.dumps(self.robot_settings, indent=4))

	def load(self, filename):
		if filename == '':
			return
		with open(filename, "r") as f:
			self.robot_settings = json.loads(f.read())

	def get_camera_port(self):
		return self.robot_settings["camera_port"]

	def get_robot_port(self):
		return self.robot_settings["robot_port"]

	def get_camera_size(self):
		return self.robot_settings["camera_size"]

	def get_keymap(self) -> dict:
		return self.robot_settings["keymap"]

	def tick(self):
		for servo in self.servos.values():
			servo.tick()

		self.steering_updated.emit(self.servos["steering"].value)
