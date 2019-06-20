
var events = [
    {% for event in events %}
    {% set number_of_connections_to_ddbb = event.eventDoubles|selectattr("name", "equalto", "number_of_parallel_connections_to_ddbb")|first|attr("value") %}
    {
        "id": "{{ event.event_uuid }}-{{ event.start.isoformat() }}",
        "group": "# Connections to DDBB in parallel",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ number_of_connections_to_ddbb }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td># Connections to DDBB in parallel</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ number_of_connections_to_ddbb }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {% endfor %}
]
