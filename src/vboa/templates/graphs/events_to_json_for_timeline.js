var events = [
    {% for event in events %}
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
    },
    {% endfor %}
]
