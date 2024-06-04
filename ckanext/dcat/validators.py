import numbers
import json

from ckantoolkit import (
    missing,
    StopOnError,
    _,
)
from ckanext.scheming.validation import scheming_validator


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
        # 1. list of strings or 2. single string
        if value is not missing:
            if not isinstance(value, list):
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
}
