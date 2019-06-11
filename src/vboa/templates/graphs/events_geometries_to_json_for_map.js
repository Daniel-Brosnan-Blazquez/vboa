var events_geometries = {
    "events_geometries": [
        {% for event_geometry in events_geometries %}
        {
            "id": "{{ event_geometry['event'].event_uuid }}",
            "gauge":{
                "name": "{{ event_geometry['event'].gauge.name }}",
                "system": "{{ event_geometry['event'].gauge.system }}",
                "description": "{{ event_geometry['event'].gauge.description }}"
            },
            "explicit_reference": "{{ event_geometry['event'].explicitRef.explicit_ref }}",
            "ingestion_time": "{{ event_geometry['event'].ingestion_time }}",
            "source": "{{ event_geometry['event'].source.name }}",
            "geometries": [
                {% for geometry in event_geometry["geometries"] %}
                {
                    "value": "{{ geometry['value'] }}",
                    "name": "{{ geometry['name'] }}"
                }
                {% endfor %}
            ]
        },
        {% endfor %}
    ]
}
