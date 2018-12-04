"""
Automated tests for the eboa_nav submodule

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import python utilities
import pytest
import json

from vboa.eboa_nav import eboa_nav

def test_initial_panel(client):

    response = client.get('/')
    assert response.status_code == 200

def test_initial_eboa_nav(client):

    response = client.get('/eboa_nav', follow_redirects=True)
    assert response.status_code == 200

def test_query_events_and_render(client):

    response = client.get('/eboa_nav/query-events')
    assert response.status_code == 200

    response = client.post('/eboa_nav/query-events', data={
        "source_like": "",
        "er_like": "",
        "gauge_name_like": "",
        "gauge_system_like": "",
        "start": "",
        "start_operator": "",
        "stop": "",
        "stop_operator": "",
        "ingestion_time": "",
        "ingestion_time_operator": "",
    })
    assert response.status_code == 200

def test_query_events(app, client):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "key": "EVENT_KEY"
            }]
    }]
    }
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    with app.test_request_context(
            '/eboa_nav/query-events', data={
                "source_like": "source.json",
                "er_like": "EXPLICIT_REFERENCE_EVENT",
                "gauge_name_like": "GAUGE_NAME",
                "gauge_system_like": "GAUGE_SYSTEM",
                "start": ["2018-06-05T02:07:03"],
                "start_operator": ["=="],
                "stop": ["2018-06-05T08:07:36"],
                "stop_operator": ["=="],
                "ingestion_time": ["1900-06-05T02:07:36"],
                "ingestion_time_operator": [">"],
            }):
        events = eboa_nav.query_events()

    assert len(events) == 1

def test_query_event_links_and_render(client, app):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                          "exec": "exec",
                          "version": "1.0"},
        "source": {"name": "source.xml",
                   "generation_time": "2018-07-05T02:07:03",
                   "validity_start": "2018-06-05T02:07:03",
                   "validity_stop": "2018-06-05T08:07:36"},
        "events": [{
            "link_ref": "EVENT_LINK1",
            "gauge": {"name": "GAUGE_NAME",
                      "system": "GAUGE_SYSTEM",
                      "insertion_type": "SIMPLE_UPDATE"},
            "start": "2018-06-05T02:07:03",
            "stop": "2018-06-05T08:07:36",
            "links": [{
                "link": "EVENT_LINK2",
                "link_mode": "by_ref",
                "name": "EVENT_LINK_NAME"
            }]
            },
            {
                "link_ref": "EVENT_LINK2",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "links": [{
                    "link": "EVENT_LINK1",
                    "link_mode": "by_ref",
                    "name": "EVENT_LINK_NAME"
                }]
            }]
        }]}
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    with app.test_request_context(
            '/eboa_nav/query-events', data={
                "source_like": "",
                "er_like": "",
                "gauge_name_like": "",
                "gauge_system_like": "",
                "start": "",
                "start_operator": "",
                "stop": "",
                "stop_operator": "",
                "ingestion_time": "",
                "ingestion_time_operator": "",
            }):
        events = eboa_nav.query_events()

    uuid1 = events[0].event_uuid

    response = client.get('/eboa_nav/query-event-links/' + str(uuid1))
    assert response.status_code == 200
    
def test_query_event_links(app, client):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                          "exec": "exec",
                          "version": "1.0"},
        "source": {"name": "source.xml",
                   "generation_time": "2018-07-05T02:07:03",
                   "validity_start": "2018-06-05T02:07:03",
                   "validity_stop": "2018-06-05T08:07:36"},
        "events": [{
            "link_ref": "EVENT_LINK1",
            "gauge": {"name": "GAUGE_NAME",
                      "system": "GAUGE_SYSTEM",
                      "insertion_type": "SIMPLE_UPDATE"},
            "start": "2018-06-05T02:07:03",
            "stop": "2018-06-05T08:07:36",
            "links": [{
                "link": "EVENT_LINK2",
                "link_mode": "by_ref",
                "name": "EVENT_LINK_NAME"
            }]
            },
            {
                "link_ref": "EVENT_LINK2",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "SIMPLE_UPDATE"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "links": [{
                    "link": "EVENT_LINK1",
                    "link_mode": "by_ref",
                    "name": "EVENT_LINK_NAME"
                }]
            }]
        }]}
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    with app.test_request_context(
            '/eboa_nav/query-events', data={
                "source_like": "",
                "er_like": "",
                "gauge_name_like": "",
                "gauge_system_like": "",
                "start": "",
                "start_operator": "",
                "stop": "",
                "stop_operator": "",
                "ingestion_time": "",
                "ingestion_time_operator": "",
            }):
        events = eboa_nav.query_events()

    uuid1 = events[0].event_uuid

    with app.test_request_context(
            '/eboa_nav/query-event', data={
                "source_like": "",
                "er_like": "",
                "gauge_name_like": "",
                "gauge_system_like": "",
                "start": "",
                "start_operator": "",
                "stop": "",
                "stop_operator": "",
                "ingestion_time": "",
                "ingestion_time_operator": "",
            }):
        links = eboa_nav.query_event_links(uuid1)

    assert response.status_code == 200
    assert len(links) == 3

def test_query_source_and_render(client):

    response = client.get('/eboa_nav/query-sources')
    assert response.status_code == 200

    response = client.post('/eboa_nav/query-sources', data={
        "source_like": "",
        "dim_signature_like": "",
        "validity_start": "",
        "validity_start_operator": "",
        "validity_stop": "",
        "validity_stop_operator": "",
        "ingestion_time": "",
        "ingestion_time_operator": "",
        "generation_time": "",
        "generation_time_operator": "",
    })
    assert response.status_code == 200

def test_query_sources(app, client):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "key": "EVENT_KEY"
            }]
    }]
    }
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    with app.test_request_context(
            '/eboa_nav/query-events', data={
                "source_like": "source.json",
                "dim_signature_like": "dim_signature",
                "validity_start": ["2018-06-05T02:07:03"],
                "validity_start_operator": ["=="],
                "validity_stop": ["2018-06-05T08:07:36"],
                "validity_stop_operator": ["=="],
                "ingestion_time": ["1900-06-05T02:07:36"],
                "ingestion_time_operator": [">"],
                "generation_time": ["2018-07-05T02:07:03"],
                "generation_time_operator": ["=="],
            }):
        sources = eboa_nav.query_sources()

    assert len(sources) == 1
   
def test_query_source(app, client):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "key": "EVENT_KEY"
            }]
    }]
    }
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    with app.test_request_context(
            '/eboa_nav/query-events', data={
                "source_like": "",
                "er_like": "",
                "gauge_name_like": "",
                "gauge_system_like": "",
                "start": "",
                "start_operator": "",
                "stop": "",
                "stop_operator": "",
                "ingestion_time": "",
                "ingestion_time_operator": "",
            }):
        events = eboa_nav.query_events()

    source_uuid = events[0].source.processing_uuid

    response = client.get('/eboa_nav/query-source/' + str(source_uuid))
    assert response.status_code == 200
 
def test_query_gauges(app, client):

    data = {"operations": [{
        "mode": "insert",
        "dim_signature": {"name": "dim_signature",
                              "exec": "exec",
                              "version": "1.0"},
            "source": {"name": "source.json",
                       "generation_time": "2018-07-05T02:07:03",
                       "validity_start": "2018-06-05T02:07:03",
                       "validity_stop": "2018-06-05T08:07:36"},
            "events": [{
                "explicit_reference": "EXPLICIT_REFERENCE_EVENT",
                "gauge": {"name": "GAUGE_NAME",
                          "system": "GAUGE_SYSTEM",
                          "insertion_type": "EVENT_KEYS"},
                "start": "2018-06-05T02:07:03",
                "stop": "2018-06-05T08:07:36",
                "key": "EVENT_KEY"
            }]
    }]
    }
    response = client.post('/eboa_nav/treat-data', json=data)
    exit_information = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert int(exit_information["exit_status"]) == 0

    response = client.get('/eboa_nav/query-jsonify-gauges')
    gauges = json.loads(response.get_data().decode('utf8').replace("'", '"'))
    assert response.status_code == 200
    assert len(gauges) == 1

    
