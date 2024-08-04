import re
import logging
log = logging.getLogger(__name__)

def validate_overwrite_param(overwrite_values_str):
    # Convert key-value unicode str to dictionary using map() + split() + loop
    overwrite_list = []
    for sub in overwrite_values_str.split(','):
        if ':' in sub:

            # Python3 compatibility changes applied from original code
            overwrite_list.append(list(map(str.strip, sub.split(':', 1))))
            # overwrite_list.append(map(unicode.strip, sub.split(':', 1)))

    overwrite_dict = dict(overwrite_list)
    return overwrite_dict
