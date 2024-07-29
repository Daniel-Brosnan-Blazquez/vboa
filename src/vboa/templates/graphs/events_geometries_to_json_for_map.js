var events_geometries = [
    {% for event_geometry in events_geometries %}
    {
        "id": "{{ event_geometry['event'].event_uuid }}",
        "gauge":{
            "name": "{{ event_geometry['event'].gauge.name }}",
            "system": "{{ event_geometry['event'].gauge.system }}"
        },
        "explicit_reference": "{{ event_geometry['event'].explicitRef.explicit_ref }}",
        "explicit_ref_uuid": "{{ event_geometry['event'].explicitRef.explicit_ref_uuid }}",
        "ingestion_time": "{{ event_geometry['event'].ingestion_time.isoformat() }}",
        "source": "{{ event_geometry['event'].source.name }}",
        "source_uuid": "{{ event_geometry['event'].source.source_uuid }}",
        "start": "{{ event_geometry['event'].start.isoformat() }}",
        "stop": "{{ event_geometry['event'].stop.isoformat() }}",
        "geometries": [
            {% for geometry in event_geometry["geometries"] %}
            {
                "value": "{{ geometry['value'] }}",
                "name": "{{ geometry['name'] }}"
            },
            {% endfor %}
        ]
    },
    {% endfor %}
]
