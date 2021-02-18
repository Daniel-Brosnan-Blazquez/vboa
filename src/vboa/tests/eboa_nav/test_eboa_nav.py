"""
Automated tests for the eboa_nav submodule

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import unittest
import os
import shutil
import pdb

from vboa.views.eboa_nav import eboa_nav

# Import app
from vboa import create_app

# Import engine of the DDBB
import eboa.engine.engine as eboa_engine
from eboa.engine.engine import Engine
from eboa.engine.query import Query
from eboa.datamodel.base import Session, engine, Base

class TestEboaNav(unittest.TestCase):

    def setUp(self):
        # Create the engine to manage the data
        self.engine_eboa = Engine()
        self.query_eboa = Query()

        # Create session to connect to the database
        self.session = Session()

        # Clear all tables before executing the test
        self.query_eboa.clear_db()

        # Create app
        self.app = create_app()

        # Create client
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            os.rename("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")
        except FileNotFoundError:
            pass
        # end try
        # Close connections to the DDBB
        self.engine_eboa.close_session()
        self.query_eboa.close_session()
        self.session.close()

    def test_initial_panel(self):

        response = self.client.get('/eboa_nav/')
        assert response.status_code == 200

    def test_prepare_reingestion_of_sources_and_dependencies_no_data(self):

        sources = []
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []
        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 0

        assert len(source_uuids_matching_triggering_rule) == 0

        assert len(source_uuids_not_matching_triggering_rule) == 0

    def test_prepare_reingestion_of_sources_and_dependencies_one_source_no_matching_triggering_rules(self):

        # Insert data
        data = {"operations":[{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "source.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        sources = self.query_eboa.get_sources()
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []
        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 1

        assert len(source_uuids_matching_triggering_rule) == 0

        assert len(source_uuids_not_matching_triggering_rule) == 1

    def test_prepare_reingestion_of_sources_and_dependencies_one_source_matching_triggering_rules(self):

        # Move test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")

        # Insert data
        data = {"operations":[{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_1.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        sources = self.query_eboa.get_sources()
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []
        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 1

        assert len(source_uuids_matching_triggering_rule) == 1

        assert len(source_uuids_not_matching_triggering_rule) == 0

        shutil.copyfile("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")

    def test_prepare_reingestion_of_sources_and_dependencies_one_source_matching_triggering_rules_skip(self):

        # Move test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")

        # Insert data
        data = {"operations":[{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_SKIP_1.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        sources = self.query_eboa.get_sources()
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []
        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 1

        assert len(source_uuids_matching_triggering_rule) == 0

        assert len(source_uuids_not_matching_triggering_rule) == 1

        shutil.copyfile("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")

    def test_prepare_reingestion_of_sources_and_dependencies_three_source_uuids_matching_triggering_rules_one_to_be_reingest_one_linked_to_it(self):

        # Move test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")

        # Insert data
        data = {"operations":[{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_1.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                           },
            "events": [{
                "link_ref": "EVENT_1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
            }]
        },
                              {
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_2.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                           },
            "events": [{
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "links": [{
                    "link": "EVENT_1",
                    "link_mode": "by_ref",
                    "name": "LINK_NAME"
                }]
            }]
                              },{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_3.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        sources = self.query_eboa.get_sources(names = {"filter": "FILE_TO_PROCESS_1.xml", "op": "=="})
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []
        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 1

        assert len(source_uuids_matching_triggering_rule) == 2

        assert len(source_uuids_not_matching_triggering_rule) == 0

        shutil.copyfile("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")

    def test_prepare_reingestion_of_sources_circular_links(self):

        # Move test configuration for triggering
        os.rename("/resources_path/triggering.xml", "/resources_path/triggering_bak.xml")
        shutil.copyfile(os.path.dirname(os.path.abspath(__file__)) + "/inputs/triggering.xml", "/resources_path/triggering.xml")

        # Insert data
        data = {"operations":[{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_4.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                           },
            "events": [{
                "link_ref": "EVENT_1",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36"
            }]
        },
                              {
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_5.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                           },
            "events": [{
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T04:07:03",
                "stop": "2018-06-05T06:07:36",
                "links": [{
                    "link": "EVENT_1",
                    "link_mode": "by_ref",
                    "name": "LINK_NAME",
                    "back_ref": "BACK_REF_LINK_NAME"
                }]
            }]
                              },{
                "mode": "insert",
                "dim_signature": {"name": "dim_signature",
                                    "exec": "exec",
                                    "version": "1.0"},
                "source": {"name": "FILE_TO_PROCESS_3.xml",
                            "reception_time": "2018-07-05T02:07:03",
                            "generation_time": "2018-07-05T02:07:03",
                            "validity_start": "2018-06-05T02:07:03",
                            "validity_stop": "2018-06-05T08:07:36",
                            "priority": 10
                }
        }]}

        # Check data is correctly inserted
        exit_status = self.engine_eboa.treat_data(data)
        assert len([item for item in exit_status if item["status"] != eboa_engine.exit_codes["OK"]["status"]]) == 0
        
        sources = self.query_eboa.get_sources(names = {"filter": "FILE_TO_PROCESS_4.xml", "op": "=="})
        source_uuids_matching_triggering_rule = []
        source_uuids_not_matching_triggering_rule = []

        eboa_nav.prepare_reingestion_of_sources_and_dependencies(sources, source_uuids_matching_triggering_rule, source_uuids_not_matching_triggering_rule)

        assert len(sources) == 1

        assert len(source_uuids_matching_triggering_rule) == 2

        assert len(source_uuids_not_matching_triggering_rule) == 0

        shutil.copyfile("/resources_path/triggering_bak.xml", "/resources_path/triggering.xml")

        
# def test_query_events_and_render(client):

#     response = client.get('/eboa_nav/query-events')
#     assert response.status_code == 200

#     response = client.post('/eboa_nav/query-events', data={
#         "source_like": "",
#         "er_like": "",
#         "gauge_name_like": "",
#         "gauge_system_like": "",
#         "start": "",
#         "start_operator": "",
#         "stop": "",
#         "stop_operator": "",
#         "ingestion_time": "",
#         "ingestion_time_operator": "",
#         "key_like": "",
#         "keys": ""
#     })
#     assert response.status_code == 200

# def test_query_events(app, client):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                               "exec": "exec",
#                               "version": "1.0"},
#             "source": {"name": "source.json",
#                        "generation_time": "2018-07-05T02:07:03",
#                        "validity_start": "2018-06-05T02:07:03",
#                        "validity_stop": "2018-06-05T08:07:36"},
#             "events": [{
#                 "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "EVENT_KEYS"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "key": "EVENT_KEY"
#             }]
#     }]
#     }
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     with app.test_request_context(
#             '/eboa_nav/query-events', data={
#                 "source_like": "source.json",
#                 "er_like": "EXPLICIT_REFERENCE_EVENT",
#                 "gauge_name_like": "GAUGE_NAME",
#                 "gauge_system_like": "GAUGE_SYSTEM",
#                 "start": ["2018-06-05T02:07:03"],
#                 "start_operator": ["=="],
#                 "stop": ["2018-06-05T08:07:36"],
#                 "stop_operator": ["=="],
#                 "ingestion_time": ["1900-06-05T02:07:36"],
#                 "ingestion_time_operator": [">"],
#                 "key_like": "EVENT_KEY",
#                 "keys": ["EVENT_KEY"]
#             }):
#         events = eboa_nav.query_events()

#     assert len(events) == 1

# def test_query_event_links_and_render(client, app):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                           "exec": "exec",
#                           "version": "1.0"},
#         "source": {"name": "source.xml",
#                    "generation_time": "2018-07-05T02:07:03",
#                    "validity_start": "2018-06-05T02:07:03",
#                    "validity_stop": "2018-06-05T08:07:36"},
#         "events": [{
#             "link_ref": "EVENT_LINK1",
#             "gauge": {"name": "GAUGE_NAME",
#                       "system": "GAUGE_SYSTEM",
#                       "insertion_type": "SIMPLE_UPDATE"},
#             "start": "2018-06-05T02:07:03",
#             "stop": "2018-06-05T08:07:36",
#             "links": [{
#                 "link": "EVENT_LINK2",
#                 "link_mode": "by_ref",
#                 "name": "EVENT_LINK_NAME"
#             }]
#             },
#             {
#                 "link_ref": "EVENT_LINK2",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "SIMPLE_UPDATE"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "links": [{
#                     "link": "EVENT_LINK1",
#                     "link_mode": "by_ref",
#                     "name": "EVENT_LINK_NAME"
#                 }]
#             }]
#         }]}
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     with app.test_request_context(
#             '/eboa_nav/query-events', data={
#                 "source_like": "",
#                 "er_like": "",
#                 "gauge_name_like": "",
#                 "gauge_system_like": "",
#                 "start": "",
#                 "start_operator": "",
#                 "stop": "",
#                 "stop_operator": "",
#                 "ingestion_time": "",
#                 "ingestion_time_operator": "",
#                 "key_like": "",
#                 "keys": ""
#             }):
#         events = eboa_nav.query_events()

#     uuid1 = events[0].event_uuid

#     response = client.get('/eboa_nav/query-event-links/' + str(uuid1))
#     assert response.status_code == 200
    
# def test_query_event_links(app, client):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                           "exec": "exec",
#                           "version": "1.0"},
#         "source": {"name": "source.xml",
#                    "generation_time": "2018-07-05T02:07:03",
#                    "validity_start": "2018-06-05T02:07:03",
#                    "validity_stop": "2018-06-05T08:07:36"},
#         "events": [{
#             "link_ref": "EVENT_LINK1",
#             "gauge": {"name": "GAUGE_NAME",
#                       "system": "GAUGE_SYSTEM",
#                       "insertion_type": "SIMPLE_UPDATE"},
#             "start": "2018-06-05T02:07:03",
#             "stop": "2018-06-05T08:07:36",
#             "links": [{
#                 "link": "EVENT_LINK2",
#                 "link_mode": "by_ref",
#                 "name": "EVENT_LINK_NAME"
#             }]
#             },
#             {
#                 "link_ref": "EVENT_LINK2",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "SIMPLE_UPDATE"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "links": [{
#                     "link": "EVENT_LINK1",
#                     "link_mode": "by_ref",
#                     "name": "EVENT_LINK_NAME"
#                 }]
#             }]
#         }]}
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     with app.test_request_context(
#             '/eboa_nav/query-events', data={
#                 "source_like": "",
#                 "er_like": "",
#                 "gauge_name_like": "",
#                 "gauge_system_like": "",
#                 "start": "",
#                 "start_operator": "",
#                 "stop": "",
#                 "stop_operator": "",
#                 "ingestion_time": "",
#                 "ingestion_time_operator": "",
#                 "key_like": "",
#                 "keys": ""
#             }):
#         events = eboa_nav.query_events()

#     uuid1 = events[0].event_uuid

#     with app.test_request_context(
#             '/eboa_nav/query-event', data={
#                 "source_like": "",
#                 "er_like": "",
#                 "gauge_name_like": "",
#                 "gauge_system_like": "",
#                 "start": "",
#                 "start_operator": "",
#                 "stop": "",
#                 "stop_operator": "",
#                 "ingestion_time": "",
#                 "ingestion_time_operator": "",
#                 "key_like": "",
#                 "keys": ""
#             }):
#         links = eboa_nav.query_event_links(uuid1)

#     assert response.status_code == 200
#     assert len(links) == 3

# def test_query_source_and_render(client):

#     response = client.get('/eboa_nav/query-sources')
#     assert response.status_code == 200

#     response = client.post('/eboa_nav/query-sources', data={
#         "source_like": "",
#         "processor_like": "",
#         "dim_signature_like": "",
#         "validity_start": "",
#         "validity_start_operator": "",
#         "validity_stop": "",
#         "validity_stop_operator": "",
#         "ingestion_time": "",
#         "ingestion_time_operator": "",
#         "ingestion_duration": "",
#         "ingestion_duration_operator": "",
#         "generation_time": "",
#         "generation_time_operator": "",
#     })
#     assert response.status_code == 200

# def test_query_sources(app, client):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                               "exec": "exec",
#                               "version": "1.0"},
#             "source": {"name": "source.json",
#                        "generation_time": "2018-07-05T02:07:03",
#                        "validity_start": "2018-06-05T02:07:03",
#                        "validity_stop": "2018-06-05T08:07:36"},
#             "events": [{
#                 "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "EVENT_KEYS"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "key": "EVENT_KEY"
#             }]
#     }]
#     }
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     with app.test_request_context(
#             '/eboa_nav/query-sources', data={
#                 "source_like": "source.json",
#                 "processor_like": "exec",
#                 "dim_signature_like": "dim_signature",
#                 "validity_start": ["2018-06-05T02:07:03"],
#                 "validity_start_operator": ["=="],
#                 "validity_stop": ["2018-06-05T08:07:36"],
#                 "validity_stop_operator": ["=="],
#                 "ingestion_time": ["1900-06-05T02:07:36"],
#                 "ingestion_time_operator": [">"],
#                 "ingestion_duration": [0],
#                 "ingestion_duration_operator": [">"],
#                 "generation_time": ["2018-07-05T02:07:03"],
#                 "generation_time_operator": ["=="],
#             }):
#         sources = eboa_nav.query_sources()

#     assert len(sources) == 1
   
# def test_query_source(app, client):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                               "exec": "exec",
#                               "version": "1.0"},
#             "source": {"name": "source.json",
#                        "generation_time": "2018-07-05T02:07:03",
#                        "validity_start": "2018-06-05T02:07:03",
#                        "validity_stop": "2018-06-05T08:07:36"},
#             "events": [{
#                 "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "EVENT_KEYS"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "key": "EVENT_KEY"
#             }]
#     }]
#     }
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     with app.test_request_context(
#             '/eboa_nav/query-events', data={
#                 "source_like": "",
#                 "er_like": "",
#                 "gauge_name_like": "",
#                 "gauge_system_like": "",
#                 "start": "",
#                 "start_operator": "",
#                 "stop": "",
#                 "stop_operator": "",
#                 "ingestion_time": "",
#                 "ingestion_time_operator": "",
#                 "key_like": "",
#                 "keys": ""
#             }):
#         events = eboa_nav.query_events()

#     source_uuid = events[0].source.source_uuid

#     response = client.get('/eboa_nav/query-source/' + str(source_uuid))
#     assert response.status_code == 200
 
# def test_query_gauges(app, client):

#     data = {"operations": [{
#         "mode": "insert",
#         "dim_signature": {"name": "dim_signature",
#                               "exec": "exec",
#                               "version": "1.0"},
#             "source": {"name": "source.json",
#                        "generation_time": "2018-07-05T02:07:03",
#                        "validity_start": "2018-06-05T02:07:03",
#                        "validity_stop": "2018-06-05T08:07:36"},
#             "events": [{
#                 "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
#                 "gauge": {"name": "GAUGE_NAME",
#                           "system": "GAUGE_SYSTEM",
#                           "insertion_type": "EVENT_KEYS"},
#                 "start": "2018-06-05T02:07:03",
#                 "stop": "2018-06-05T08:07:36",
#                 "key": "EVENT_KEY"
#             }]
#     }]
#     }
#     response = client.post('/eboa_nav/treat-data', json=data)
#     exit_information = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert int(exit_information["returned_values"][0]["status"]) == 0

#     response = client.get('/eboa_nav/query-jsonify-gauges')
#     gauges = json.loads(response.get_data().decode('utf8'))
#     assert response.status_code == 200
#     assert len(gauges) == 1

    
