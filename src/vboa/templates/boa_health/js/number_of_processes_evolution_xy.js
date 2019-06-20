
var events = [
    {% for event in events %}
    {% set number_of_processes_in_parallel = event.eventObjects|selectattr("name", "match", "information_for_process_.*")|list|length %}
    {
        "id": "{{ event.event_uuid }}-{{ event.start.isoformat() }}",
        "group": "# Processes in parallel",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ number_of_processes_in_parallel }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td># Processes in parallel</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ number_of_processes_in_parallel }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {% endfor %}
]
