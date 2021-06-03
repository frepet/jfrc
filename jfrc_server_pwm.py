import RPi.GPIO as GPIO
from time import sleep


class ServoController:
	def __init__(self, servo_pin: int):
		self.servo_pin = servo_pin
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.servo_pin, GPIO.OUT)
		self.pwm = GPIO.PWM(self.servo_pin, 50)
		self.pwm.start(0)

	def set_angle(self, angle: int):
		duty = ((0.05 / 180) * angle + 0.05) * 100
		GPIO.output(self.servo_pin, True)
		self.pwm.ChangeDutyCycle(duty)

	def stop(self):
		GPIO.output(self.servo_pin, False)
		self.pwm.ChangeDutyCycle(0)
		self.pwm.stop()
		GPIO.cleanup()


if __name__ == "__main__":
	sc = ServoController(servo_pin=11)
	sc.set_angle(0)
	sleep(3)
	sc.set_angle(90)
	sleep(3)
	sc.set_angle(180)
	sleep(3)
	sc.stop()

