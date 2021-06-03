from sys import argv
try:
    channel = int(argv[1])
    val = int(argv[2])
except Exception:
    print(f"USAGE: python3 {argv[0]} CHANNEL MICROSECONDS")
    exit(1)

with open("/dev/servoblaster", "w") as sb:
    print(f"{channel}={val}us", file=sb)
