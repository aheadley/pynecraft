#!/usr/bin/env python

from wrapper import Wrapper

if __name__ == '__main__':
    server = Wrapper()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()