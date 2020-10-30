from PySide2.QtCore import QObject, Signal


class JFRCModel(QObject):
	class BoundedInteger:
		def __init__(self, val=127, lower=-255, upper=255):
			self.val = val
			self.lower = lower
			self.upper = upper

		def __set__(self, instance, value):
			self.val = max(self.lower, min(self.val, self.upper))

		def __get__(self, instance, owner):
			return self.val

		def __sub__(self, other):
			self.val = max(self.lower, min(self.val - other.val, self.upper))
			return self

		def __add__(self, other):
			self.val = max(self.lower, min(self.val + other.val, self.upper))
			return self

		def __mul__(self, other):
			self.val = max(self.lower, min(self.val * other.val, self.upper))
			return self

		def __int__(self):
			return self.val

	steering_updated = Signal(int)
	throttle_updated = Signal(int)

	pwms = {
		"steering": {
			"value": BoundedInteger(127, 0, 255),
			"gain": BoundedInteger(5),
			"center_gain": BoundedInteger(5),
		},
		"throttle": {
			"value": BoundedInteger(127, 0, 255),
			"forward": BoundedInteger(255),
			"neutral": BoundedInteger(127),
			"reverse": BoundedInteger(0),
		}
	}

	active = {
		"steering": BoundedInteger(0),
		"center": False,
	}

	def throttle_value(self):
		return self.pwms["throttle"]["value"].val

	def steering_value(self):
		return self.pwms["steering"]["value"].val

	def left(self):
		self.active["steering"] -= self.pwms["steering"]["gain"]

	def left_stop(self):
		self.active["steering"] += self.pwms["steering"]["gain"]

	def right(self):
		self.active["steering"] += self.pwms["steering"]["gain"]

	def right_stop(self):
		self.active["steering"] -= self.pwms["steering"]["gain"]

	def center(self):
		self.active["center"] = True

	def center_stop(self):
		self.active["center"] = False

	def tick(self):
		if self.active["center"]:
			self._turn_towards_center()
		else:
			self.pwms["steering"]["value"] += self.active["steering"]

		self.steering_updated.emit(self.steering_value())

	def _turn_towards_center(self):
		if self.pwms["steering"]["value"].val in range(123, 133):
			self.pwms["steering"]["value"].val = 127
		else:
			gain = self.pwms["steering"]["center_gain"]
			self.pwms["steering"]["value"] += \
				gain if self.pwms["steering"]["value"].val < 127 else self.BoundedInteger(-1 * gain.val)

	def forward(self):
		self.pwms["throttle"]["value"] = self.pwms["throttle"]["forward"]
		self.throttle_updated.emit(self.throttle_value())

	def neutral(self):
		self.pwms["throttle"]["value"] = self.pwms["throttle"]["neutral"]
		self.throttle_updated.emit(self.throttle_value())

	def reverse(self):
		self.pwms["throttle"]["value"] = self.pwms["throttle"]["reverse"]
		self.throttle_updated.emit(self.throttle_value())
