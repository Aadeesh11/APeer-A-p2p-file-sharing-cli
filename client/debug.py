import threading


def pr(msg):
    if (True):
        print(f'{threading.currentThread().getName()}' + msg)
