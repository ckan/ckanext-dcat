import datetime
import json

import pytest

from ckantoolkit import StopOnError, Invalid
from ckanext.dcat.validators import scheming_multiple_number, dcat_date


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


def test_dcat_date_valid():

    key = ("some_date",)
    errors = {key: []}
    valid_values = [
        datetime.datetime.now(),
        "2024",
        "2024-07",
        "2024-07-01",
        "1905-03-01T10:07:31.182680",
        "2024-04-10T10:07:31",
        "2024-04-10T10:07:31.000Z",
    ]

    for value in valid_values:
        data = {key: value}
        dcat_date(key, data, errors, {}), value


def test_dcat_date_invalid():

    key = ("some_date",)
    errors = {key: []}
    invalid_values = [
        "2024+07",
        "not_a_date",
        True
    ]

    for value in invalid_values:
        data = {key: value}
        with pytest.raises(Invalid):
            dcat_date(key, data, errors, {}), value


def test_dcat_date_empty_values():

    key = ("some_date",)
    errors = {key: []}
    valid_values = [
        None,
        False,
        ""
    ]

    for value in valid_values:
        data = {key: value}
        dcat_date(key, data, errors, {}), value

        assert data[key] is None
