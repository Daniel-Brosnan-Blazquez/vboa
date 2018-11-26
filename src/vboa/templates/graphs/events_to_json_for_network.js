var events = {
    "events": [
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
            "start": "{{ event.start }}",
            "stop": "{{ event.stop }}",
            "label": "{{ key }}",
            "link_name": "{{ link_name }}",
            "source": "{{ event.source.name }}"
        },
        {% endfor %}
        {% endfor %}
    ]
}
