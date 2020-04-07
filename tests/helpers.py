import os
import sys
import random
import shutil
import string
from io import StringIO
from contextlib import contextmanager
from scripting_utilities import ChangeDirectory


@contextmanager
def suppressed_stdout():
    """
    Supress stdout in the current context, and redirect it to another buffer.
    This buffer is available in the "as" variable of the associated context
    manager within a "with" statement.

    Usage:
        with supress_stdout() as stdout:
            do_something()
        print(stdout.getvalue()) <-- get the contents of the buffer
    """

    old_stdout = sys.stdout
    sys.stdout = new_stdout = StringIO()

    try:
        yield new_stdout
    finally:
        sys.stdout = old_stdout


@contextmanager
def send_input(value):
    """
    Pass a string to stdin.

    Args:
        value (str): The string to pass to stdin
    """

    original_stdin = sys.stdin
    sys.stdin = StringIO(value)

    try:
        yield
    finally:
        sys.stdin = original_stdin


def raise_exception(exception):
    """
    This function is used to raise exceptions in lambdas.
    """

    raise exception


@contextmanager
def temporary_directory(name = "".join(random.choices(string.ascii_lowercase, k = 64))):
    """
    Create and cd into a temporary directory.
    The aforementioned is removed when the context is exited.

    Args:
        name (str):
            The name of the temporary directory.
    """

    with ChangeDirectory("/tmp"):
        try:
            os.mkdir(name)

            with ChangeDirectory(name):
                yield
        finally:
            shutil.rmtree(name)
