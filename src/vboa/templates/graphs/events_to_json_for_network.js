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
        "ingestion_time": "{{ event.ingestion_time }}",
        "source": "{{ event.source.name }}",
        "start": "{{ event.start }}",
        "stop": "{{ event.stop }}",
        "label": "{{ key }}",
        "link_name": "{{ link_name }}"
    },
    {% endfor %}
    {% endfor %}
]
