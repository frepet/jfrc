from PySide2.QtCore import QObject, Signal, Qt

from Servo import Servo


class JFRCModel(QObject):
	"""
	Model for a JFRC Robot, stores servos and settings for the whole robot.
	Has two signals are available, steering_updated and throttle_updated.

	tick() should be called frequently to update the servos.

	Author: Fredrik Peteri, fredrik@peteri.se
	"""
	servos = {
		"steering": Servo(mapping=Servo.linear_mapping(0.65, 0.3), gain=0.05, center=0.5),
		"throttle": Servo(mapping=Servo.linear_mapping(0.33, 0.66)),
	}

	url = "localhost"
	SERVER_PORT = 65520
	CAMERA_PORT = 65521
	camera_size = (800, 600)
	keymap = {
		"turn_left": Qt.Key_A,
		"turn_right": Qt.Key_D,
		"turn_center": Qt.Key_C,
		"forward": Qt.Key_W,
		"reverse": Qt.Key_S,
	}

	# Signals the steering value from 0.0-1.0
	steering_updated = Signal(float)

	# Signals the throttle value from 0.0-1.0
	throttle_updated = Signal(float)

	def throttle_value(self):
		return self.servos["throttle"].get()

	def steering_value(self):
		return self.servos["steering"].get()

	def left(self):
		self.servos["steering"].move_low = True

	def left_stop(self):
		self.servos["steering"].move_low = False

	def right(self):
		self.servos["steering"].move_high = True

	def right_stop(self):
		self.servos["steering"].move_high = False

	def center(self):
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

	def tick(self):
		for servo in self.servos.values():
			servo.tick()

		self.steering_updated.emit(self.servos["steering"].value)
