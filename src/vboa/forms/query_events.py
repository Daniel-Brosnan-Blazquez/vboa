"""
Form definition for query events

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
from wtforms import Form, DateTimeField, validators

class QueryEvents(Form):
    """
    Class for managing the form for querying events
    """

    # Period
    start = DateTimeField()
    stop = DateTimeField()
