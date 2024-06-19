#!/usr/bin/python3

import sys
import time

if len(sys.argv) < 2:
    print("Usage: python wait.py HH:MM")
    sys.exit(1)

times = []
for arg in sys.argv[1:]:
    hour, minute = map(int, arg.split(":"))
    times.append(hour * 60 + minute)

while True:
    tm = time.localtime()
    current = tm.tm_hour*60 + tm.tm_min

    for t in times:
        d = current - t
        if d >= 0 and d <= 2:
            print(f'Reach {tm.tm_hour}:{tm.tm_min}')
            sys.exit(0)

    time.sleep(60)
