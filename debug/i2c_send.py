# Writes a VALUE to a I2C slave at a specific ADDRESS
#
# Author: Fredrik Peteri, fredrik@peteri.se

import smbus
from sys import argv

if len(argv) is not 3:
	print("USAGE: " + argv[0] + " ADDRESS VALUE")
	exit(1)

bus = smbus.SMBus(1)
bus.write_byte(int(argv[1]), int(argv[2]))

