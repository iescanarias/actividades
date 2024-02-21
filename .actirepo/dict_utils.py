# This file contains utility functions for working with dictionaries

# Trim keys from a list of dictionaries
def trim_all_keys(dict, keys):
    return [ trim_keys(x, keys) for x in dict ]

# Trim keys from a dictionary
def trim_keys(dict, keys):
    return {k: dict[k] for k in keys}