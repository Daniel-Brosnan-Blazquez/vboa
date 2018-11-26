var events = {
    "events": [
        {% for event in events %}
        {
            "id": "{{ event.event_uuid }}",
            "gauge":{
                "name": "{{ event.gauge.name }}",
                "system": "{{ event.gauge.system }}"
            },
            "start": "{{ event.start }}",
            "stop": "{{ event.stop }}",
            "source": "{{ event.source.name }}"
        },
        {% endfor %}
    ]
}
