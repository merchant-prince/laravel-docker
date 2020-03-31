#! /usr/bin/env python3

from laravel_docker.application import Application


if __name__ == "__main__":
    try:
        application = Application()
        application.run()
    except Exception:
        pass
    else:
        pass
    finally:
        pass
