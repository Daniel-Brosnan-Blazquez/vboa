var events = [
    {% for event in events %}
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
    },
    {% endfor %}
]
