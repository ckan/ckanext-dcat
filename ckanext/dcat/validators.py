import datetime
import json
import re

from dateutil.parser import parse as parse_date
from ckantoolkit import (
    missing,
    StopOnError,
    Invalid,
    _,
)

try:
    from ckanext.scheming.validation import scheming_validator
except ImportError:
    def scheming_validator(func):
        return func


# https://www.w3.org/TR/xmlschema11-2/#gYear
regexp_xsd_year = re.compile(
    "-?([1-9][0-9]{3,}|0[0-9]{3})(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?"
)

# https://www.w3.org/TR/xmlschema11-2/#gYearMonth
regexp_xsd_year_month = re.compile(
    "-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?"
)

regexp_xsd_date = re.compile(
    "-?([1-9][0-9]{3,}|0[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(Z|(\+|-)((0[0-9]|1[0-3]):[0-5][0-9]|14:00))?"
)


def is_year(value):
    return regexp_xsd_year.fullmatch(value)


def is_year_month(value):
    return regexp_xsd_year_month.fullmatch(value)


def is_date(value):
    return regexp_xsd_date.fullmatch(value)


def dcat_date(key, data, errors, context):
    value = data[key]

    if not value:
        data[key] = None
        return

    if isinstance(value, datetime.datetime):
        return

    try:
        if is_year(value) or is_year_month(value) or is_date(value):
            return
    except TypeError:
        raise Invalid(_("Dates must be provided as strings or datetime objects"))

    try:
        parse_date(value)
    except ValueError:
        raise Invalid(
            _(
                "Date format incorrect. Supported formats are YYYY, YYYY-MM, YYYY-MM-DD and YYYY-MM-DDTHH:MM:SS"
            )
        )

    return value


@scheming_validator
def scheming_multiple_number(field, schema):
    """
    Accept repeating numbers input in the following forms and convert to a
    json list of decimal values for storage. Also act like scheming_required
    to check for at least one non-empty string when required is true:

    1. a list of numbers, eg.

       [22, 1.3]

    2. a single number value to allow single text fields to be
       migrated to repeating numbers

       33.4

    """

    def _scheming_multiple_number(key, data, errors, context):
        # just in case there was an error before our validator,
        # bail out here because our errors won't be useful
        if errors[key]:
            return

        value = data[key]
        if value and value is not missing:

            if not isinstance(value, list):
                if isinstance(value, str) and value.startswith("["):
                    try:
                        value = json.loads(value)
                    except ValueError:
                        errors[key].append(_("Could not parse value"))
                        raise StopOnError
                else:
                    try:
                        value = [float(value)]
                    except ValueError:
                        errors[key].append(_("expecting list of numbers"))
                        raise StopOnError

            out = []
            for element in value:
                if not element:
                    continue
                try:
                    element = float(element)
                except ValueError:
                    errors[key].append(
                        _("invalid type for repeating number: %r") % element
                    )
                    continue

                out.append(element)

            if errors[key]:
                raise StopOnError

            data[key] = json.dumps(out)

        if (data[key] is missing or data[key] == "[]") and field.get("required"):
            errors[key].append(_("Missing value"))
            raise StopOnError

    return _scheming_multiple_number


dcat_validators = {
    "scheming_multiple_number": scheming_multiple_number,
    "dcat_date": dcat_date,
}
