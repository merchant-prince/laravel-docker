import os
from re import compile, match, IGNORECASE


def directory_does_not_exist(name):
    if name in os.listdir() and os.path.isdir(name):
        raise ValueError("Another directory with the same name already exists in the current directory.")


def is_alphabetic(value):
    if not value.isalpha():
        raise ValueError(f"The provided value is not alphabetic.")


def is_alphanumeric(value):
    if not value.isalnum():
        raise ValueError("The provided value is not alphanumeric.")


def is_digit(value):
    if not value.isdigit():
        raise ValueError("The provided value does not contain digits only.")


def is_lowercase(value):
    if value.lower() != value:
        raise ValueError(f"The provided value is not lowercase.")


def is_pascalcased(value):
    if match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', value) is None:
        raise ValueError("The provided value is not PascalCased")


def is_url(value):
    url_regex = compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$',
        IGNORECASE
    )

    if match(url_regex, f"http://{value}") is None:
        raise ValueError("The provided value is not a valid domain.")


def min_length(length):
    def minimum_length_validator(value):
        if len(value) < length:
            raise ValueError(f"The provided value should be longer than {length} characters.")

    return minimum_length_validator


def max_length(length):
    def maximum_length_validator(value):
        if len(value) > length:
            raise ValueError(f"The provided value should not be longer than {length} characters.")

    return maximum_length_validator
