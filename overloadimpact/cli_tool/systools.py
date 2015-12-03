import sys
import time


def easysleep(seconds):
    size = 60
    count = 0
    sys.stdout.write("    Minute %d  " % (count / 60))
    while True:
        count += 1
        sys.stdout.write(".")
        sys.stdout.flush()
        if count % size == 0:
            sys.stdout.write("\n    Minute %d  " % (count / 60))
            sys.stdout.flush()
        time.sleep(1)
        if count >= seconds:
            print
            return
