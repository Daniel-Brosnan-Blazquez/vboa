"""
Automated tests for the filters in json

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import unittest
import traceback
import sys

# Import the VBOA functions module
from vboa.filters import filters_for_values_in_json
from vboa.filters import filters_for_events_in_json

class TestVboaFiltersInJson(unittest.TestCase):

    #############
    # Tests for filters for values
    #############
    def test_check_value_all_operators(self):
        """
        Method to test the function filters_for_values_in_json.check_value
        """
        # regex
        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": ".*am.*",
                "op": "regex"
            },
            "value": {
                "filter": "value",
                "op": "regex"
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == True

        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "different",
                "op": "regex"
            },
            "value": {
                "filter": "different",
                "op": "regex"
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == False

        # ==
        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == True

        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "different",
                "op": "=="
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == False

        # !=
        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "different",
                "op": "!="
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == True

        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "!="
            },
            "group": "group"
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == False

    def test_check_value_filter_only_name(self):
        """
        Method to test the function filters_for_values_in_json.check_value
        """
        # ==
        value = {
            "name": "name",
            "value": "value",
            "type": "text"
        }
        
        value_filter = {
            "name": {
                "filter": "name",
                "op": "=="
            }
        }
        
        check = filters_for_values_in_json.check_value(value, value_filter)

        assert check == True

    def test_search_values_duplicated(self):
        """
        Method to test the function filters_for_values_in_json.check_value
        """

        list_values = [{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name2",
            "value": "value2",
            "type": "text"
        }]
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group"
        }]
        
        found_values = filters_for_values_in_json.search_values(list_values, value_filters)

        assert found_values == {
            "group": [{
                "name": "name",
                "value": "value",
                "type": "text"
                }]
        }

    def test_search_values_duplicated_not_stop_first(self):
        """
        Method to test the function filters_for_values_in_json.check_value
        """

        list_values = [{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name2",
            "value": "value2",
            "type": "text"
        }]
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group"
        }]
        found_values = filters_for_values_in_json.search_values(list_values, value_filters, stop_first = False)

        assert found_values == {
            "group": [{
                "name": "name",
                "value": "value",
                "type": "text"
                },{
                "name": "name",
                "value": "value",
                "type": "text"
                }]
        }

    def test_search_values_duplicated_several_filters(self):
        """
        Method to test the function filters_for_values_in_json.check_value
        """

        list_values = [{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name",
            "value": "value",
            "type": "text"
        },{
            "name": "name2",
            "value": "value2",
            "type": "text"
        }]
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group1"
        },{
            "name": {
                "filter": "name.",
                "op": "regex"
            },
            "value": {
                "filter": "value2",
                "op": "=="
            },
            "group": "group2"
        }]
        
        found_values = filters_for_values_in_json.search_values(list_values, value_filters)

        assert found_values == {
            "group1": [{
                "name": "name",
                "value": "value",
                "type": "text"
                }],
            "group2": [{
                "name": "name2",
                "value": "value2",
                "type": "text"
                }]
        }

    def test_get_values_definition_duplicated_several_filters(self):
        """
        Method to test the function filters_for_values_in_json.get_values
        """

        event = {
            "event_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
            "start": "2018-01-01T04:00:00",
            "stop": "2018-01-01T05:00:00",
            "ingestion_time": "2020-01-01T05:00:00",
            "gauge": {"gauge_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                      "dim_signature": "dim_signature",
                      "name": "GAUGE_NAME",
                      "system": "GAUGE_SYSTEM",
                      "description": None},
            "source": {"source_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                       "name": "source1.xml"},
            "links_to_me": [],
            "alerts": [],
            "values" :[{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name2",
                "value": "value2",
                "type": "text"
            }]
        }
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group1"
        },{
            "name": {
                "filter": "name2",
                "op": "=="
            },
            "value": {
                "filter": "value2",
                "op": "=="
            },
            "group": "group2"
        }]
        
        found_values = filters_for_values_in_json.get_values_definition(event, value_filters)

        assert found_values == {
            "group1": [{
                "name": "name",
                "value": "value",
                "type": "text"
                }],
            "group2": [{
                "name": "name2",
                "value": "value2",
                "type": "text"
                }]
        }

    #############
    # Tests for filters for events
    #############
    def test_events_filtered_by_values_several_value_filters(self):

        events = [{
            "event_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
            "start": "2018-01-01T04:00:00",
            "stop": "2018-01-01T05:00:00",
            "ingestion_time": "2020-01-01T05:00:00",
            "gauge": {"gauge_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                      "dim_signature": "dim_signature",
                      "name": "GAUGE_NAME",
                      "system": "GAUGE_SYSTEM",
                      "description": None},
            "source": {"source_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                       "name": "source1.xml"},
            "links_to_me": [],
            "alerts": [],
            "values" :[{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name2",
                "value": "value2",
                "type": "text"
            }]
        }]
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            },
            "value": {
                "filter": "value",
                "op": "=="
            },
            "group": "group1"
        },{
            "name": {
                "filter": "name2",
                "op": "=="
            },
            "value": {
                "filter": "value2",
                "op": "=="
            },
            "group": "group2"
        }]
        
        filtered_events = filters_for_events_in_json.get_events_filtered_by_values_definition(events, value_filters)

        assert filtered_events == [
            {
                "event_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                "start": "2018-01-01T04:00:00",
                "stop": "2018-01-01T05:00:00",
                "ingestion_time": "2020-01-01T05:00:00",
                "gauge": {"gauge_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                          "dim_signature": "dim_signature",
                          "name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "description": None},
                "source": {"source_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                           "name": "source1.xml"},
                "links_to_me": [],
                "alerts": [],
                "values" :[{
                    "name": "name",
                    "value": "value",
                    "type": "text"
                },{
                    "name": "name",
                    "value": "value",
                    "type": "text"
                },{
                    "name": "name2",
                    "value": "value2",
                    "type": "text"
                }]
            }
        ]

    def test_events_filtered_by_values_only_name(self):

        events = [{
            "event_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
            "start": "2018-01-01T04:00:00",
            "stop": "2018-01-01T05:00:00",
            "ingestion_time": "2020-01-01T05:00:00",
            "gauge": {"gauge_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                      "dim_signature": "dim_signature",
                      "name": "GAUGE_NAME",
                      "system": "GAUGE_SYSTEM",
                      "description": None},
            "source": {"source_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                       "name": "source1.xml"},
            "links_to_me": [],
            "alerts": [],
            "values" :[{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name",
                "value": "value",
                "type": "text"
            },{
                "name": "name2",
                "value": "value2",
                "type": "text"
            }]
        }]
        
        value_filters = [{
            "name": {
                "filter": "name",
                "op": "=="
            }
        }]
        
        filtered_events = filters_for_events_in_json.get_events_filtered_by_values_definition(events, value_filters)

        assert filtered_events == [
            {
                "event_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                "start": "2018-01-01T04:00:00",
                "stop": "2018-01-01T05:00:00",
                "ingestion_time": "2020-01-01T05:00:00",
                "gauge": {"gauge_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                          "dim_signature": "dim_signature",
                          "name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "description": None},
                "source": {"source_uuid": "5f519d5e-a665-11eb-8c0f-000000000234",
                           "name": "source1.xml"},
                "links_to_me": [],
                "alerts": [],
                "values" :[{
                    "name": "name",
                    "value": "value",
                    "type": "text"
                },{
                    "name": "name",
                    "value": "value",
                    "type": "text"
                },{
                    "name": "name2",
                    "value": "value2",
                    "type": "text"
                }]
            }
        ]
