from unittest import TestCase
import laravel_docker.helpers.validation as validators


class TestValidators(TestCase):


    def test_an_alphabetic_value_is_accepted(self):
        value = "thisisAlphabetic"
        validators.is_alphabetic(value)


    def test_a_non_alphabetic_value_is_not_accepted(self):
        value = "non44alpha00Betic55"
        self.assertRaises(ValueError, validators.is_alphabetic, value)


    def test_an_alphanumeric_value_is_accepted(self):
        value = "thisisalphaNumeric001"
        validators.is_alphanumeric(value)


    def test_a_non_alphanumeric_value_is_not_accepted(self):
        value = "this is not alphanumeric 4554"
        self.assertRaises(ValueError, validators.is_alphanumeric, value)


    def test_a_string_consisting_of_digits_only_is_accepted(self):
        value = "1234566"
        validators.is_digit(value)


    def test_a_string_not_consisting_of_digits_only_is_not_accepted(self):
        value = "3550a"
        self.assertRaises(ValueError, validators.is_digit, value)


    def test_a_string_consisting_of_lowercase_characters_only_is_accepted(self):
        value = "thisislowercase"
        validators.is_lowercase(value)


    def test_a_string_consisting_of_mixed_case_characters_is_not_accepted(self):
        value = "ThisIsMixedCase"
        self.assertRaises(ValueError, validators.is_lowercase, value)


    def test_a_string_longer_than_the_minimum_length_specified_is_accepted(self):
        length = 10
        value = "z" * (length + 1)
        validator = validators.min_length(length)
        validator(value)


    def test_a_string_shorter_than_the_minimum_length_specified_is_not_accepted(self):
        length = 10
        value = "a" * (length - 1)
        self.assertRaises(ValueError, validators.min_length(length), value)


    def test_a_string_shorter_than_the_maximum_length_specified_is_accepted(self):
        length = 10
        value = "z" * (length - 1)
        validator = validators.max_length(length)
        validator(value)


    def test_a_string_longer_than_the_maximum_length_specified_is_not_accepted(self):
        length = 10
        value = "a" * (length + 1)
        self.assertRaises(ValueError, validators.max_length(length), value)
