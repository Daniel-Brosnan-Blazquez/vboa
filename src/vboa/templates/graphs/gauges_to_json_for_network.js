var gauges = {
    "gauges": [
        {% for gauge in links %}
        {
            "id": "{{ gauge['gauge_uuid'] }}",
            "name": "{{ gauge['name'] }}",
            "system": "{{ gauge['system'] }}",
            "dim_signature_uuid": "{{ gauge['dim_signature_uuid'] }}",
            "gauges_linking": {{ gauge['gauges_linking'] }}
        },
        {% endfor %}
    ]
}
