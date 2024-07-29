var events = [
    {% for key in links %}
    {% for link in links[key] %}
    {% if key == "prime_events" %}
    {% set event = link %}
    {% set link_name = "" %}
    {% else %}
    {% set event = link["event"] %}
    {% set link_name = link["link_name"] %}
    {% endif %}
    {
        "id": "{{ event.event_uuid }}",
        "gauge":{
            "name": "{{ event.gauge.name }}",
            "system": "{{ event.gauge.system }}"
        },
        "explicit_reference": "{{ event.explicitRef.explicit_ref }}",
        "explicit_ref_uuid": "{{ event.explicitRef.explicit_ref_uuid }}",
        "ingestion_time": "{{ event.ingestion_time.isoformat() }}",
        "source": "{{ event.source.name }}",
        "source_uuid": "{{ event.source.source_uuid }}",
        "start": "{{ event.start.isoformat() }}",
        "stop": "{{ event.stop.isoformat() }}",
        "label": "{{ key }}",
        "link_name": "{{ link_name }}"
    },
    {% endfor %}
    {% endfor %}
]
