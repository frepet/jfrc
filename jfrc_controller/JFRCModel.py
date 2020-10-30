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

	pwms = {
		"steering": {
			"value": BoundedInteger(127, 0, 255),
			"gain": BoundedInteger(5),
			"center_gain": BoundedInteger(5),
		}
	}

	active = {
		"steering": BoundedInteger(0),
		"center": False,
	}

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
