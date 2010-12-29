#!/usr/bin/env python

from wrapper import Wrapper

if __name__ == '__main__':
    server = Wrapper()
    while server.keep_running():
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
            break
        except Exception as exception:
            print exception
