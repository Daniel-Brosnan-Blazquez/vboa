"""
Filters for date operations for data in json format

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import datetime
from dateutil import parser
import re

# Import operators
from vboa.filters.operators import mathematic_operators

def add_filters(app):
    """
    Method to add the filters associated to date operations for data in json format
    to the app
    """
    
    @app.template_filter()
    def date_op(date1, date2, op):

        result = None
        if op in mathematic_operators:
            operation = mathematic_operators[op]
            result = operation(parser.parse(date1), parser.parse(date2)).total_seconds()
        # end if

        return result

    @app.template_filter()
    def add_seconds_to_date(date, seconds):

        result = (parser.parse(date) + datetime.timedelta(seconds=seconds)).isoformat()

        return result
