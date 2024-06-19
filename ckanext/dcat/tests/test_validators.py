import json
import pytest

from ckantoolkit import StopOnError
from ckanext.dcat.validators import scheming_multiple_number


def test_scheming_multiple_number():

    expected_value = [1.5, 2.0, 0.345]

    key = ("some_number_field",)
    errors = {key: []}

    values = [
        expected_value,
        [1.5, 2, 0.345],
        ["1.5", "2", ".345"],
    ]
    for value in values:
        data = {key: value}
        scheming_multiple_number({}, {})(key, data, errors, {})

        assert data[key] == json.dumps(expected_value)


def test_scheming_multiple_number_single_value():

    expected_value = [1.5]

    key = ("some_number_field",)
    errors = {key: []}

    values = [
        expected_value,
        1.5,
        "1.5",
    ]
    for value in values:
        data = {key: value}
        scheming_multiple_number({}, {})(key, data, errors, {})

        assert data[key] == json.dumps(expected_value)


def test_scheming_multiple_number_wrong_value():

    key = ("some_number_field",)
    errors = {key: []}

    values = [
        ["a", 2, 0.345],
        ["1..5", "2", ".345"],
    ]
    for value in values:
        with pytest.raises(StopOnError):
            data = {key: value}
            scheming_multiple_number({}, {})(key, data, errors, {})

        assert errors[key][0].startswith("invalid type for repeating number")

        errors = {key: []}
