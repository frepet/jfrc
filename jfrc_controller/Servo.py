class Servo:
	"""
	Model for one servo, stores all the parameters about the servo and its current value.
	Call the method tick() for the servo to update itself based on the move toggles.

	Author: Fredrik Peteri, fredrik@peteri.se
	"""

	def __init__(self, mapping=lambda x: x, gain=0.1, center=0.5):
		self.mapping = mapping
		self.gain = gain
		self.center = center
		self.move_low = False
		self.move_high = False
		self.move_center = False
		self.value = 0.5
		self.delta = 0.0

	def set(self, value):
		self.value = min(1.0, max(0.0, value))

	def get(self):
		return self.mapping(self.value)

	def tick(self):
		if self.move_center:
			if 0.45 < self.value < 0.55:
				self.set(0.5)
			else:
				self.set((self.value + self.center) / 2)
		elif self.move_low:
			self.set(self.value - self.gain)
		elif self.move_high:
			self.set(self.value + self.gain)

	def set_low(self):
		self.value = 0.0

	def set_high(self):
		self.value = 1.0

	def set_center(self):
		self.value = self.center

	def trim(self, val):
		self.center = min(0.0, max(1.0, self.center + val))

	@staticmethod
	def linear_mapping(y1, y2):
		return lambda x: Servo.linear_remap(x, 0.0, 1.0, y1, y2)

	@staticmethod
	def linear_remap(x, x1, x2, y1, y2):
		return (x - x1) * (y2 - y1) / (x2 - x1) + y1
