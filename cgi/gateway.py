#!/usr/local/bin/python
"""Whitelisted access to functions via POST/GET...

Experimental!

REQUIRED FIELDS

function_name
args_string
args_file

http://127.0.0.1:8080/cgi/test.py?first_name=ZARA&last_name=ALI

"""


import cgi
import cgitb; cgitb.enable()


def upper(s):
    """must return mimetype, return_value."""
    return (
            'Content-type:text/plain\n\n',
            s.upper()
           )


def incorrect_parameter():
    pass

# CONSTANTS: configure the whitelist of functions accessible through the
# gateway.

whitelist = {
             'upper': upper
            }

# collect information to evaluate a function and return the results
form = cgi.FieldStorage()
kwargs = {key: form.getvalue(key) for key in form.keys()}

# interpret evaluate the function with the kwargs
function_name = kwargs.pop('function_name')
mime_type, return_value = whitelist[function_name](**kwargs)  # should return mimetype
print mime_type + return_value  # the response

# if unexpected arg print proper error response!

