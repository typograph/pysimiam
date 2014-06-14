from collections import deque

logqueue = deque()

def log(obj, message):
    print("{}: {}".format(obj.__class__.__name__, message))
    logqueue.append((obj, message))